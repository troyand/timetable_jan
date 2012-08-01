#-*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
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


class BaseView(View):
    """
    Base view - simple template for a request handlers.
    """
    def get(self, request, *args, **kwargs):
        """
        Response to a GET request.

        Renders a page using a generated context in a response to a GET
        request.
        """
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Returns a context data for this request."""
        context = self._get_initial_data(**kwargs)
        data = self._generate_context_data(context)
        context.update(data)
        return context

    def render_to_response(self, context):
        """Renders a given context in a some manner."""
        raise NotImplementedError

    def _get_initial_data(self, **kwargs):
        """
        Retrieves all initial data required for rendering a page.
        """
        raise NotImplementedError

    def _generate_context_data(self, context):
        """
        Generates additional required context data based on a given context.
        """
        raise NotImplementedError


class TermExtractorMixin(object):
    """
    Extracts a 'term' parameter from a request.
    """
    def _get_initial_data(self, **kwargs):
        """
        Retrieves all initial data required for rendering a planning page.

        Main goal - extract captured parameters.
        Returns a map with pairs: 'term' - id of a term, 'academic_term' -
        AcademicTerm object from a DB.
        """
        data = {}
        # Get captured params
        term = int(kwargs.get('term'))
        if term < 0 or term >= AcademicTerm.objects.count():
            raise Http404
        academic_term = AcademicTerm.objects.all()[term]
        data['academic_term'] = academic_term
        data['term'] = term
        return data


class BasePlanningView(TermExtractorMixin, BaseView):
    """
    Base view for a table generation part of a planning.

    Fills context with some initial info: term, number of weeks in it, rows and
    columns for a planning table, number of lessons per day.
    """
    def _generate_context_data(self, context):
        """
        Generates additional required context data based on a given context.

        Adds such pairs to a context: 'number_of_weeks' - number of weeks in a
        given term, 'rows' - rows list for a planning table, 'time_rows' -
        names of rows for a planning table, 'number_of_lessons_per_day' -
        maximum number of lessons in a day, child-specific columns pair.
        """
        rows = []
        time_rows = []
        columns = self._get_columns(context)
        for weekday in range(1,7):
            for lesson_number in lesson_times.keys():
                if lesson_number == 1:
                    time_rows.append((day_names[weekday], lesson_times[lesson_number][0]))
                else:
                    time_rows.append((None, lesson_times[lesson_number][0]))
                rows.append(
                    self._generate_row(weekday, lesson_number, columns))
        academic_term = context['academic_term']
        context['number_of_weeks'] = academic_term.number_of_weeks
        context['rows'] = rows
        context['time_rows'] = time_rows
        context['number_of_lessons_per_day'] = len(lesson_times.keys())
        context['columns'] = columns
        return context

    def _generate_row(self, weekday, lesson_number, columns):
        """Generates a row for a given weekday and lesson number."""
        row = []
        for item in columns:
            cell = '%d-%d-%d' % (weekday, lesson_number,
                                 self._get_column_name(item))
            row.append(cell)
        return row

    def _get_columns(self, context):
        """Generates columns data source for a planning table."""
        raise NotImplementedError

    def _get_column_name(self, column):
        """Returns a name for a given column."""
        return column


class PlanningLightView(TemplateResponseMixin, BasePlanningView):
    """Main planning view that obtains actual info using ajax."""
    template_name = 'planning_light.html'

    def _generate_context_data(self, context):
        """Adds some specific info for term planning overview to context."""
        px_per_day = 8
        context['px_per_day'] = px_per_day
        academic_term = context['academic_term']
        # TODO change this
        room_column_width = academic_term.number_of_weeks * px_per_day
        # increase value in order to make correct tables when number of weeks
        # is small (~ 3-300ФПвН and 6 weeks)
        room_column_width = 72 if room_column_width < 72 else room_column_width
        context['room_column_width'] = room_column_width
        return super(PlanningLightView, self)._generate_context_data(context)

    def _get_columns(self, _):
        """Returns all available rooms as a sorted list."""
        rooms = Room.objects.select_related('building').filter(
            building__number__gt=0)
        sorted_rooms = sorted(rooms, key=lambda x: u'%s' % x)
        return sorted_rooms

    def _get_column_name(self, item):
        """Returns room's number.'"""
        return item.pk


class PlanningLightRoomView(TemplateResponseMixin, BasePlanningView):
    """
    Planning view for a specific room that obtains actual info using ajax.
    """
    template_name = 'planning_light_room.html'

    def _get_initial_data(self, **kwargs):
        """Adds room id to the initial data."""
        context = super(PlanningLightRoomView, self)._get_initial_data(**kwargs)
        context['room_id'] = kwargs.get('room_id')
        return context

    def _generate_context_data(self, context):
        """Adds some specific info for room planning to context."""
        context = super(PlanningLightRoomView, self)._generate_context_data(
            context)
        column_width = 78
        context['column_width'] = column_width
        context['room'] = get_object_or_404(Room, pk=context['room_id'])
        return context

    def _get_columns(self, context):
        """Returns all weeks for a given term."""
        academic_term = context['academic_term']
        week_numbers = range(1, academic_term.number_of_weeks + 1)
        return week_numbers


color_palette = list(palette(400))

class JSONResponseMixin(object):
    """Renders a page as a JSON response."""
    def render_to_response(self, context):
        """Renders a given context as a JSON-response."""
        json_response = self._generate_json_response(context)
        return HttpResponse(json.dumps(json_response),
                            mimetype="application/json")

    def _generate_json_response(self, context):
        """Generates a data (map) required for a JSON response."""
        raise NotImplementedError


class BasePlanningAjaxView(JSONResponseMixin, TermExtractorMixin, BaseView):
    """
    Base view for an ajax part of a planning.

    Fills context with some initial info: term, room, room+date:lesson mapping:
    mapping[(1,1)][Room('1-225')]=[(1,Lesson('A')), (2,Lesson('A'))].

    Returns an JSON response generated from a mapping using a child-class
    implementation of a generation method.
    """
    def _get_initial_data(self, **kwargs):
        """Adds room id to the initial data."""
        context = super(BasePlanningAjaxView, self)._get_initial_data(**kwargs)
        context['room_id'] = kwargs.get('room_id')
        return context

    def _generate_context_data(self, context):
        """Adds room, mapping info to a context."""
        academic_term = context['academic_term']
        room_id = context['room_id']
        context['room'] = Room.objects.get(pk=room_id)
        lessons = Lesson.objects.select_related(
            'room', 'room__building',
            'group', 'group__course__discipline').filter(
                date__gte=academic_term.start_date,
                date__lt=academic_term.exams_start_date,
                room__pk=room_id
            ).order_by('date')
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
        context['mapping'] = mapping
        return context

    def _generate_json_response(self, context):
        """
        Returns a map with pairs:
        'cell-%d-%d-%d' % (weekday, lesson_number, room.pk): required info
        """
        json_response = {}
        for weekday in range(1,7):
            for lesson_number in lesson_times.keys():
                date_timekey = (weekday, lesson_number)
                json_response = self._update_json_for_timeday(
                    json_response, date_timekey, context)
        return json_response

    def _update_json_for_timeday(self, json_response, date_timekey, context):
        """
        Updates a given JSON response and returns an updated copy.

        Adds information for a given week day and lesson number to a response.
        """
        raise NotImplementedError

    def _generate_lesson_json(self, cell_mapping, week_number):
        """
        Generates a JSON-like representation for a lesson.

        Info is generated for a a given week_number from a cell_mapping.
        """
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
        return item


class PlanningAjaxView(BasePlanningAjaxView):
    """Ajax part of a main planning view."""
    def _update_json_for_timeday(self, json_response, date_timekey, context):
        cell = []
        mapping = context['mapping']
        room = context['room']
        academic_term = context['academic_term']
        (weekday, lesson_number) = date_timekey
        if mapping.has_key(date_timekey) and mapping[date_timekey].has_key(room):
            cell_mapping = dict(mapping[date_timekey][room])
            for week_number in range(1, academic_term.number_of_weeks+1):
                cell.append(self._generate_lesson_json(
                    cell_mapping, week_number))
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
        return json_response


class PlanningRoomAjaxView(BasePlanningAjaxView):
    """Ajax part of a room planning view."""
    def _update_json_for_timeday(self, json_response, date_timekey, context):
        mapping = context['mapping']
        room = context['room']
        academic_term = context['academic_term']
        (weekday, lesson_number) = date_timekey
        if mapping.has_key(date_timekey) and mapping[date_timekey].has_key(room):
            cell_mapping = dict(mapping[date_timekey][room])
        else:
            cell_mapping = {}
        for week_number in range(1, academic_term.number_of_weeks+1):
            item = self._generate_lesson_json(cell_mapping, week_number)
            json_response['cell-%d-%d-%d' % (weekday, lesson_number, week_number)] = item
        return json_response

    def _generate_lesson_json(self, cell_mapping, week_number):
        """Adds a name of a lesson to its JSON representation."""
        item = super(PlanningRoomAjaxView, self)._generate_lesson_json(
            cell_mapping, week_number)
        if week_number in cell_mapping:
            item['html'] = cell_mapping[week_number].group.number or u'лекція'
        else:
            item['html'] = u''
        return item