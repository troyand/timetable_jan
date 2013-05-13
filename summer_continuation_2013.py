#-*- coding: utf-8 -*-

from django.core.management import setup_environ
from timetable import settings

setup_environ(settings)


from timetable.university.models import *
academic_term, created = AcademicTerm.objects.get_or_create(
        university=University.objects.get(abbr=u'НаУКМА'),
        year=2012,
        kind=u'семестр',
        season=u'літній',
        number_of_weeks=7,
        tcp_week=None,
        start_date='2013-05-13',
        exams_start_date='2013-06-23',
        exams_end_date='2013-06-27',
        )
print academic_term.pk
