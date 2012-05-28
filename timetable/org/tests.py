#-*- coding: utf-8 -*-
from django.test import TestCase
from timetable.org.models import *


class OrgUnitTestCase(TestCase):
    def setUp(self):
        self.university = University.objects.create(
                name=u'Національний університет «Києво-Могилянська академія»',
                short_name=u'НаУКМА',
                )
        self.faculty = Faculty.objects.create(
                parent=self.university,
                name=u'Факультет інформатики',
                short_name=u'ФІ',
                )
        self.department = Department.objects.create(
                parent=self.faculty,
                name=u'Кафедра мережних технологій',
                )

    def test_department_name(self):
        self.assertEqual(
                u'%s' % self.department,
                u'НаУКМА - ФІ - Кафедра мережних технологій'
                )

    def test_department_manager(self):
        self.assertEqual(
                Department.objects.get(),
                self.department
                )

    def test_sql(self):
        queryset = Department.objects.select_related().all()
        print queryset.query


    def tearDown(self):
        self.university.delete()
        self.faculty.delete()
        self.department.delete()
