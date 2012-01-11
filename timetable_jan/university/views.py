#-*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from timetable_jan.university.models import *
import math
import datetime


from django.template.defaultfilters import register as rf

@rf.filter(name='lookup')
def lookup(dictionary, index):
    if index in dictionary:
        return dictionary[index]
    return None

@rf.filter(name='vertical')
def vertical(string):
    return ' '.join(list(string))


def index(request):
    timetables = Timetable.objects.all()
    return render_to_response(
            'index.html',
            {
                'timetables': timetables,
                }
            )

def help(request):
    return render_to_response(
            'help.html',
            {}
            )

def about(request):
    return render_to_response(
            'about.html',
            {}
            )

def contacts(request):
    return render_to_response(
            'contacts.html',
            {}
            )

def ical(request, lessons=Lesson.objects.all()):
    import icalendar
    cal = icalendar.Calendar()
    cal.add('prodid', '-//USIC timetable//')
    cal.add('version', '2.0')
    for lesson in lessons:
        cal.add_component(lesson.icalendar_event())
    response = HttpResponse(
            cal.as_string().replace(';VALUE=DATE', ''),
            mimetype='text/calendar'
            )
    response['Content-Disposition'] = 'attachment; filename=universitytimetabe.ics'
    return response



def choose_subjects(request, timetable_id):
    timetable = get_object_or_404(Timetable, pk=timetable_id)
    course_groups = {}
    for course in timetable.courses.all():
        course_groups[course] = sorted(course.group_set.filter(number__gt=0), key=lambda g: g.number)
        if len(course_groups[course]) == 0:
            course_groups[course] = course.group_set.all()
    return render_to_response(
            'choose_subjects.html',
            {
                'course_groups': course_groups,
                },
            context_instance=RequestContext(request)
            )

def return_timetable(mapping, clashing_lessons=[]):
    if min(mapping.keys()).weekday() != 0:
        from datetime import timedelta
        mapping[min(mapping.keys())-timedelta(days=min(mapping.keys()).weekday())]={}
        #print 'First day of study is not Monday!' # add dummy days so that week starts on Monday
    first_monday = min(mapping.keys())
    week_mapping = {}
    week_date_mapping = {}
    number_of_weeks = int(math.ceil(
            float((max(mapping.keys()) - min(mapping.keys())).days) / 7))
    number_of_rows = 2
    for week_number in range(1, number_of_weeks + 1):
        week_mapping[week_number] = {}
        week_date_mapping[week_number] = {}
        for row in range(0, number_of_rows):
            week_mapping[week_number][row] = {}
            for i in range(0, 6/number_of_rows):
                weekday = row*(6/number_of_rows) + i
                week_mapping[week_number][row][weekday] = {}
                date = first_monday + datetime.timedelta(days=
                        7*(week_number-1) + weekday)
                week_date_mapping[week_number][weekday] = date
                if not mapping.has_key(date):
                    mapping[date] = {}
                for lesson_number in range(1, 8):
                    if mapping[date].has_key(lesson_number):
                        week_mapping[week_number][row][weekday][lesson_number] = mapping[date][lesson_number]
                    else:
                        week_mapping[week_number][row][weekday][lesson_number] = None

    #pprint.pprint(mapping)
    return render_to_response('timetable.html', {
        'week_mapping': week_mapping,
        'week_date_mapping': week_date_mapping,
        'lesson_times': lesson_times,
        'lesson_numbers': range(1,8),
        'clashing_lessons': clashing_lessons,
        })

def timetable(request, encoded_groups, **kwargs):
    groups = []
    group_ids = [int(g) for g in encoded_groups.split('/')]
    for group_id in group_ids:
        # add practice group
        group = get_object_or_404(Group, pk=group_id)
        groups.append(group)
        # add lecture group if it is present
        try:
            lecture_group = group.course.group_set.get(number=0)
            groups.append(lecture_group)
        except Group.DoesNotExist:
            pass
    mapping = {} # mapping[date][lesson_number]=Lesson()
    lessons = []
    clashing_lessons = []
    for lesson in Lesson.objects.select_related().filter(
            group__in=groups):
        mapping.setdefault(lesson.date, {})
        if mapping[lesson.date].has_key(lesson.lesson_number):
            clashing_lessons.append((
                    mapping[lesson.date][lesson.lesson_number],
                    lesson,
                    ))
        else:
            mapping[lesson.date][lesson.lesson_number] = lesson
        lessons.append(lesson)
    if kwargs['action'] == 'ical':
        return ical(request, lessons)
    elif kwargs['action'] == 'render':
        return return_timetable(mapping, clashing_lessons)


def rooms_status(request, year, month, day):
    import datetime
    #def daterange(start_date, end_date):
    #    for n in range((end_date - start_date).days):
    #        yield start_date + datetime.timedelta(n)
    #TODO change to more flexible
    #start_date = datetime.date(2012, 1, 9)
    #end_date = datetime.date(2012, 1, 12)
    # evaluate the queryset by converting it to the list
    #lessons = list(Lesson.objects.select_related().filter(
    #        date__gt=start_date).filter(
    #                date__lt=end_date)
    #        )
    lessons = list(Lesson.objects.select_related().filter(
        date=datetime.date(int(year), int(month), int(day))
        ))
    mapping = {}
    rooms = set()
    for lesson in lessons:
        first_key = (lesson.date, lesson.lesson_number)
        second_key = lesson.room.pk
        mapping.setdefault(first_key, {}
                )[second_key] = lesson
        rooms.add(lesson.room)
    rooms = sorted(rooms, key=lambda x: u'%s' % x)
    table = []
    header = [u''] + [u'%s' % r for r in rooms]
    for first_key in sorted(mapping.keys()):
        row = [(u'', u'', u'%d' % first_key[1])]
        for room in rooms:
            try:
                row.append(
                        (
                        mapping[first_key][room.pk].group.course.discipline.name,
                        mapping[first_key][room.pk].group.number or u'лекція',
                        mapping[first_key][room.pk].group.course.discipline.abbr()
                        )
                        )
            except KeyError:
                row.append(u'')
        table.append(row)
    return render_to_response(
            'rooms_status.html',
            {
                'header': header,
                'table': table
                }
            )
