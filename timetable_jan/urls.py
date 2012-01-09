from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/favicon.ico'}),
    (r'^$', 'timetable_jan.university.views.index'),
    (r'^choose-subjects/(?P<timetable_id>\d+)/$', 'timetable_jan.university.views.choose_subjects'),
    url(r'^render/(?P<encoded_groups>[\d/]+)/$', 'timetable_jan.university.views.timetable', {'action': 'render'}, name='render'),
    url(r'^ical/(?P<encoded_groups>[\d/]+)/$', 'timetable_jan.university.views.timetable', {'action': 'ical'}, name='ical'),
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
