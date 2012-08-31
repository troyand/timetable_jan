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
            season=u'осінній',
            number_of_weeks=15,
            tcp_week=8,
            start_date='2012-09-03',
            exams_start_date='2012-12-17',
            exams_end_date='2012-12-30',
            )
if sys.argv[1] == 'short':
    academic_term, created = AcademicTerm.objects.get_or_create(
            university=University.objects.get(abbr=u'НаУКМА'),
            year=2012,
            kind=u'семестр',
            season=u'осінній',
            number_of_weeks=14,
            tcp_week=8,
            start_date='2012-09-03',
            exams_start_date='2012-12-10',
            exams_end_date='2012-12-23',
            )
print academic_term.pk

