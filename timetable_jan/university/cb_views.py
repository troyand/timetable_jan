from django.views.generic import DetailView, CreateView, DeleteView, UpdateView, FormView
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from timetable_jan.university.models import *
from timetable_jan.university.forms import *


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)



class LessonDetailView(LoginRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    context_object_name = "lesson"

    #def get(self, request, *args, **kwargs):
    #    return super(LessonDetailView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.user = request.user
        return super(LessonDetailView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        # check if user has permission to edit lesson
        #if self.object not in self.user.get_profile().student.lessons():
        #    return HttpResponseForbidden('Forbidden')
        if not self.object.can_edit(self.user):
            return HttpResponseForbidden('Forbidden')
        print self.object # unsaved/uncommitted object
        self.object.notify_subscribers(self.user)
        return super(LessonDetailView, self).form_valid(form)

    def get_success_url(self):
        return self.request.path
