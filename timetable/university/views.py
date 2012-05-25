# vim: ai ts=4 sts=4 et sw=4
#-*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from timetable.university.models import *
from timetable.university.forms import *
from django.contrib.auth.decorators import login_required
import datetime

from django.template.defaultfilters import register as rf

#FIXME: hack, should be in db or smwr else
term_begining = datetime.datetime(year=2012, month=4, day=16)

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

def split_lessons(lessons, begin, delta):
    '''split lessons list into lists grouped within delta time interval.
        Takes sorted lessons list'''
    week_list = []
    last_lesson = 0
    current = 0
    for lesson in lessons:
        if lesson.time >= begin + delta:
            i = 1
            # increase delta, if delta less than two adjasent times
            while lesson.time >= begin + delta * (i + 1):
                i += 1
            begin += delta * i
            # possible if very first lesson > begin+delta
            if last_lesson != current:
                week_list.append( lessons[last_lesson:current] )
            last_lesson = current
        current += 1
    # append remaining lessons
    if len(lessons[last_lesson:]) > 0:
        week_list.append( lessons[last_lesson:] )
    return week_list



class ICALResponseMixin(object):
    """Mixin which produces an ical file as a response to a request."""
    def render_to_response(self, context):
        lessons = context.get('lessons') or LessonModel.objects.all()
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
        
class ICALView(ICALResponseMixin):
    """View which produces an ical-file with a timetable."""
    pass


def index(request):
    groups = GroupProfile.objects.select_related('GroupModel').filter(is_public=True)
    return render_to_response(
            'index.html',
            { 'groups': groups, },
            context_instance=RequestContext(request)
            )

def group(request, group):
    lessons = TimeTableModel.objects.select_related('LecturerModel', 'RoomModel', 'DisciplineModel').filter(groupprofile__group=group).order_by('time')
    return return_timetable(request, lessons)

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

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserForm(instance=request.user)
    return render_to_response(
            'profile.html',
            {
                'user_form': user_form,
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

def weeknum(time):
    return (time - term_begining).days // 7 + 1

def return_timetable(request, lessons):
    week_mapping = {}
    weeks = split_lessons(lessons, term_begining, datetime.timedelta(days=7))
    for week in weeks:
        week_begin = week[0].time
        week_number = weeknum(week_begin)
        week_mapping[week_number] = {}
            
        week_begin = week_begin - datetime.timedelta(hours=week_begin.hour, minutes=week_begin.minute)
        days = split_lessons(week, week_begin, datetime.timedelta(days=1))
        for day_number in range(0,6):
            if not week_mapping[week_number].has_key(day_number//3):
                week_mapping[week_number][day_number//3] = {}
            week_mapping[week_number][day_number//3][day_number] = {}

        for day in days:
            day_number = day[0].time.weekday()
            lesson_number = 0
            for lesson in day:
                week_mapping[week_number][day_number//3][day_number][lesson_number] = lesson
                lesson_number += 1
    return render_to_response(
            'timetable.html',
            {
                'week_mapping': week_mapping,
                'lesson_numbers': range(0,7),
                'lesson_times': lesson_times,
                'promos': promos,
                },
            context_instance=RequestContext(request)
            )

def rooms_status(request, year, month, day):
    #FIXME: steaming pile of crap
    status_date=datetime.date(int(year), int(month), int(day))
    start_time = datetime.datetime(int(year), int(month), int(day),0,0)
    next_day = datetime.datetime(int(year), int(month), int(day) + 1, 0, 0)
    lessons = list(TimeTableModel.objects.select_related('DisciplineModel', 'RoomModel', 'BuildingModel').filter(
        time__gt=start_time, time__lt=next_day
        ))
    # mapping[building][time][room] = lesson
    mapping = {}
    # building_rooms[building] = set(room, room, room)
    building_rooms = {}
    for lesson in lessons:
        building = lesson.location.building
        room = lesson.location
        building_rooms.setdefault(
                building, set()).add(room)
        mapping.setdefault(building, {}).setdefault(
                "%d:%d" % (lesson.time.hour, lesson.time.minute),
                {})[room] = lesson
    building_tables = []
    for building in sorted(building_rooms.keys(), key=lambda x: (x.number, x.label)):
        table = []
        rooms = sorted(building_rooms[building], key=lambda x: u'%s' % x)
        table.append([u''] + [u'%s' % r for r in rooms])
        for t in sorted(mapping[building].keys()):
            row = [u'%s' % t]
            for room in rooms:
                try:
                    row.append(
                            mapping[building][t][room]
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

def lecturers(request):
    department_lecturer_mapping = {}
    #FIXME: master _single_ query: join 3 tables
    lecturers = LecturerModel.objects.select_related()
    for lecturer in lecturers:
        for dep in lecturer.department.all():
            if not department_lecturer_mapping.has_key(dep):
                department_lecturer_mapping[dep] = []
            department_lecturer_mapping[dep].append(lecturer)

    print lecturers.query
    return render_to_response(
        'lecturer_timetable.html',
        {
            'department_lecturer_mapping': department_lecturer_mapping,
        },
        context_instance=RequestContext(request)
        )

def lecturer_timetable(request, lecturer):
    lessons = TimeTableModel.objects.select_related('LecturerModel', 'RoomModel', 'DisciplineModel').filter(lecturer=lecturer).order_by('time')
    return return_timetable(request, lessons)

def robots_txt(request):
    return HttpResponse("User-agent: *\nDisallow: /\n", mimetype="text/plain")

def http_gone(request):
    return HttpResponse(status=410)
