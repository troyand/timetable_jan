#-*- coding: utf-8 -*-

from django.views.generic.list import BaseListView
from django.views.generic import TemplateView, FormView
from django.http import HttpResponse, HttpResponseForbidden
from timetable_jan.university.models import *
from django.utils.datastructures import MultiValueDictKeyError
from django import forms
import json


class AjaxAutocompleteMixin(object):
    def unicode_format_object(self, o):
        return unicode(o)
    def autocomplete_response(self, query):
        '''implementation should return json response
        in a more effective way (e.g. via icontains)'''
        query_upper = query.upper()
        object_unicode_pk_pairs = [
                (self.unicode_format_object(o), o.pk) for o in self.model.objects.select_related().all()]
        objects = filter(
                lambda o: o[0].upper().startswith(query_upper), object_unicode_pk_pairs)
        json_response = {
                'query': query,
                'suggestions': [u for u, pk in objects],
                'data': [pk for u, pk in objects],
                }
        return HttpResponse(
                json.dumps(json_response)
                )
    def get(self, request):
        try:
            return self.autocomplete_response(request.GET['query'])
        except MultiValueDictKeyError:
            return HttpResponseForbidden('Forbidden')


class UnifiedTimetableProcessView(FormView):
    class CSVUploadForm(forms.Form):
        csv_file  = forms.FileField()
    form_class = CSVUploadForm

    def get_context_data(self, **kwargs):
        context = super(UnifiedTimetableProcessView, self).get_context_data(**kwargs)
        try:
            context['table'] = self.table
        except:
            context['table'] = []
        context['days'] = [u'ПН', u'ВТ', u'СР', u'ЧТ', u'ПТ', u'СБ']
        context['times'] = [u'08:30-09:50', u'10:00-11:20', u'11:40-13:00', u'13:30-14:50',
            u'15:00-16:20', u'16:30-17:50', u'18:00-19:20']
        return context


    def post(self, request):
        import csv
        def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
            # csv.py doesn't do Unicode; encode temporarily as UTF-8:
            csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                                    dialect=dialect, **kwargs)
            for row in csv_reader:
                # decode UTF-8 back to Unicode, cell by cell:
                yield [unicode(cell, 'utf-8') for cell in row]

        def utf_8_encoder(unicode_csv_data):
            for line in unicode_csv_data:
                yield line.encode('utf-8')

        try:
            csv_contents = request.FILES['csv_file']
            table = []
            for line in csv.reader(csv_contents):
                table.append([e.decode('utf-8') for e in line])
            self.table = table
        except MultiValueDictKeyError:
            #TODO there was not csv file attached, may be some display some error message
            pass
        return super(UnifiedTimetableProcessView, self).get(request)


class ExtraCoursesAutocompleteView(AjaxAutocompleteMixin, BaseListView):
    model = Course
    def autocomplete_response(self, query):
        query_upper = query.upper()
        unicode_course_pairs = [
                (unicode(course.discipline.name), course)
                for course in self.model.objects.select_related().all()]
        objects = filter(
                lambda course: query_upper in course[0].upper(), unicode_course_pairs)[:15]
        from django.template.loader import get_template
        from django.template import Context
        choose_course_groups = get_template('choose_course_groups.html')
        json_response = {
                'query': query,
                'suggestions': [u for u, c in objects],
                'data': [choose_course_groups.render(Context({
                    'course': c,
                    'groups': sorted(c.group_set.filter(number__gt=0), key=lambda g: g.number)
                    })) for u, c in objects],
                }
        return HttpResponse(
                json.dumps(json_response)
                )


class RoomAutocompleteView(AjaxAutocompleteMixin, BaseListView):
    model = Room
    def autocomplete_response_(self, query):
        room_name_pk_pairs = [(unicode(r), r.pk) for r in Room.objects.all()]
        rooms = filter(lambda x: x[0].startswith(query), room_name_pk_pairs)
        json_response = {
                'query': query,
                'suggestions': [name for name, pk in rooms],
                'data': [pk for name, pk in rooms],
                }
        return HttpResponse(
                json.dumps(json_response)
                )

class LecturerAutocompleteView(AjaxAutocompleteMixin, BaseListView):
    model = Lecturer
    def unicode_format_object(self, o):
        return o.short_name()
    def autocomplete_response_(self, query):
        lecturers = [(l.full_name, l.pk) for l in Lecturer.objects.filter(full_name__icontains=query)]
        json_response = {
                'query': query,
                'suggestions': [name for name, pk in lecturers],
                'data': [pk for name, pk in lecturers],
                }
        return HttpResponse(
                json.dumps(json_response)
                )

class DisciplineAutocompleteView(AjaxAutocompleteMixin, BaseListView):
    model = Discipline
    def unicode_format_object(self, o):
        return o.name
