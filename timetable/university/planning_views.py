#-*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from timetable.university.models import *
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from htmlmin.decorators import minified_response
import math
import itertools
import json
from django.db import transaction, IntegrityError
import logging

logger = logging.getLogger(__name__)



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
    for i in range(2, size/2 + 1):
        if size % i == 0:
            raise Exception(
                    'Palette size must be a prime number. '
                    '%d has a divisor %d' % (size, i)
                    )
    base_element = 3
    current_element = base_element
    for i in range(size):
        rgb_tuple = colorsys.hsv_to_rgb(
            float(current_element) / size,
            1,
            0.4 + 0.1 * (current_element % 7))
        hexcolor = '#%02x%02x%02x' % tuple(
            map(lambda x: int(x * 255), rgb_tuple))
        yield hexcolor
        current_element = (current_element * base_element) % size


def course_stats(request, term):
    from django.db.models import Count
    academic_term = get_object_or_404(AcademicTerm, id=int(term))
    groups = Group.objects.select_related(
        'course', 'course__discipline').defer(
            'course__discipline__description').filter(
                course__academic_term=academic_term
            ).annotate(
                lesson_count=Count('lesson')).order_by('course', 'number')
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
            'non_lectures': [(k, v)
                             for k, v in sorted(mapping[course].items())
                             if k != 0]
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
    for weekday in range(1, 7):
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
        academic_term = get_object_or_404(
                AcademicTerm.objects.select_related(),
                pk=term
                )
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
        for weekday in range(1, 7):
            for lesson_number in lesson_times.keys():
                if lesson_number == 1:
                    time_rows.append(
                        (day_names[weekday], lesson_times[lesson_number][0]))
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
        academic_term = context['academic_term']
        if academic_term.number_of_weeks < 10:
            px_per_day = 12
        else:
            px_per_day = 8
        context['px_per_day'] = px_per_day
        room_column_width = academic_term.number_of_weeks * px_per_day
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

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PlanningLightRoomView, self).dispatch(request, *args, **kwargs)

    def _generate_context_data(self, context):
        """Adds some specific info for room planning to context."""
        context = super(PlanningLightRoomView, self)._generate_context_data(
            context)
        column_width = 34
        context['column_width'] = column_width
        #FIXME change to smth more elaborate (user-dependent/...)
        context['rooms'] = list(enumerate(
            [Room.objects.get(number=100, building__number=4),
            Room.objects.get(number=317, building__number=4)]
            ))
        context['all_rooms'] = Room.objects.select_related(
                'building', 'building__university').all()
        context['all_courses'] = []
        for course in Course.objects.select_related('discipline').prefetch_related(
                'group_set').filter(academic_term=context['academic_term']).order_by(
                        'discipline__name'):
            context['all_courses'].append((course, sorted([
                [group.number, group.pk] for group in course.group_set.all()])))
        return context

    def _get_columns(self, context):
        """Returns all weeks for a given term."""
        academic_term = context['academic_term']
        week_numbers = range(1, academic_term.number_of_weeks + 1)
        return week_numbers


class PlanningLightRoomDeleteView(PlanningLightRoomView):
    template_name = 'planning_light_room_delete.html'

color_palette = list(palette(401))


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
        context['room'] = Room.objects.get(pk=context['room_id'])
        return context

    def _get_lessons(self, context):
        """By default, get the lessons based on the room"""
        return Lesson.objects.select_related(
            'room', 'room__building',
            'group', 'group__course__discipline').filter(
                date__gte=context['academic_term'].start_date,
                date__lt=context['academic_term'].exams_start_date,
                room__pk=context['room_id'],
            ).order_by('date')

    def _generate_context_data(self, context):
        """Adds room, mapping info to a context."""
        academic_term = context['academic_term']
        lessons = self._get_lessons(context)
        mapping = {}
        course_ids = set()
        for lesson in lessons:
            date_timekey = (lesson.date.isoweekday(), lesson.lesson_number)
            if not date_timekey in mapping:
                mapping[date_timekey] = {}
            if not lesson.room in mapping[date_timekey]:
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
        for weekday in range(1, 7):
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
        if date_timekey in mapping and room in mapping[date_timekey]:
            cell_mapping = dict(mapping[date_timekey][room])
            for week_number in range(1, academic_term.number_of_weeks + 1):
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
        if date_timekey in mapping and room in mapping[date_timekey]:
            cell_mapping = dict(mapping[date_timekey][room])
        else:
            cell_mapping = {}
        for week_number in range(1, academic_term.number_of_weeks + 1):
            item = self._generate_lesson_json(cell_mapping, week_number)
            json_response['cell-%d-%d-%d' % (weekday, lesson_number, week_number)] = item
        return json_response


class PlanningRoomAddLessonsAjaxView(PlanningRoomAjaxView):
    def _generate_lesson_json(self, cell_mapping, week_number):
        """Adds a name of a lesson to its JSON representation."""
        item = super(PlanningRoomAddLessonsAjaxView, self)._generate_lesson_json(
            cell_mapping, week_number)
        if week_number in cell_mapping:
            item['html'] = cell_mapping[week_number].group.number or u'л'
        else:
            item['html'] = u'<input type="checkbox">'
        return item


