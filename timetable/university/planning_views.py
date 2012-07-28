#-*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from timetable.university.models import *
from django.views.decorators.cache import cache_page
from htmlmin.decorators import minified_response
import math
import itertools
import json


def choose_term_for_planning(request):
    """Renders a page with a chooser of term for term planning."""
    return render_to_response(
            'choose_term_for_planning.html',
            {
                'terms': AcademicTerm.objects.all(),
            },
            context_instance=RequestContext(request)
            )


def palette(size):
    import colorsys
    for i in range(size):
        rgb_tuple = colorsys.hsv_to_rgb(
            float(i) / size,
            1,
            0.4 + 0.1 * (i % 7))
        hexcolor = '#%02x%02x%02x' % tuple(
            map(lambda x: int(x * 255), rgb_tuple))
        yield hexcolor


def course_stats(request):
    from django.db.models import Count
    academic_term = AcademicTerm.objects.all()[2]
    groups = Group.objects.select_related('course', 'course__discipline').defer('course__discipline__description').filter(course__academic_term=academic_term
            ).annotate(lesson_count=Count('lesson')).order_by('course', 'number')
    mapping = {}
    # mapping[Course] = {0: 13, 1: 6, 2: 6}
    for group in groups:
        mapping.setdefault(group.course, {})[group.number] = group.lesson_count
        #group, group.lesson_count
    rows = []
    for course in sorted(mapping.keys(), key=lambda c: c.discipline.name):
        if len(set([v for k, v in mapping[course].items() if k != 0])) > 1:
            inconsistent = True
        else:
            inconsistent = False
        rows.append({
            'name': course.discipline.name,
            'lectures': mapping[course].get(0, 0),
            'inconsistent': inconsistent,
            'non_lectures': [(k,v) for k, v in sorted(mapping[course].items()) if k != 0]
            })
    return render_to_response(
            'course_stats.html',
            {
                'rows': rows,
                },
            context_instance=RequestContext(request)
            )


@cache_page(60 * 60 * 24)
def planning(request, term):
    """
    Renders a page with an overall view of a given term.

    term - number of a term to render
    """
    term = int(term)
    if term < 0 or term >= AcademicTerm.objects.count():
        raise Http404
    academic_term = AcademicTerm.objects.all()[term]
    lessons = Lesson.objects.select_related(
        'room', 'room__building', 'group', 'group__course__discipline').filter(
            date__gte=academic_term.start_date,
            date__lt=academic_term.exams_start_date,
            room__building__number__gt=0
        ).order_by('date')
    # mapping[(1,1)][Room('1-225')]=[(1,Lesson('A')), (2,Lesson('A'))]
    rooms = set()
    mapping = {}
    course_ids = set()
    for lesson in lessons:
        date_timekey = (lesson.date.isoweekday(), lesson.lesson_number)
        if not date_timekey in mapping:
            mapping[date_timekey] = {}
        if not lesson.room in mapping[date_timekey]:
            mapping[date_timekey][lesson.room] = []
        rooms.add(lesson.room)
        course_ids.add(lesson.group.course_id)
        mapping[date_timekey][lesson.room].append(
            (
                academic_term.get_week(lesson.date).week_number,
                lesson
            )
        )
    course_colors = {}
    number_of_courses = len(course_ids)
    for hexcolor, course_id in itertools.izip(
            palette(number_of_courses), course_ids):
        course_colors[course_id] = hexcolor
    ##
    rows = []
    time_rows = []
    sorted_rooms = sorted(rooms, key=lambda x: u'%s' % x)
    #print sorted_rooms
    for weekday in range(1,7):
        for lesson_number in lesson_times.keys():
            #row_names.append('%s-%s' % (weekday, lesson_times[lesson_number][0]))
            row = []
            if lesson_number == 1:
                time_rows.append(
                    (day_names[weekday], lesson_times[lesson_number][0]))
            else:
                time_rows.append((None, lesson_times[lesson_number][0]))
            date_timekey = (weekday, lesson_number)
            for room in sorted_rooms:
                cell = []
                if date_timekey in mapping and room in mapping[date_timekey]:
                    cell_mapping = dict(mapping[date_timekey][room])
                    for week_number in range(
                            1, academic_term.number_of_weeks + 1):
                        if week_number in cell_mapping:
                            cell.append(
                                {
                                    'css_class': 'lesson',
                                    'background_color': course_colors[cell_mapping[week_number].group.course_id],
                                    'title': u'Тиждень %d' % week_number,
                                    'content': u'%s - %s' % (
                                        cell_mapping[week_number].group.course.discipline.name,
                                        cell_mapping[week_number].group.number or u'лекція'),
                                }
                            )
                        else:
                            cell.append(
                                {
                                    'css_class': 'free',
                                    'background_color': 'inherit',
                                    'title': u'Тиждень %d' % week_number,
                                    'content': u'Пара відсутня',
                                }
                            )
                else:
                    pass
                    # the following is too slow, better just to leave cell empty
                    #for week_number in range(1, academic_term.number_of_weeks+1):
                    #    cell.append(
                    #            {
                    #                'css_class': 'free',
                    #                'background_color': 'inherit'
                    #                }
                    #            )
                row.append(cell)
            rows.append(row)
    px_per_day = 8
    return render_to_response(
        'planning.html',
        {
            'number_of_weeks': academic_term.number_of_weeks,
            'room_column_width': academic_term.number_of_weeks * px_per_day,
            'rows': rows,
            'time_rows': time_rows,
            'px_per_day': px_per_day,
            'sorted_rooms': sorted_rooms,
            'number_of_lessons_per_day': len(lesson_times.keys()),
        },
        context_instance=RequestContext(request)
    )


