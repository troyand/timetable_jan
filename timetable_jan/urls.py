from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'timetable_jan.university.views.index'),
    (r'^choose-subjects/(?P<timetable_id>\d+)/$', 'timetable_jan.university.views.choose_subjects'),
    (r'^render/$', 'timetable_jan.university.views.render'),
    (r'^edit/$', 'timetable_jan.university.views.edit'),
    (r'^edit-lessons/$', 'timetable_jan.university.views.edit_lessons'),
    (r'^faculties\.json$', 'timetable_jan.university.views.faculties_json'),
    # Examples:
    # url(r'^$', 'dj_timetable.views.home', name='home'),

    # url(r'^dj_timetable/', include('dj_timetable.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.SITE_ROOT + '/static'}),
    )
