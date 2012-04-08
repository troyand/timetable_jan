#-*- coding: utf-8 -*-

import csv
import codecs
from optparse import OptionParser
import logging


logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;m:%(message)s', level=logging.INFO)

from django.core.management import setup_environ
from timetable_jan import settings

setup_environ(settings)
from timetable_jan.university.models import *


def load_table(filename):
    def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
        # csv.py doesn't do Unicode; encode temporarily as UTF-8:
        csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                                dialect=dialect, **kwargs)
        for row in csv_reader:
            # decode UTF-8 back to Unicode, cell by cell:
            yield [unicode(cell, 'utf-8') for cell in row]

    def utf_8_encoder(unicode_csv_data):
        for line in unicode_csv_data:
            yield line.encode('utf-8')

    reader = unicode_csv_reader(codecs.open(filename, 'r', 'utf-8'))
    return list(reader)


def analyze_table(table):
    rooms = set([row[2] for row in table])
    logging.info('Rooms in timetable:\n%s' % '\n'.join(sorted(rooms)))
    disciplines = set([row[3] for row in table])
    logging.info('Disciplines in timetable:\n%s' % '\n'.join(sorted(disciplines)))
    lecturers = set([row[5] for row in table])
    logging.info('Lecturers in timetable:\n%s' % '\n'.join(sorted(lecturers)))
    return rooms, disciplines, lecturers


def create_room_mapping(rooms, university):
    mapping = {}
    for room_str in rooms:
        building_number, room_name = room_str.split('-')
        room_number = filter(lambda x: x.isdigit(), room_name)
        room_label = filter(lambda x: not x.isdigit(), room_name) or None
        building, created = Building.objects.get_or_create(
                number=int(building_number), university=university)
        if created:
            logging.warn('Created building %s' % building)
        room, created = Room.objects.get_or_create(
                building=building, number=int(room_number), floor=int(room_number[0]), label=room_label)
        if created:
            logging.warn('Created room %s' % room)
        mapping[room_str] = room
    return mapping


def create_course_mapping(disciplines, academic_term):
    mapping = {}
    for discipline_name in disciplines:
        try:
            discipline = Discipline.objects.get(
                    name=discipline_name)
        except Discipline.DoesNotExist:
            discipline = Discipline.objects.create(
                    name=discipline_name,
                    code=abs(hash(discipline_name) % 2^32),
                    )
            logging.warn('Created discipline %s' % discipline)
        except Discipline.MultipleObjectsReturned:
            discipline = Discipline.objects.filter(
                    name=discipline_name)[0]
            logging.warn('Picked the first among multiple disciplines: %s' % discipline)
        course = Course.objects.create(
                discipline=discipline,
                academic_term=academic_term)
        mapping[discipline_name] = course
    return mapping


def create_lecturer_mapping(lecturers):
    mapping = {}
    for lecturer_str in lecturers:
        surname = lecturer_str.split(' ')[0]
        lecturers_surname = Lecturer.objects.filter(
                full_name__startswith=surname)
        if lecturers_surname.count() == 0:
            lecturer = Lecturer.objects.create(
                    full_name=lecturer_str)
            logging.warn('Created lecturer %s' % lecturer)
            mapping[lecturer_str] = lecturer
        elif lecturers_surname.count() >= 1:
            for lecturer in lecturers_surname:
                # if capital letters are the same
                f_f = lambda l: l.isupper()
                if filter(f_f, lecturer.full_name).startswith(
                        filter(f_f, lecturer_str)):
                    mapping[lecturer_str] = lecturer
            if not mapping.has_key(lecturer_str):
                logging.warn('Could not find match in %s' % (
                    lecturers_surname))
                lecturer = Lecturer.objects.create(
                        full_name=lecturer_str)
                logging.warn('Created lecturer %s' % lecturer)
                mapping[lecturer_str] = lecturer
    return mapping