#@cache_page(60*60*24)
#@minified_response
def planning_light(request, term):
    term = int(term)
    if term < 0 or term >= AcademicTerm.objects.count():
        raise Http404
    academic_term = AcademicTerm.objects.all()[term]
    rooms = Room.objects.select_related('building').filter(building__number__gt=0)
    rows = []
    time_rows = []
    sorted_rooms = sorted(rooms, key=lambda x: u'%s' % x)
    for weekday in range(1,7):
        for lesson_number in lesson_times.keys():
            row = []
            if lesson_number == 1:
                time_rows.append((day_names[weekday], lesson_times[lesson_number][0]))
            else:
                time_rows.append((None, lesson_times[lesson_number][0]))
            for room in sorted_rooms:
                cell = '%d-%d-%d' % (weekday, lesson_number, room.pk)
                row.append(cell)
            rows.append(row)
    px_per_day = 8
    return render_to_response(
            'planning_light.html',
            {
                'number_of_weeks': academic_term.number_of_weeks,
                'room_column_width': academic_term.number_of_weeks * px_per_day,
                'rows': rows,
                'time_rows': time_rows,
                'px_per_day': px_per_day,
                'sorted_rooms': sorted_rooms,
                'number_of_lessons_per_day': len(lesson_times.keys()),
                'term': term,
                },
            context_instance=RequestContext(request)
            )


def planning_light_room(request, term, room_id):
    term = int(term)
    if term < 0 or term >= AcademicTerm.objects.count():
        raise Http404
    academic_term = AcademicTerm.objects.all()[term]
    #room = Room.objects.select_related('building').get_object_or_404
    room = get_object_or_404(Room, pk=room_id)
    rows = []
    time_rows = []
    week_numbers = range(1, academic_term.number_of_weeks + 1)
    for weekday in range(1,7):
        for lesson_number in lesson_times.keys():
            row = []
            if lesson_number == 1:
                time_rows.append((day_names[weekday], lesson_times[lesson_number][0]))
            else:
                time_rows.append((None, lesson_times[lesson_number][0]))
            for week_number in week_numbers:
                cell = '%d-%d-%d' % (weekday, lesson_number, week_number)
                row.append(cell)
            rows.append(row)
    column_width = 78
    return render_to_response(
            'planning_light_room.html',
            {
                'number_of_weeks': academic_term.number_of_weeks,
                'column_width': column_width,
                'rows': rows,
                'time_rows': time_rows,
                'week_numbers': week_numbers,
                'room': room,
                'number_of_lessons_per_day': len(lesson_times.keys()),
                'term': term,
                },
            context_instance=RequestContext(request)
            )


color_palette = list(palette(400))

