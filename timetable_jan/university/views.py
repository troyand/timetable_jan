#-*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.template import RequestContext
from timetable_jan.university.models import *
from timetable_jan.university.utils import collapse_weeks
import json
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

def faculties_json(request):
    faculties_dict = {}
    major_kinds = list(
            set([m.kind for m in Major.objects.all()]))
    for f in Faculty.objects.all():
        faculties_dict[f.name]={}
        for kind in major_kinds:
            if len(f.major_set.filter(kind=kind)) > 0:
                faculties_dict[f.name][kind] = []
                for m in f.major_set.filter(kind=kind):
                    faculties_dict[f.name][kind].append(m.name)
    return HttpResponse(
            json.dumps(faculties_dict, ensure_ascii=False, indent=2)
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
    response['Content-Disposition'] = 'attachment; filename=tt.ics'
    return response

def edit(request):
    day_lesson_mapping = {}
    # day_lesson_mapping[0][3] = [(course, group, room, weeks_str, [lesson_id1, lesson_id2, ...]), ...] # third lesson of Monday
    dates_mapping = {}
    # dates_mapping[(weekday, lesson_number, course, group, room)]=[lesson1, lesson2,...]
    timetable = Timetable.objects.select_related().get(id=2)
    for course in timetable.courses.all():
        for lesson in Lesson.objects.filter(group__in=Group.objects.filter(course=course)):
            dates_mapping.setdefault((
                lesson.date.weekday(),
                lesson.lesson_number,
                course,
                lesson.group,
                lesson.room,
                ), []).append(
                        lesson
                        )
    for weekday_number in range(0, 7):
        day_lesson_mapping[weekday_number] = {}
        for lesson_number in range(1, 8):
            day_lesson_mapping[weekday_number][lesson_number] = []
    for key in dates_mapping:
        weekday, lesson_number, course, group, room = key
        academic_term = course.academic_term
        collapsed_weeks = collapse_weeks([academic_term.get_week(l.date).week_number for l in dates_mapping[key]], course.academic_term)
        day_lesson_mapping[weekday][lesson_number].append(
                (course, group, room, collapsed_weeks, json.dumps([l.pk for l in dates_mapping[key]]))
                )


    return render_to_response('edit.html', {
        'week_dates': dict([(i, academic_term[1][i]) for i in range(0,7)]),
        'lesson_times': lesson_times,
        'day_lesson_mapping': day_lesson_mapping,
        },
        context_instance=RequestContext(request)
        )

@transaction.commit_manually
def edit_lessons(request):
    def all_equal(iterable):
        return len(set(iterable)) <= 1
    def json_fail(message):
        transaction.rollback()
        return HttpResponse(json.dumps({
            'result': 'fail',
            'message': message
            }))
    lessons = []
    for lesson_id in request.POST.getlist(u'lessons[]'):
        try:
            lessons.append(Lesson.objects.get(id=int(lesson_id)))
        except Lesson.DoesNotExist:
            return json_fail('No lesson with id %s' % lesson_id)
    # check that lessons have the same course, weekday, lesson number and room
    if not all_equal([l.room.id for l in lessons]):
        return json_fail('Rooms are not the same')
    if not all_equal([l.group.id for l in lessons]):
        return json_fail('Groups are not the same')
    if not all_equal([l.lesson_number for l in lessons]):
        return json_fail('Lesson numbers are not the same')
    if not all_equal([l.date.weekday() for l in lessons]):
        return json_fail('Weekdays are not the same')
    #print lessons
    try:
        new_lesson_number = int(request.POST[u'lesson-number'])
        old_lesson_number = lessons[0].lesson_number
        if new_lesson_number != old_lesson_number:
            for lesson in lessons:
                lesson.lesson_number = new_lesson_number
                lesson.save()
    except IntegrityError:
        return json_fail('Integrity error')
    except KeyError:
        # no lesson-number at POST
        pass
    try:
        new_weekday_number = int(request.POST[u'weekday-number'])
        old_weekday_number = lessons[0].date.weekday()
        days_diff = new_weekday_number - old_weekday_number
        if days_diff != 0:
            delta = datetime.timedelta(days_diff)
            for lesson in lessons:
                lesson.date += delta
                lesson.save()
    except IntegrityError:
        return json_fail('Integrity error')
    except KeyError:
        # no weekday-number at POST
        pass
    transaction.commit()
    return HttpResponse(json.dumps({
        'result': 'ok',
        }))


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

def return_timetable(mapping):
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
        })

def render(request, encoded_groups):
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
    for lesson in Lesson.objects.select_related().filter(
            group__in=groups):
        mapping.setdefault(lesson.date, {})
        if mapping[lesson.date].has_key(lesson.lesson_number):
            return render_to_response('error.html', {
                'error_message': u'Накладка пар: "%s" з "%s"' % (
                    mapping[lesson.date][lesson.lesson_number],
                    lesson,
                    )
                })
        else:
            mapping[lesson.date][lesson.lesson_number] = lesson
            lessons.append(lesson)
    #return ical(request, lessons)
    return return_timetable(mapping)


def soft_eng_3_q(request, timetable_id):
    timetable = get_object_or_404(Timetable, pk=timetable_id)
    mapping = {} # mapping[date][lesson_number]=Lesson()
    for lesson in Lesson.objects.select_related().filter(
            group__in=Group.objects.filter(
                course__in=timetable.courses.all()
                ).filter(Q(number=0) | Q(number=1))):
        mapping.setdefault(lesson.date, {})
        if mapping[lesson.date].has_key(lesson.lesson_number):
            raise Exception('Lesson overlapping: %s with %s' % (
                mapping[lesson.date][lesson.lesson_number],
                lesson,
                ))
        else:
            mapping[lesson.date][lesson.lesson_number] = lesson
    return return_timetable(mapping)

def soft_eng_3(request):
    timetable = Timetable.objects.all()[0] # for test get just the first one
    mapping = {} # mapping[date][lesson_number]=Lesson()
    for course in timetable.courses.all():
        groups = [] # for test only 0th group for lectures and 1st for practice
        try:
            groups.append(course.group_set.get(number=0))
        except Group.DoesNotExist:
            print 'No lectures for %s' % course.discipline
        try:
            groups.append(course.group_set.get(number=1))
        except Group.DoesNotExist:
            print 'No practice for %s' % course.discipline
        for group in groups:
            for lesson in group.lesson_set.all():
                mapping.setdefault(lesson.date, {})
                if mapping[lesson.date].has_key(lesson.lesson_number):
                    raise Exception('Lesson overlapping: %s with %s' % (
                        mapping[lesson.date][lesson.lesson_number],
                        lesson,
                        ))
                else:
                    mapping[lesson.date][lesson.lesson_number] = lesson
    if min(mapping.keys()).weekday() != 0:
        print 'First day of study is not Monday!' # add dummy days so that week starts on Monday
    first_monday = min(mapping.keys())
    week_mapping = {}
    week_date_mapping = {}
    number_of_weeks = int(math.ceil(
            float((max(mapping.keys()) - min(mapping.keys())).days) / 7))
    number_of_rows = 6 
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
        })
    return HttpResponse('Ok')
