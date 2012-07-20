#-*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from timetable.university.models import *
from timetable.university.forms import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from htmlmin.decorators import minified_response
import math
import datetime
import re
import itertools
import json


from django.template.defaultfilters import register as rf

@rf.filter(name='lookup')
def lookup(dictionary, index):
    if index in dictionary:
        return dictionary[index]
    return None

@rf.filter(name='vertical')
def vertical(string):
    return ' '.join(list(string))

promos = {
        datetime.date(2012,4,19): [
            ('img/promo/ultramarine.png', 'https://www.facebook.com/events/166568366799044/'),
            ],
        datetime.date(2012,4,20): [
            ('img/promo/social_ship.png', 'http://vk.com/social_ship'),
            ('img/promo/fsnst_day.png', 'http://vk.com/event37945333'),
            ],
        datetime.date(2012,4,26): [
            ('img/promo/glasses_party.png', 'http://vk.com/event37852523'),
            ],
        datetime.date(2012,4,27): [
            ('img/promo/vynnyi.png', 'http://vk.com/vynnyi'),
            ],
        datetime.date(2012,5,11): [
            ('img/promo/perevtilnyi.png', 'http://vk.com/perevtilnyi'),
            ],
        datetime.date(2012,5,15): [
            ('img/promo/d3-logo.png', ''),
            ],
        datetime.date(2012,5,16): [
            ('img/promo/shockolad.png', 'https://www.facebook.com/events/348381305217123/'),
            ],
        datetime.date(2012,5,18): [
            ('img/promo/fi_day.png', ''),
            ],
        datetime.date(2012,5,25): [
            ('img/promo/konvorablyk.png', 'https://plazerazzi.org/konvorablyk'),
            ],
        }


class ICALResponseMixin(object):
    """Mixin which produces an ical file as a response to a request."""
    def render_to_response(self, context):
        lessons = context.get('lessons') or Lesson.objects.all()
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
        

class BaseTimetableView(View):
    """
    Basic view for a timetable.

    Fills context with some initial info: mapping with user's lessons, clashing lessons info,
    groups which user wants to be shown, week user wants to be shown,
    list with all of the user's lessons, first monday of studying.
    """
    def get(self, request, *args, **kwargs):
        """Renders a page using a generated context in a response to a GET request."""
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        """Returns a context data for this request."""
        return self._get_initial_data()
        
    def _get_initial_data(self):
        """
        Retrieves all initial data required for rendering a timetable page.

        Returns a map with keys: 'mapping', 'user_group_list', 'clashing_lessons',
        'week_to_show', 'lessons', 'first_monday'.
        """
        # Get captured params
        encoded_groups = self.kwargs.get("encoded_groups")
        week_to_show = self.kwargs.get("week_to_show")
        group_to_show = self.kwargs.get("group_to_show")
        # All user's groups (both lecture and practise).
        groups = []
        # Which groups (lecture + practise) must be shown to a user in a timetable.
        groups_to_show = []
        # Which group the user has selected to show. 
        group_to_show = group_to_show and int(group_to_show)
        # Which groups must be shown to user in a filtering list (lecture groups
        # aren't include here becaue they're paired with a practise ones)
        user_group_list = []
        group_ids = [int(g) for g in encoded_groups.split('/')]
        for group_id in group_ids:
            # add practice group
            group = get_object_or_404(Group, pk=group_id)
            groups.append(group)
            user_group_list.append(group)
            if group_to_show and group_id == group_to_show:
                groups_to_show.append(group)
            # add lecture group if it is present
            try:
                lecture_group = group.course.group_set.get(number=0)
                groups.append(lecture_group)
                # Add lecture group if user has choosen related practise one
                # as a filtering option.
                if group_to_show and group_id == group_to_show:
                    groups_to_show.append(lecture_group)
            except Group.DoesNotExist:
                pass
        if not group_to_show:
            groups_to_show = groups
        mapping = {} # mapping[date][lesson_number]=Lesson()
        lessons = []
        clashing_lessons = []
        for lesson in Lesson.objects.select_related().filter(
                group__in=groups_to_show):
            mapping.setdefault(lesson.date, {})
            if mapping[lesson.date].has_key(lesson.lesson_number):
                clashing_lessons.append((
                        mapping[lesson.date][lesson.lesson_number],
                        lesson,
                        ))
            else:
                mapping[lesson.date][lesson.lesson_number] = lesson
            lessons.append(lesson)

        # Find first monday of studying.
        if min(mapping.keys()).weekday() != 0:
            from datetime import timedelta
            mapping[min(mapping.keys())-timedelta(days=min(mapping.keys()).weekday())]={}
            #print 'First day of study is not Monday!' # add dummy days so that week starts on Monday
        first_monday = min(mapping.keys())

        data = {}
        data['mapping'] = mapping
        data['user_group_list'] = user_group_list
        data['clashing_lessons'] = clashing_lessons
        data['week_to_show'] = week_to_show
        data['lessons'] = lessons
        data['first_monday'] = first_monday
        return data

                
