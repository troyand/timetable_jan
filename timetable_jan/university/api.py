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
                # TODO add link to child resources
                #bundle.data[field.attribute + u'_uri'] = 
        return bundle
        
        
class UniversityResource(ModelResource):
    terms = fields.ToManyField(
        'timetable_jan.university.api.AcademicTermResource',
        'terms', 'university', null=True)
    buildings = fields.ToManyField(
        'timetable_jan.university.api.BuildingResource',
        'buildings', 'university', null=True)
    faculties = fields.ToManyField(
        'timetable_jan.university.api.FacultyResource',
        'faculties', 'university', null=True)

    class Meta:
        queryset = University.objects.all()
        resource_name = 'universities'
        allowed_methods = ['get']


class AcademicTermResource(ModelResource):
    university = fields.ForeignKey(UniversityResource, 'university')
    courses = fields.ToManyField(
        'timetable_jan.university.api.CourseResource',
        'courses', 'academic_term', null=True)

    class Meta:
        queryset = AcademicTerm.objects.all()
        resource_name = 'terms'
        allowed_methods = ['get']

        filtering = {
            'university': ('exact',),
            }


class BuildingResource(ModelResource):
    university = fields.ForeignKey(UniversityResource, 'university')
    rooms = fields.ToManyField(
        'timetable_jan.university.api.RoomResource',
        'rooms', 'building', null=True)
    
    class Meta:
        queryset = Building.objects.all()
        resource_name = 'buildings'
        allowed_methods = ['get']

        filtering = {
            'university': ('exact',),
            }
        
        
class RoomResource(ModelResource):
    building = fields.ForeignKey(BuildingResource, 'building')
        
    class Meta:
        queryset = Room.objects.all()
        resource_name = 'rooms'
        allowed_methods = ['get']

        filtering = {
            'building': ('exact',),
            }


class FacultyResource(ModelResource):
    university = fields.ForeignKey(UniversityResource, 'university')
    departments = fields.ToManyField(
        'timetable_jan.university.api.DepartmentResource',
        'departments', 'faculty', null=True)
    majors = fields.ToManyField(
        'timetable_jan.university.api.MajorResource',
        'majors', 'faculty', null=True)

    class Meta:
        queryset = Faculty.objects.all()
        resource_name = 'faculties'
        allowed_methods = ['get']

        filtering = {
            'university': ('exact',),
            }

        
class DepartmentResource(ModelResource):
    faculty = fields.ForeignKey(FacultyResource, 'faculty')
    disciplines = fields.ToManyField(
        'timetable_jan.university.api.DisciplineResource',
        'disciplines', 'department', null=True)

    class Meta:
        queryset = Department.objects.all()
        resource_name = 'departments'
        allowed_methods = ['get']

        filtering = {
            'faculty': ('exact',),
            }


class MajorResource(ModelResource):
    faculty = fields.ForeignKey(FacultyResource, 'faculty')

    class Meta:
        queryset = Major.objects.all()
        resource_name = 'majors'
        allowed_methods = ['get']

        filtering = {
            'faculty': ('exact',),
            }


class DisciplineResource(ModelResource):
    department = fields.ForeignKey(DepartmentResource, 'department')
    courses = fields.ToManyField(
        'timetable_jan.university.api.CourseResource',
        'courses', 'discipline', null=True)

    class Meta:
        queryset = Discipline.objects.all()
        resource_name = 'disciplines'
        allowed_methods = ['get']

        filtering = {
            'department': ('exact',),
            }


class CourseResource(ModelResource):
    discipline = fields.ForeignKey(DisciplineResource, 'discipline')
    term = fields.ForeignKey(AcademicTermResource, 'academic_term')
    
    class Meta:
        queryset = Course.objects.all()
        resource_name = 'courses'
        allowed_methods = ['get']

        filtering = {
            'discipline': ('exact',),
            'academic_term': ('exact',),
            }


#------------------------ API links ----------------------------------
v1_api = Api(api_name='v1')
v1_api.register(UniversityResource())
v1_api.register(AcademicTermResource())
v1_api.register(BuildingResource())
v1_api.register(RoomResource())
v1_api.register(FacultyResource())
v1_api.register(DepartmentResource())
v1_api.register(MajorResource())
v1_api.register(DisciplineResource())
v1_api.register(CourseResource())

urls = patterns('',
    (r'^', include(v1_api.urls)),
)
