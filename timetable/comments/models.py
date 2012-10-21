from django.db import models
from django.contrib.auth.models import User
from timetable.university.models import Lesson
import datetime


# Create your models here.

class LessonComment(models.Model):
    lesson = models.ForeignKey(Lesson)
    author = models.ForeignKey(User, blank=True, null=True)
    ip = models.IPAddressField(db_index=True)
    added = models.DateTimeField(default=datetime.datetime.now)
    comment = models.TextField()

    def ip_two_octets(self):
        return '.'.join(self.ip.split('.')[-2:])