class ICALView(ICALResponseMixin, BaseTimetableView):
    """View which produces an ical-file with a timetable."""
    pass
        

class TimetableView(TemplateResponseMixin, BaseTimetableView):
    """Main timetable view with some filtering options."""
    template_name = "timetable.html"

    def get_context_data(self, **kwargs):
        "Adds info required by a template."
        context = super(TimetableView, self).get_context_data(**kwargs)
        data = self._generate_context_data(context)
        context.update(data)
        return context

    def _generate_context_data(self, context):
        """Generates all information required by a template from a previously obtained context."""
        # Acquire initial info
        request = self.request
        mapping = context.get('mapping')
        groups = context.get('user_group_list')
        clashing_lessons = context.get('clashing_lessons') or []
        week = context.get('week_to_show')
        week = week and int(week)
        first_monday = context.get('first_monday')
        
        week_mapping = {}
        week_date_mapping = {}
        number_of_weeks = int(math.ceil(
                float((max(mapping.keys()) - min(mapping.keys())).days) / 7))
        number_of_rows = 2
        starting_week = self._sanitize_week(week or 1, number_of_weeks) 
        finishing_week = self._sanitize_week(week or number_of_weeks, number_of_weeks)
        for week_number in range(starting_week, finishing_week + 1):
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

        week_links = self._generate_week_links(number_of_weeks)
        group_links, current_group_name = self._generate_group_links_and_name(groups)

        #pprint.pprint(mapping)
        return {
                    'week_mapping': week_mapping,
                    'week_date_mapping': week_date_mapping,
                    'lesson_times': lesson_times,
                    'lesson_numbers': range(1,8),
                    'clashing_lessons': clashing_lessons,
                    'week_links': week_links,
                    'current_week': week or u'Всі тижні',
                    'group_links': group_links,
                    'current_group': current_group_name, 
                    'promos': promos,
                }

    def _sanitize_week(self, week, max_week):
        """Ensures that a week is in range [1, max_week]."""
        # REVIEW Maybe must fire some exception and write error to user
        result = week
        if result > max_week:
            result = max_week
        if result < 1:
            result = 1
        return result

    def _generate_week_links(self, number_of_weeks):
        """Generates a list of links to timetable pages of a particular weeks."""
        request = self.request
        link_parts = re.split('(group/\d+/)', request.path)
        all_weeks_link = re.sub(r'week/.+?/', u'', link_parts[0]) + 'weeks/' 
        all_weeks_link += link_parts[1] if len(link_parts) > 1 else u''
        week_links = [(u'Всі тижні', all_weeks_link)]
        for week_number in range(1, number_of_weeks + 1):
            week_link = None
            if request.path.find(u'week/') != -1:
                week_link = re.sub(r'week/\d+', u'week/%i' % week_number,
                                   request.path)
            else:
                link_parts = re.split('(group/\d+/)', request.path)
                tt_link = re.sub(r'weeks/', u'', link_parts[0])
                group_link = link_parts[1] if len(link_parts) > 1 else u''
                week_link = tt_link + u'week/%i/' % week_number + group_link
            week_links.append((week_number, week_link))
        return week_links

    def _generate_group_links_and_name(self, groups):
        """Generates a list of links to timetable pages of particular courses and finds current group's name."""
        request = self.request
        current_group_number = re.search("group/(\d*)", request.path)
        current_group_number = current_group_number and current_group_number.group(1)
        current_group_name = u'Всі пари'
        group_links = [(u'Всі пари', re.sub(r'/group/.*', '/', request.path))]
        for group in groups:
            group_full_name = group.course.discipline.name + u' - ' + \
                              unicode(group.number) 
            group_links.append(
                (group_full_name,
                 re.sub(r'group/.*', '', request.path) + u'group/' + \
                 str(group.pk) + u'/'))
            if current_group_number and unicode(group.pk) == current_group_number:
                current_group_name = group_full_name
        return group_links, current_group_name

    
