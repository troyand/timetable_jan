#-*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns


urlpatterns = patterns('',
    (r'/lesson/get/(?P<lesson_id>\d+)/$', 'timetable.comments.views.get_lesson_comments'),
    (r'/lesson/post/(?P<lesson_id>\d+)/$', 'timetable.comments.views.post_lesson_comment'),
)