#@cache_page(60*60*24)
def planning_ajax(request, term, room_id):
    term = int(term)
    if term < 0 or term >= AcademicTerm.objects.count():
        raise Http404
    academic_term = AcademicTerm.objects.all()[term]
    room = Room.objects.get(pk=room_id)
    lessons = Lesson.objects.select_related('room', 'room__building', 'group', 'group__course__discipline').filter(
            date__gte=academic_term.start_date
            ).filter(
            date__lt=academic_term.exams_start_date
            ).filter(
            room__pk=room_id
            ).order_by('date')
    # mapping[(1,1)][Room('1-225')]=[(1,Lesson('A')), (2,Lesson('A'))]
    mapping = {}
    course_ids = set()
    for lesson in lessons:
        date_timekey = (lesson.date.isoweekday(), lesson.lesson_number)
        if not mapping.has_key(date_timekey):
            mapping[date_timekey] = {}
        if not mapping[date_timekey].has_key(lesson.room):
            mapping[date_timekey][lesson.room] = []
        course_ids.add(lesson.group.course_id)
        mapping[date_timekey][lesson.room].append(
                (
                    academic_term.get_week(lesson.date).week_number,
                    lesson
                    )
                )
    json_response = {}
    for weekday in range(1,7):
        for lesson_number in lesson_times.keys():
            date_timekey = (weekday, lesson_number)
            cell = []
            if mapping.has_key(date_timekey) and mapping[date_timekey].has_key(room):
                cell_mapping = dict(mapping[date_timekey][room])
                for week_number in range(1, academic_term.number_of_weeks+1):
                    if week_number in cell_mapping:
                        cell.append(
                                {
                                    'css_class': 'lesson',
                                    'background_color': color_palette[cell_mapping[week_number].group.course_id % len(color_palette)],
                                    'title': u'Тиждень %d' % week_number,
                                    'content': u'%s - %s' % (
                                        cell_mapping[week_number].group.course.discipline.name,
                                        cell_mapping[week_number].group.number or u'лекція'),
                                    }
                                )
                    else:
                        cell.append(
                                {
                                    'css_class': 'free',
                                    'background_color': 'inherit',
                                    'title': u'Тиждень %d' % week_number,
                                    'content': u'Пара відсутня',
                                    }
                                )
            else:
                pass
            divs = ''.join(['<div class="%s" title="%s" data-content="%s" style="background: %s">&nbsp;</div>' % (
                item['css_class'],
                item['title'],
                item['content'],
                item['background_color'],
                ) for item in cell])
            if cell:
                json_response['cell-%d-%d-%d' % (weekday, lesson_number, room.pk)] = divs
    return HttpResponse(json.dumps(json_response), mimetype="application/json")

def planning_room_ajax(request, term, room_id):
    term = int(term)
    if term < 0 or term >= AcademicTerm.objects.count():
        raise Http404
    academic_term = AcademicTerm.objects.all()[term]
    room = Room.objects.get(pk=room_id)
    lessons = Lesson.objects.select_related('room', 'room__building', 'group', 'group__course__discipline').filter(
            date__gte=academic_term.start_date
            ).filter(
            date__lt=academic_term.exams_start_date
            ).filter(
            room__pk=room_id
            ).order_by('date')
    # mapping[(1,1)][Room('1-225')]=[(1,Lesson('A')), (2,Lesson('A'))]
    mapping = {}
    course_ids = set()
    for lesson in lessons:
        date_timekey = (lesson.date.isoweekday(), lesson.lesson_number)
        if not mapping.has_key(date_timekey):
            mapping[date_timekey] = {}
        if not mapping[date_timekey].has_key(lesson.room):
            mapping[date_timekey][lesson.room] = []
        course_ids.add(lesson.group.course_id)
        mapping[date_timekey][lesson.room].append(
                (
                    academic_term.get_week(lesson.date).week_number,
                    lesson
                    )
                )
    json_response = {}
    for weekday in range(1,7):
        for lesson_number in lesson_times.keys():
            date_timekey = (weekday, lesson_number)
            if mapping.has_key(date_timekey) and mapping[date_timekey].has_key(room):
                cell_mapping = dict(mapping[date_timekey][room])
            else:
                cell_mapping = {}
            for week_number in range(1, academic_term.number_of_weeks+1):
                if week_number in cell_mapping:
                    item = {
                            'css_class': 'lesson',
                            'background_color': color_palette[cell_mapping[week_number].group.course_id % len(color_palette)],
                            'title': u'Тиждень %d' % week_number,
                            'content': u'%s - %s' % (
                                cell_mapping[week_number].group.course.discipline.name,
                                cell_mapping[week_number].group.number or u'лекція'),
                            }
                else:
                    item = {
                            'css_class': 'free',
                            'background_color': 'inherit',
                            'title': u'Тиждень %d' % week_number,
                            'content': u'Пара відсутня',
                            }
                json_response['cell-%d-%d-%d' % (weekday, lesson_number, week_number)] = item
    return HttpResponse(json.dumps(json_response), mimetype="application/json")