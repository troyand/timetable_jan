#-*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from timetable_jan.university.cb_views import *
from django.views.generic import TemplateView
from timetable_jan.university.ajax_views import ajax_urls, UnifiedTimetableProcessView
from timetable_jan.university.views import IcalView, TimetableView, TimetableIndexView


urlpatterns = patterns('',
    (r'^$', 'timetable_jan.university.views.index'),
    (r'^help/$', 'timetable_jan.university.views.help'),
    (r'^about/$', 'timetable_jan.university.views.about'),
    (r'^contacts/$', 'timetable_jan.university.views.contacts'),
    (r'^choose-subjects/(?P<timetable_id>\d+)/$', 'timetable_jan.university.views.choose_subjects'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/$', TimetableIndexView.as_view(), name='render-index'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/group/(?P<group_to_show>\d+)/$', TimetableIndexView.as_view(), name='render-index-group'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/weeks/$', TimetableView.as_view(), name='render-all'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/weeks/group/(?P<group_to_show>\d+)/$', TimetableView.as_view(), name='render-all-group'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/week/(?P<week_to_show>\d+)/$', TimetableView.as_view(), name='render-week'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/week/(?P<week_to_show>\d+)/group/(?P<group_to_show>\d+)/$', TimetableView.as_view(), name='render-week-group'),
    url(r'^ical/(?P<encoded_groups>[\d/]+)/$', IcalView.as_view(), name='ical'),
    (r'^rooms-status/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'timetable_jan.university.views.rooms_status'),
    (r'^lecturer-timetable/$', 'timetable_jan.university.views.lecturer_timetable'),
    (r'^robots.txt$', 'timetable_jan.university.views.robots_txt'),
    (r'^[a-z0-9]+.ics$', 'timetable_jan.university.views.http_gone'),
    (r'^accounts/profile/$', 'timetable_jan.university.views.profile'),
    url(r'^lesson/(?P<pk>\d+)/$', LessonDetailView.as_view(template_name="lesson.html"), name='lesson'),
    (r'^autocomplete/', include(ajax_urls)),
    (r'create-timetable/$', UnifiedTimetableProcessView.as_view(template_name='create_timetable.html')),
    url(r'^feedback/$', FeedbackView.as_view(template_name='feedback.html')),
)