class TimetableMainView(TimetableView):
    """Main timetable view - opens a timetable filtering view for a current week."""
    def _generate_context_data(self, context):
        "Changes week_to_show in a context to a current week."
        today = datetime.date.today()
        # for Sunday show the following Monday
        if today.isoweekday() == 7:
            today += datetime.timedelta(days=1)
        days_diff = abs(today - context['first_monday']).days
        week = days_diff / 7 + 1
        context['week_to_show'] = week
        return super(TimetableMainView, self)._generate_context_data(context)


def index(request):
    timetables = Timetable.objects.select_related().all()
    academic_term_timetable_mapping = {}
    for timetable in timetables:
        academic_term_timetable_mapping.setdefault(
                timetable.academic_term,
                []).append(timetable)
    academic_term_timetable_list = sorted(
            academic_term_timetable_mapping.items(),
            key=lambda x: x[0].start_date,
            reverse=True
            )
    return render_to_response(
            'index.html',
            {
                'academic_term_timetable_list': academic_term_timetable_list,
                },
            context_instance=RequestContext(request)
            )

def help(request):
    return render_to_response(
            'help.html',
            {},
            context_instance=RequestContext(request)
            )

def about(request):
    return render_to_response(
            'about.html',
            {},
            context_instance=RequestContext(request)
            )

def contacts(request):
    return render_to_response(
            'contacts.html',
            {},
            context_instance=RequestContext(request)
            )

def palette(size):
    import colorsys
    for i in range(size):
        rgb_tuple = colorsys.hsv_to_rgb(
                float(i)/size,
                1,
                0.4 + 0.1 * (i % 7))
        hexcolor = '#%02x%02x%02x' % tuple(map(lambda x: int(x*255), rgb_tuple))
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

@cache_page(60*60*24)
#@minified_response
def planning(request):
    academic_term = AcademicTerm.objects.all()[2]
    lessons = Lesson.objects.select_related('room', 'room__building', 'group', 'group__course__discipline').filter(
            date__gte=academic_term.start_date
            ).filter(
            date__lt=academic_term.exams_start_date
            ).filter(
            room__building__number__gt=0
            ).order_by('date')
    # mapping[(1,1)][Room('1-225')]=[(1,Lesson('A')), (2,Lesson('A'))]
    rooms = set()
    mapping = {}
    course_ids = set()
    for lesson in lessons:
        date_timekey = (lesson.date.isoweekday(), lesson.lesson_number)
        if not mapping.has_key(date_timekey):
            mapping[date_timekey] = {}
        if not mapping[date_timekey].has_key(lesson.room):
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
    for hexcolor, course_id in itertools.izip(palette(number_of_courses), course_ids):
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
                time_rows.append((day_names[weekday], lesson_times[lesson_number][0]))
            else:
                time_rows.append((None, lesson_times[lesson_number][0]))
            date_timekey = (weekday, lesson_number)
            for room in sorted_rooms:
                cell = []
                if mapping.has_key(date_timekey) and mapping[date_timekey].has_key(room):
                    cell_mapping = dict(mapping[date_timekey][room])
                    for week_number in range(1, academic_term.number_of_weeks+1):
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
def planning_light(request):
    academic_term = AcademicTerm.objects.all()[2]
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
                },
            context_instance=RequestContext(request)
            )

def planning_light_room(request, room_id):
    academic_term = AcademicTerm.objects.all()[2]
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
                },
            context_instance=RequestContext(request)
            )

