from django.forms import ModelForm
from timetable_jan.university.models import *

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('email', )


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ('major', )
