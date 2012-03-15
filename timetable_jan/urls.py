from django.conf.urls.defaults import patterns, include
from django.conf import settings
from timetable_jan.university.ajax_views import ajax_urls, UnifiedTimetableProcessView


# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/favicon.ico'}),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^', include('timetable_jan.university.urls')),
                           
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