color_palette = list(palette(400))

#@cache_page(60*60*24)
def planning_ajax(request, room_id):
    academic_term = AcademicTerm.objects.all()[2]
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

def planning_room_ajax(request, room_id):
    academic_term = AcademicTerm.objects.all()[2]
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

@login_required
def profile(request):
    try:
        student = request.user.get_profile().student
    except Student.DoesNotExist:
        student = None
        student_form = None
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
        if student:
            student_form = StudentForm(request.POST, instance=student)
            if student_form.is_valid():
                student_form.save()
    else:
        user_form = UserForm(instance=request.user)
        if student:
            student_form = StudentForm(instance=student)
    return render_to_response(
            'profile.html',
            {
                'user_form': user_form,
                'student_form': student_form,
                },
            context_instance=RequestContext(request)
            )

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
                'timetable': timetable,
                },
            context_instance=RequestContext(request)
            )

def rooms_status(request, year, month, day):
    import datetime
    status_date = datetime.date(int(year), int(month), int(day))
    lessons = list(Lesson.objects.select_related().filter(
        date=status_date
        ))
    # mapping[building][lesson_number][room] = lesson
    mapping = {}
    # building_rooms[building] = set(room, room, room)
    building_rooms = {}
    for lesson in lessons:
        building = lesson.room.building
        room = lesson.room
        building_rooms.setdefault(
                building, set()).add(room)
        mapping.setdefault(building, {}).setdefault(
                lesson.lesson_number, {})[room] = lesson
    building_tables = []
    for building in sorted(building_rooms.keys(), key=lambda x: (x.number, x.label)):
        table = []
        rooms = sorted(building_rooms[building], key=lambda x: u'%s' % x)
        table.append([u''] + [u'%s' % r for r in rooms])
        for lesson_number in sorted(mapping[building].keys()):
            row = [u'%s' % lesson_times[lesson_number][0]]
            for room in rooms:
                try:
                    row.append(
                            mapping[building][lesson_number][room]
                            )
                except KeyError:
                    row.append(None)
            table.append(row)
        building_tables.append((building, table))
    return render_to_response(
            'rooms_status.html',
            {
                'status_date': status_date,
                'building_tables': building_tables,
                },
            context_instance=RequestContext(request)
            )

def lecturer_timetable(request):
    import locale
    locale.setlocale(locale.LC_ALL, "en_US.utf8")
    #add filtering for only current academic term
    groups = Group.objects.select_related().all()
    # department_lecturer_groups[department][lecturer] = set(group_id1, group_id2)
    department_lecturer_groups = {}
    # lecturer_groups[lecturer] = set(group_id1, group_id2)
    lecturer_groups = {}
    for group in groups:
        lecturer = group.lecturer
        lecturer_groups.setdefault(lecturer, set()).add(group.pk)
    for lecturer in lecturer_groups.keys():
        departments = list(lecturer.departments.all())
        if len(departments) > 0:
            for department in departments:
                department_lecturer_groups.setdefault(
                        department, {})[lecturer] = lecturer_groups[lecturer]
        else:
            department = u"Інша"
            department_lecturer_groups.setdefault(
                    department, {})[lecturer] = lecturer_groups[lecturer]
    department_lecturer_groups_mapping = {}
    for department in department_lecturer_groups.keys():
        lecturer_groups_list = []
        lecturer_groups = department_lecturer_groups[department]
        for lecturer in sorted(
                lecturer_groups.keys(),
                cmp=lambda x,y : locale.strcoll(x.full_name, y.full_name)):
            lecturer_groups_list.append(
                    (
                        lecturer, 
                        '/'.join(map(unicode, lecturer_groups[lecturer]))
                        )
                    )
        department_lecturer_groups_mapping[department] = lecturer_groups_list
    return render_to_response(
            'lecturer_timetable.html',
            {
                'department_lecturer_groups_mapping': department_lecturer_groups_mapping,
                },
            context_instance=RequestContext(request)
            )

def robots_txt(request):
    return HttpResponse("User-agent: *\nDisallow: /\n", mimetype="text/plain")

def http_gone(request):
    return HttpResponse(status=410)
