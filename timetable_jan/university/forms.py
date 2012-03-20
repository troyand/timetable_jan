#-*- coding: utf-8 -*-

from django.forms import ModelForm, Form, CharField, Textarea
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
            required=False,
            label=u'Що найбільше сподобалось'
            )
    disliked = CharField(
            widget=Textarea,
            max_length=5000,
            required=False,
            label=u'Що найбільше не сподобалось'
            )
    wouldliked = CharField(
            widget=Textarea,
            max_length=5000,
            required=False,
            label=u'Чого найбільше не вистачало'
            )
