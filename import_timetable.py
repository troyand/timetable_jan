#-*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

import csv
import codecs
from optparse import OptionParser
import logging
import datetime


logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;m:%(message)s', level=logging.INFO)

from django.core.management import setup_environ
from timetable import settings

setup_environ(settings)
from timetable.university.models import *


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
        building, created = BuildingModel.objects.get_or_create(
                number=int(building_number), university=university)
        if created:
            logging.warn('Created building %s' % building)
        room, created = RoomModel.objects.get_or_create(
                building=building, number=int(room_number), floor=int(room_number[0]), label=room_label)
        if created:
            logging.warn('Created room %s' % room)
        mapping[room_str] = room
    return mapping

def create_lecturer_mapping(lecturers):
    mapping = {}
    for lecturer_str in lecturers:
        surname = lecturer_str.split(' ')[0]
        lecturers_surname = LecturerModel.objects.filter(
                name__startswith=surname)
        if lecturers_surname.count() == 0:
            lecturer = LecturerModel.objects.create(
                    name=lecturer_str)
            logging.warn('Created lecturer %s' % lecturer)
            mapping[lecturer_str] = lecturer
        elif lecturers_surname.count() >= 1:
            for lecturer in lecturers_surname:
                # if capital letters are the same
                f_f = lambda l: l.isupper()
                if filter(f_f, lecturer.name).startswith(
                        filter(f_f, lecturer_str)):
                    mapping[lecturer_str] = lecturer
            if not mapping.has_key(lecturer_str):
                logging.warn('Could not find match in %s' % (
                    lecturers_surname))
                lecturer = LecturerModel.objects.create(
                        name=lecturer_str)
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


def populate_timetable(table, room_mapping, lecturer_mapping, group, term_begining):
    days = [u'ПН', u'ВТ', u'СР', u'ЧТ', u'ПТ', u'СБ']
    for line in table:
        day_str, time_str, room_str, discipline_str, agroup_str, lecturer_str, weeks_str = line
        beg, end = time_str.split('-')
        hour, minute = beg.split(':')
        try:
            day_number = days.index(day_str)
            lecturer = lecturer_mapping[lecturer_str]
            room = room_mapping[room_str]
            discipline, created = DisciplineModel.objects.get_or_create(name=discipline_str, code=0)
            if created:
                logging.info("created discipline %s - %s" % (discipline_str, discipline.discipline_id))


            for week in expand_weeks(weeks_str):
                timetable, created = TimeTableModel.objects.get_or_create(
                    time = term_begining + datetime.timedelta(
                        days=(7 * (week - 1) + day_number),
                        hours=int(hour),
                        minutes=int(minute)
                        ),
                    location = room,
                    lecturer = lecturer,
                    discipline = discipline,
                    academic_group = int(agroup_str),
                    )
            if created:
                logging.info("added new lesson %s" % timetable.id)
                group.lessons.add(timetable)
            else:
                logging.error("lesson already there: %s" % (' '.join(row)))
 
        except Exception, e:
            logging.error('%s in %s' %(e, ' '.join(line)))

def main():
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='filename',
            help='read timetable from FILE', metavar='FILE')
    parser.add_option('-a', '--analyze', dest='analyze',
            action='store_true', help='analyze the timetable')
    parser.add_option('-i', '--import', dest='import_',
            action='store_true', help='import the timetable')
    parser.add_option('-g', '--group', dest='groupname',
            help='import the timetable')
    (options, args) = parser.parse_args()
    if not options.filename:
        parser.print_help()
        return
    table = load_table(options.filename)
    university = UniversityModel.objects.get()
    term_begining = datetime.datetime(year=2012, month=4, day=16)
    auth_group, created = GroupModel.objects.get_or_create(name=options.groupname)
    if created:
        logging.info("created group %s" % auth_group.name)
    group, created = GroupProfile.objects.get_or_create(group=auth_group, is_public=True)

    if options.analyze or options.import_:
        rooms, disciplines, lecturers = analyze_table(table)
        if options.import_:
            room_mapping = create_room_mapping(rooms, university)
            lecturer_mapping = create_lecturer_mapping(lecturers)
            populate_timetable(
                    table,
                    room_mapping,
                    lecturer_mapping,
                    group,
                    term_begining,
                    )

if __name__ == '__main__':
    main()
