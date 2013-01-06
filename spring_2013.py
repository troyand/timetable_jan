#-*- coding: utf-8 -*-

from django.core.management import setup_environ
from timetable import settings
import sys

setup_environ(settings)


from timetable.university.models import *
if sys.argv[1] == 'long':
    academic_term, created = AcademicTerm.objects.get_or_create(
            university=University.objects.get(abbr=u'НаУКМА'),
            year=2012,
            kind=u'семестр',
            season=u'весняний',
            number_of_weeks=15,
            tcp_week=8,
            start_date='2013-01-14',
            exams_start_date='2013-04-29',
            exams_end_date='2012-05-10',
            )
if sys.argv[1] == 'short':
    academic_term, created = AcademicTerm.objects.get_or_create(
            university=University.objects.get(abbr=u'НаУКМА'),
            year=2012,
            kind=u'семестр',
            season=u'осінній',
            number_of_weeks=11,
            tcp_week=None,
            start_date='2013-01-07',
            exams_start_date='2013-03-25',
            exams_end_date='2013-04-5',
            )
print academic_term.pk

