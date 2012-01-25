from django.views.generic.list import BaseListView
from django.http import HttpResponse, HttpResponseForbidden
from timetable_jan.university.models import *
from django.utils.datastructures import MultiValueDictKeyError
import json


class AjaxAutocompleteMixin(object):
    def autocomplete_response(self, query):
        '''implementation should return json response'''
        raise NotImplementedError
    def get(self, request):
        try:
            return self.autocomplete_response(request.GET['query'])
        except MultiValueDictKeyError:
            return HttpResponseForbidden('Forbidden')


class RoomAutocompleteView(AjaxAutocompleteMixin, BaseListView):
    model = Room
    def autocomplete_response(self, query):
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
    def autocomplete_response(self, query):
        lecturers = [(l.full_name, l.pk) for l in Lecturer.objects.filter(full_name__icontains=query)]
        json_response = {
                'query': query,
                'suggestions': [name for name, pk in lecturers],
                'data': [pk for name, pk in lecturers],
                }
        return HttpResponse(
                json.dumps(json_response)
                )
