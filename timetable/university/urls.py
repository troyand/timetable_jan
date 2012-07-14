#-*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from timetable.university.cb_views import *
from django.views.generic import TemplateView
from timetable.university.ajax_views import ajax_urls, UnifiedTimetableProcessView
from timetable.university.views import ICALView, TimetableView, TimetableMainView


urlpatterns = patterns('',
    (r'^$', 'timetable.university.views.index'),
    (r'^help/$', 'timetable.university.views.help'),
    (r'^about/$', 'timetable.university.views.about'),
    (r'^contacts/$', 'timetable.university.views.contacts'),
    (r'^planning/$', 'timetable.university.views.planning'),
    (r'^planning-light/$', 'timetable.university.views.planning_light'),
    (r'^course-stats/$', 'timetable.university.views.course_stats'),
    (r'^planning-light/(?P<room_id>\d+)/$', 'timetable.university.views.planning_ajax'),
    (r'^choose-subjects/(?P<timetable_id>\d+)/$', 'timetable.university.views.choose_subjects'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/$', TimetableMainView.as_view(), name='render-main'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/group/(?P<group_to_show>\d+)/$', TimetableMainView.as_view(), name='render-main-group'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/weeks/$', TimetableView.as_view(), name='render-all'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/weeks/group/(?P<group_to_show>\d+)/$', TimetableView.as_view(), name='render-all-group'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/week/(?P<week_to_show>\d+)/$', TimetableView.as_view(), name='render-week'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/week/(?P<week_to_show>\d+)/group/(?P<group_to_show>\d+)/$', TimetableView.as_view(), name='render-week-group'),
    url(r'^ical/(?P<encoded_groups>[\d/]+)/$', ICALView.as_view(), name='ical'),
    (r'^rooms-status/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'timetable.university.views.rooms_status'),
    (r'^lecturer-timetable/$', 'timetable.university.views.lecturer_timetable'),
    (r'^robots.txt$', 'timetable.university.views.robots_txt'),
    (r'^[a-z0-9]+.ics$', 'timetable.university.views.http_gone'),
    (r'^accounts/profile/$', 'timetable.university.views.profile'),
    url(r'^lesson/(?P<pk>\d+)/$', LessonDetailView.as_view(template_name="lesson.html"), name='lesson'),
    (r'^autocomplete/', include(ajax_urls)),
    (r'create-timetable/$', UnifiedTimetableProcessView.as_view(template_name='create_timetable.html')),
    url(r'^feedback/$', FeedbackView.as_view(template_name='feedback.html')),
)