def expand_weeks(weeks):
    result = []
    for part in weeks.split(','):
        if '-' in part:
            result += range(
                    int(part.split('-')[0]),
                    int(part.split('-')[1]) + 1
                    )
        else:
            result += [int(part)]
    return result


def populate_timetable(timetable, academic_term, table, room_mapping, course_mapping, lecturer_mapping):
    from django.db import IntegrityError, transaction
    days = [u'ПН', u'ВТ', u'СР', u'ЧТ', u'ПТ', u'СБ']
    lesson_times = [u'08:30-09:50', u'10:00-11:20', u'11:40-13:00', u'13:30-14:50',
            u'15:00-16:20', u'16:30-17:50', u'18:00-19:20']
    for course in course_mapping.values():
        timetable.courses.add(course)
    for line in table:
        day_str, time_str, room_str, course_str, group_str, lecturer_str, weeks_str = line
        try:
            day_number = days.index(day_str)
            lesson_number = lesson_times.index(time_str) + 1
            lecturer = lecturer_mapping[lecturer_str]
            course = course_mapping[course_str]
            group_number = int(group_str)
            group, created = Group.objects.get_or_create(course=course, number=group_number, lecturer=lecturer)
            room = room_mapping[room_str]
            for week in expand_weeks(weeks_str):
                try:
                    Lesson.objects.create(
                            group=group,
                            room=room,
                            lesson_number=lesson_number,
                            date=academic_term[week][day_number]
                            )
                except IntegrityError:
                    transaction.rollback()
                    conflicting_lesson = Lesson.objects.select_related().get(
                            room=room, lesson_number=lesson_number, date=academic_term[week][day_number])
                    error_message = u'Conflict: %s тиждень %s - %s - %s\n' % (room, week, days[day_number], lesson_times[lesson_number-1])
                    error_message += u'%s - %s - %s\n' % (timetable, course, lecturer)
                    error_message += u'%s - %s - %s' % (
                            ','.join(map(unicode, conflicting_lesson.group.course.timetable_set.all())),
                            conflicting_lesson.group.course.discipline,
                            conflicting_lesson.group.lecturer,
                            )
                    logging.error(error_message)
        except Exception, e:
            logging.error('%s in %s' %(e, ' '.join(line)))

def main():
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='filename',
            help='read timetable from FILE', metavar='FILE')
    parser.add_option('-c', '--code', dest='major_code',
            help='major code')
    parser.add_option('-t', '--academictermid', dest='academic_term_id',
            help='academic term id')
    parser.add_option('-y', '--year', dest='year',
            help='year of study')
    parser.add_option('-a', '--analyze', dest='analyze',
            action='store_true', help='analyze the timetable')
    parser.add_option('-i', '--import', dest='import_',
            action='store_true', help='import the timetable')
    (options, args) = parser.parse_args()
    if not options.filename or not options.major_code or not options.year:
        parser.print_help()
        return
    table = load_table(options.filename)
    university = University.objects.get()
    if options.academic_term_id:
        academic_term = AcademicTerm.objects.get(pk=int(options.academic_term_id))
    else:
        # fallback to legacy timetable_jan behaviour to keep compatibility with old bootstrap.sh
        academic_term = AcademicTerm.objects.get(number_of_weeks=12)
    if options.analyze or options.import_:
        rooms, disciplines, lecturers = analyze_table(table)
        if options.import_:
            room_mapping = create_room_mapping(rooms, university)
            course_mapping = create_course_mapping(disciplines, academic_term)
            lecturer_mapping = create_lecturer_mapping(lecturers)
            timetable, created = Timetable.objects.get_or_create(
                    year=int(options.year),
                    major=Major.objects.get(code=options.major_code),
                    academic_term=academic_term,
                    )
            populate_timetable(
                    timetable,
                    academic_term,
                    table,
                    room_mapping,
                    course_mapping,
                    lecturer_mapping,
                    )

if __name__ == '__main__':
    main()
