#-*- coding: utf-8 -*-

from django.core.management import setup_environ
from timetable_jan import settings

setup_environ(settings)


from timetable_jan.university.models import *
print AcademicTerm.objects.get_or_create(
        university=University.objects.get(abbr=u'НаУКМА'),
        year=2011,
        kind=u'семестр',
        season=u'літній',
        number_of_weeks=6,
        tcp_week=None,
        start_date='2012-04-15',
        exams_start_date='2012-05-27',
        exams_end_date='2012-06-07',
        ).pk
