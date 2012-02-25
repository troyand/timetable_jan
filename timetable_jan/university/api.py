from django.conf.urls.defaults import patterns, include
from django.shortcuts import get_object_or_404
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.api import Api
from timetable_jan.university.models import *


#------------------------ Resources ----------------------------------

class UniversityResource(ModelResource):
    class Meta:
        queryset = University.objects.all()
        resource_name = 'universities'
        allowed_methods = ['get']


class AcademicTermResource(ModelResource):
    university = fields.ForeignKey(UniversityResource, 'university')

    class Meta:
        queryset = AcademicTerm.objects.all()
        resource_name = 'terms'
        allowed_methods = ['get']

#------------------------ API view -----------------------------------
v1_api = Api(api_name='v1')
v1_api.register(UniversityResource())
v1_api.register(AcademicTermResource())

urls = patterns('',
    (r'^', include(v1_api.urls)),
)