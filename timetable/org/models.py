from django.db import models
from django.utils.translation import ugettext as _
from timetable.university.models import *


class OrgUnit(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=64, blank=True, null=True)
    entity = models.CharField(max_length=64, choices=(
        ('university', _('university')),
        ('faculty', _('faculty')),
        ('department', _('department')),
        ))

    class Meta:
        unique_together = ('parent', 'name')

    def __unicode__(self):
        if self.parent:
            return u'%s - %s' % (self.parent, self.short_name or self.name)
        else:
            return self.short_name or self.name


class EntityManager(models.Manager):
    def __init__(self, entity):
        self.entity = entity
        return super(EntityManager, self).__init__()

    def get_query_set(self):
        return super(EntityManager, self).get_query_set().filter(
                entity=self.entity)


class University(OrgUnit):
    objects = EntityManager('university')

    def save(self, *args, **kwargs):
        self.entity = 'university'
        super(University, self).save(*args, **kwargs)

    class Meta:
        proxy = True


class Faculty(OrgUnit):
    objects = EntityManager('faculty')

    def save(self, *args, **kwargs):
        self.entity = 'faculty'
        super(Faculty, self).save(*args, **kwargs)

    class Meta:
        proxy = True


class Department(OrgUnit):
    objects = EntityManager('department')

    def save(self, *args, **kwargs):
        self.entity = 'department'
        super(Department, self).save(*args, **kwargs)

    class Meta:
        proxy = True
