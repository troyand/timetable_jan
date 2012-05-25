#-*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from django.contrib.auth.models import User as UserModel
from django.contrib.auth.models import Group as GroupModel
import datetime

lesson_times = {
        0: (u'8:30', u'9:50'),
        1: (u'10:00', u'11:20'),
        2: (u'11:40', u'13:00'),
        3: (u'13:30', u'14:50'),
        4: (u'15:00', u'16:20'),
        5: (u'16:30', u'17:50'),
        6: (u'18:00', u'19:20')
        }


class UniversityModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbr = models.CharField(max_length=16, unique=True)
    
    def __unicode__(self):
        return u'%s' % (
                self.abbr
                )

class BuildingModel(models.Model):
    university = models.ForeignKey(UniversityModel)
    number = models.IntegerField(null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('university', 'number', 'label')

    def __unicode__(self):
        if self.number:
            number_part = u'#%d' % self.number
        else:
            number_part = u''
        if self.label:
            label_part = self.label
        else:
            label_part = u''
        return u' - '.join([
                self.university.abbr,
                number_part,
                label_part,
                ])

class RoomModel(models.Model):
    building = models.ForeignKey(BuildingModel)
    number = models.IntegerField()
    label = models.CharField(max_length=255, null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('building', 'number', 'label')
        ordering = ['building__number', 'number']

    def __unicode__(self):
        #Idendification of room itself
        if self.number:
            room_part = u'%d' % self.number
        else:
            room_part = u''
        if self.label:
            room_part += self.label
        else:
            room_part += u''
        #Identification of building
        if self.building.number is not None:
            building_part = u'%d' % self.building.number
            if self.building.label:
                building_part += u'%d' % self.building.label
        elif self.building.label:
            building_part = self.building.label
        else:
            building_part = u''
        return u'-'.join([
                building_part,
                room_part,
                ])

class FacultyModel(models.Model):
    university = models.ForeignKey(UniversityModel)
    name = models.CharField(max_length=255)
    abbr = models.CharField(max_length=16)
    
    class Meta:
        unique_together = (
                ('university', 'name'),
                ('university', 'abbr'),
                )

    def __unicode__(self):
        return '%s - %s' % (
                self.university.abbr,
                self.abbr,
                )

class DepartmentModel(models.Model):
    faculty = models.ForeignKey(FacultyModel)
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('faculty', 'name')

    def __unicode__(self):
        return self.name

class LecturerModel(models.Model):
    lecturer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    department = models.ManyToManyField(DepartmentModel, null=True, blank=True)
    def __unicode__(self):
        return self.name

    def short_name(self):
        parts = self.name.split(' ')
        result = parts[0]
        if len(parts) > 1:
            result += ' '
            for p in parts[1:]:
                if len(p) > 0:
                    result += '%s. ' % p[0]
        return result
    
    def surname(self):
        return self.full_name.split(' ')[0]

class DisciplineModel(models.Model):
    discipline_id = models.AutoField(primary_key=True)
    department = models.ForeignKey(DepartmentModel, null=True, blank=True)
    code = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('department', 'code')

    def abbr(self):
        if u'.NET' in self.name:
            return '.NET'
        else:
            return ''.join(
                    [word[0].upper() for word in self.name.split(' ') if len(word) > 2])

    def __unicode__(self):
        return self.name

class TimeTableModel(models.Model):
    time = models.DateTimeField()
    lecturer = models.ForeignKey(LecturerModel)
    location = models.ForeignKey(RoomModel)
    discipline = models.ForeignKey(DisciplineModel)
    academic_group = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        return u'%s %s %s %s' % (self.time, self.location,
                                self.discipline.name, self.lecturer.name
                                )
class UserProfile(models.Model):
    user = models.OneToOneField(UserModel)
    lessons = models.ManyToManyField(TimeTableModel)

class GroupProfile(models.Model):
    group = models.OneToOneField(GroupModel)
    is_public = models.NullBooleanField()
    lessons = models.ManyToManyField(TimeTableModel)
