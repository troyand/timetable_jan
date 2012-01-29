from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from timetable_jan.university.ajax_views import *
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/favicon.ico'}),
    (r'^$', 'timetable_jan.university.views.index'),
    (r'^help/$', 'timetable_jan.university.views.help'),
    (r'^about/$', 'timetable_jan.university.views.about'),
    (r'^contacts/$', 'timetable_jan.university.views.contacts'),
    (r'^choose-subjects/(?P<timetable_id>\d+)/$', 'timetable_jan.university.views.choose_subjects'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/$', 'timetable_jan.university.views.timetable', {'action': 'render'}, name='render'),
    url(r'^ical/(?P<encoded_groups>[\d/]+)/$', 'timetable_jan.university.views.timetable', {'action': 'ical'}, name='ical'),
    (r'^rooms-status/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'timetable_jan.university.views.rooms_status'),
    (r'^lecturer-timetable/$', 'timetable_jan.university.views.lecturer_timetable'),
    (r'^robots.txt$', 'timetable_jan.university.views.robots_txt'),
    (r'autocomplete/room/$', RoomAutocompleteView.as_view()),
    (r'autocomplete/lecturer/$', LecturerAutocompleteView.as_view()),
    (r'autocomplete/discipline/$', DisciplineAutocompleteView.as_view()),
    (r'autocomplete/extra-courses/$', ExtraCoursesAutocompleteView.as_view()),
    (r'autocomplete/test/$', TemplateView.as_view(template_name='autocomplete_test.html')),
    (r'create-timetable/$', UnifiedTimetableProcessView.as_view(template_name='create_timetable.html')),
    # Examples:
    # url(r'^$', 'dj_timetable.views.home', name='home'),

    # url(r'^dj_timetable/', include('dj_timetable.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.SITE_ROOT + '/static'}),
    )
