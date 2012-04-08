#-*- coding: utf-8 -*-

from django.forms import ModelForm, Form, CharField, Textarea, ValidationError
from timetable_jan.university.models import *

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('email', )


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ('major', )

class LessonForm(ModelForm):
    class Meta:
        model = Lesson
        exclude = ('group', )

class FeedbackForm(Form):
    liked = CharField(
            widget=Textarea,
            max_length=5000,
            required=True,
            label=u'Що найбільше сподобалось'
            )
    disliked = CharField(
            widget=Textarea,
            max_length=5000,
            required=True,
            label=u'Що найбільше не сподобалось'
            )
    wouldliked = CharField(
            widget=Textarea,
            max_length=5000,
            required=True,
            label=u'Чого найбільше не вистачало'
            )
    def ensure_min_width(self, data):
        if len(data) < 10:
            raise ValidationError(u'Ви були не надто багатослівними')
    def clean_liked(self):
        return self.ensure_min_width(self.cleaned_data['liked'])
    def clean_disliked(self):
        return self.ensure_min_width(self.cleaned_data['disliked'])
    def clean_wouldliked(self):
        return self.ensure_min_width(self.cleaned_data['wouldliked'])
