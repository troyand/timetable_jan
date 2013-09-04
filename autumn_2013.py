#-*- coding: utf-8 -*-

from django.core.management import setup_environ
from timetable import settings
import sys

setup_environ(settings)


from timetable.university.models import *
academic_term, created = AcademicTerm.objects.get_or_create(
        university=University.objects.get(abbr=u'НаУКМА'),
        year=2013,
        kind=u'семестр',
        season=u'осінній',
        number_of_weeks=15,
        tcp_week=8,
        start_date='2013-09-02',
        exams_start_date='2013-12-16',
        exams_end_date='2012-12-29',
        )
print academic_term.pk

