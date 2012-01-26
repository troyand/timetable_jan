from django.views.generic.list import BaseListView
from django.http import HttpResponse, HttpResponseForbidden
from timetable_jan.university.models import *
from django.utils.datastructures import MultiValueDictKeyError
import json


class AjaxAutocompleteMixin(object):
    def autocomplete_response(self, query):
        '''implementation should return json response
        in a more effective way (e.g. via icontains)'''
        query_upper = query.upper()
        object_unicode_pk_pairs = [
                (unicode(o), o.pk) for o in self.model.objects.select_related().all()]
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