class PlanningRoomDeleteLessonsAjaxView(PlanningRoomAjaxView):
    def _generate_lesson_json(self, cell_mapping, week_number):
        """Adds a name of a lesson to its JSON representation."""
        item = super(PlanningRoomDeleteLessonsAjaxView, self)._generate_lesson_json(
            cell_mapping, week_number)
        if week_number in cell_mapping:
            item['html'] = u'<input type="checkbox" data-lesson-id="%d">' % (
                    cell_mapping[week_number].pk,
                    )
        else:
            item['html'] = u''
        return item


class PlanningRoomAjaxLecturerView(JSONResponseMixin, TermExtractorMixin, BaseView):
    def _get_initial_data(self, **kwargs):
        """Adds room id to the initial data."""
        context = super(PlanningRoomAjaxLecturerView, self)._get_initial_data(**kwargs)
        context['group_id'] = kwargs.get('group_id')
        group = Group.objects.get(pk=context['group_id'])
        context['lesson_count'] = group.lesson_set.count()
        context['lecturer'] = group.lecturer
        return context

    def _get_lessons(self, context):
        return Lesson.objects.select_related(
            'room', 'room__building',
            'group', 'group__course__discipline').filter(
                date__gte=context['academic_term'].start_date,
                date__lt=context['academic_term'].exams_start_date,
                group__lecturer=context['lecturer'],
            ).order_by('date')

    def _generate_context_data(self, context):
        return context

    def _generate_json_response(self, context):
        mapping = {}
        academic_term = context['academic_term']
        for lesson in self._get_lessons(context):
            mapping[(
                lesson.date.isoweekday(),
                lesson.lesson_number,
                academic_term.get_week(lesson.date).week_number)] = lesson
        json_response = {}
        json_response['lesson_count'] = context['lesson_count']
        json_response['lecturer'] = context['lecturer'].short_name()
        json_response['cells'] = {}
        for weekday in range(1, 7):
            for lesson_number in lesson_times.keys():
                for week_number in range(1, academic_term.number_of_weeks + 1):
                    key = (weekday, lesson_number, week_number)
                    if key in mapping:
                        json_response['cells']['cell-%d-%d-%d' % key] = {
                                'css_class': 'lecturer-busy',
                                }
                    else:
                        json_response['cells']['cell-%d-%d-%d' % key] = {
                                'css_class': 'lecturer-free',
                                }
        return json_response


class PlanningAddLessonsAjaxView(View, TermExtractorMixin):
    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden('Forbidden')
        context = self._get_initial_data(**kwargs)
        rooms = {}
        academic_term = context['academic_term']
        with transaction.commit_manually():
            try:
                for i in [0, 1]:
                    room_id = request.POST['window-%s' % i]
                    rooms[i] = get_object_or_404(
                            Room.objects.select_related('building'),
                            pk=room_id
                            )
                group = get_object_or_404(
                        Group,
                        pk=request.POST['group']
                        )
                # TODO check if the user is authorized to add lessons
                # for this group (e.g. if they have course permissions)
                cells = request.POST.getlist('cells[]')
                for cell in cells:
                    parts = cell.split('-')
                    window_number = int(parts[1])
                    day_number = int(parts[3])
                    lesson_number = int(parts[4])
                    week_number = int(parts[5])
                    l = Lesson.objects.create(
                            group=group,
                            room=rooms[window_number],
                            date=academic_term[week_number][day_number-1],
                            lesson_number=lesson_number,
                            )
                    logger.info(u'%s added %s (lesson id=%d, course id=%d)' % (
                        request.user,
                        l,
                        l.pk,
                        l.group.course.pk
                        )
                        )
                transaction.commit()
                return HttpResponse(
                        'ok'
                        )
            except KeyError:
                transaction.rollback()
                return HttpResponseBadRequest(
                        'key error'
                        )
            except IndexError:
                transaction.rollback()
                return HttpResponseBadRequest(
                        'index error'
                        )
            except ValueError:
                transaction.rollback()
                return HttpResponseBadRequest(
                        'value error'
                        )
            except IntegrityError:
                transaction.rollback()
                return HttpResponseBadRequest(
                        'db integrity error'
                        )
            except:
                transaction.rollback()
                raise

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed('Method not allowed')

    def put(self, request, *args, **kwargs):
        return HttpResponseNotAllowed('Method not allowed')

    def delete(self, request, *args, **kwargs):
        return HttpResponseNotAllowed('Method not allowed')

class PlanningDeleteLessonsAjaxView(PlanningAddLessonsAjaxView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden('Forbidden')
        context = self._get_initial_data(**kwargs)
        with transaction.commit_manually():
            try:
                # TODO check if the user is authorized to delete the lessons
                # (e.g. if they have course permissions)
                cells = request.POST.getlist('cells[]')
                for cell in cells:
                    l = get_object_or_404(
                            Lesson,
                            pk=cell,
                            )
                    logger.info(u'%s deleted %s (lesson id=%d, course id=%d)' % (
                        request.user,
                        l,
                        l.pk,
                        l.group.course.pk
                        )
                        )
                    l.delete()
                transaction.commit()
                return HttpResponse(
                        'ok'
                        )
            except KeyError:
                transaction.rollback()
                return HttpResponseBadRequest(
                        'key error'
                        )
            except IndexError:
                transaction.rollback()
                return HttpResponseBadRequest(
                        'index error'
                        )
            except ValueError:
                transaction.rollback()
                return HttpResponseBadRequest(
                        'value error'
                        )
            except IntegrityError:
                transaction.rollback()
                return HttpResponseBadRequest(
                        'db integrity error'
                        )
            except:
                transaction.rollback()
                raise
