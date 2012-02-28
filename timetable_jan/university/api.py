from django.conf.urls.defaults import patterns, include, url
from tastypie import fields
from tastypie.api import Api
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from timetable_jan.university.models import *


#------------------------ Resources ----------------------------------
class ModelResource(ModelResource):
    """Basic ModelResource that supports nested resources."""
    def override_urls(self):
        urls = []
        for name, field in self.fields.items():
            if isinstance(field, fields.ToManyField):
                related_class = field.to_class()
                urls.extend([
                    url(r"^(?P<resource_name>%s)/(?P<%s>\w[\w/-]*)/%s%s$"
                        % (self._meta.resource_name,
                           field.related_name,
                           field.attribute,
                           trailing_slash()),
                        related_class.wrap_view('dispatch_list'),
                        name="api_dispatch_list"),
                    url(r"^(?P<resource_name>%s)/(?P<%s>\w[\w/-]*)/%s/schema%s$"
                        % (self._meta.resource_name,
                           field.related_name,
                           field.attribute,
                           trailing_slash()),
                        related_class.wrap_view('get_schema'),
                        name="api_get_schema"),
                    url(r"^(?P<resource_name>%s)/(?P<%s>\w[\w/-]*)/%s/set/(?P<pk_list>\w[\w/;-]*)/$"
                        % (self._meta.resource_name,
                           field.related_name,
                           field.attribute),
                        related_class.wrap_view('get_multiple'),
                        name="api_get_multiple"),
                    url(r"^(?P<resource_name>%s)/(?P<%s>\w[\w/-]*)/%s/(?P<pk>\w[\w/-]*)%s$"
                        % (self._meta.resource_name,
                           field.related_name,
                           field.attribute,
                           trailing_slash()),
                        related_class.wrap_view('dispatch_detail'),
                        name="api_dispatch_detail"),])
        return urls
        
    def dehydrate(self, bundle):
        """
        Removes fields that describe nested resources from an output.
        """
        for name, field in self.fields.items():
            if isinstance(field, fields.ToManyField):
                del bundle.data[name]
        return bundle
        
        
class UniversityResource(ModelResource):
    terms = fields.ToManyField(
        'timetable_jan.university.api.AcademicTermResource',
        "terms", "university", null=True)

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

        filtering = {
            "university": ('exact',),
            }
        

#------------------------ API links ----------------------------------
v1_api = Api(api_name='v1')
v1_api.register(UniversityResource())
#v1_api.register(AcademicTermResource())

urls = patterns('',
    (r'^', include(v1_api.urls)),
)