from django.views.generic import DetailView, CreateView, DeleteView, UpdateView, FormView
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from timetable.university.models import *
from timetable.university.forms import *
from django.core.mail import send_mail


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)


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
        print self.object  # unsaved/uncommitted object
        self.object.notify_subscribers(self.user)
        return super(LessonDetailView, self).form_valid(form)

    def get_success_url(self):
        return self.request.path


class FeedbackView(FormView):
    form_class = FeedbackForm

    def form_valid(self, form):
        send_mail(
            'Feedback',
            'Sent from %s\n\nLiked:\n%s\n\nDisliked:\n%s\n\nWouldliked:\n%s' %
            (
                'https://beta.universitytimetable.org.ua/feedback/\n' + '=' * 40,
                form.cleaned_data['liked'],
                form.cleaned_data['disliked'],
                form.cleaned_data['wouldliked'],
            ),
            'Timetable <noreply@universitytimetable.org.ua>',
            ['web-dev@mail.usic.ukma.kiev.ua', 'troyanovsky@gmail.com'],
            fail_silently=True
        )
        return super(FeedbackView, self).form_valid(form)

    def get_success_url(self):
        return '/'


class CourseCreateView(FormView):
    form_class = CourseForm
    #model = Course
    context_object_name = 'course'

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super(CourseCreateView, self).get_context_data(**kwargs)
        context['form'].fields['timetables'].queryset = Timetable.objects.filter(
                academic_term__pk=4
                )
        print context
        return context

