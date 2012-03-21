#-*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from timetable_jan.university.models import *
from timetable_jan.university.forms import *
from django.contrib.auth.decorators import login_required
import math
import datetime
import re


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
    timetables = Timetable.objects.select_related().all()
    return render_to_response(
            'index.html',
            {
                'timetables': timetables,
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
                'timetable': timetable,
                },
            context_instance=RequestContext(request)
            )

def return_timetable(request, mapping, groups, clashing_lessons=[], week=None):
    def sanitize_week(week, max_week):
        # REVIEW Maybe must fire some exception and write error to user
        result = week
        if result > max_week:
            result = max_week
        if result < 1:
            result = 1
        return result

    if week:
        week = int(week)
    
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
    starting_week = sanitize_week(week or 1, number_of_weeks) 
    finishing_week = sanitize_week(week or number_of_weeks, number_of_weeks)
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
                        
        
    link_prefix = request.path
    week_links = []
    if week:
        week_links.append((u'Всі тижні', re.sub(r'week/.+', u'', link_prefix)))
    for week_number in range(1, number_of_weeks + 1):
        if week_number != week:
            week_link = None
            if link_prefix.find(u'week') != -1:
                week_link = re.sub(r'week/\d+', u'week/%i' % week_number,
                                   link_prefix)
            else:
                week_link = link_prefix + u'week/%i/' % week_number
            week_links.append((week_number, week_link))

    group_links = None
    show_group_links = False

    if week:
        group_links = []
        group_links.append((u'Всі пари',
                            re.sub(r'/group/.*', '/', request.path)))
        for group in groups:
            group_links.append(
                (group.course.discipline.name + u' - ' + unicode(group.number),
                 re.sub(r'group/.*', '', request.path) + u'group/' + str(group.pk) + u'/'))

        show_group_links = True
        

    #pprint.pprint(mapping)
    return render_to_response(
            'timetable.html',
            {
                'week_mapping': week_mapping,
                'week_date_mapping': week_date_mapping,
                'lesson_times': lesson_times,
                'lesson_numbers': range(1,8),
                'clashing_lessons': clashing_lessons,
                'week_links': week_links,
                'group_links': group_links,
                'show_group_links': show_group_links,
                },
            context_instance=RequestContext(request)
            )

def timetable(request, encoded_groups, week_to_show=None, group_to_show=None, **kwargs):
    groups = []
    groups_to_show = []
    user_group_list = []
    group_to_show = group_to_show and int(group_to_show)
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
    if kwargs['action'] == 'ical':
        return ical(request, lessons)
    elif kwargs['action'] == 'render':
        return return_timetable(request, mapping, user_group_list,
                                clashing_lessons, week_to_show) 


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

