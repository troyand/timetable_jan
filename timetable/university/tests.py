"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.db import IntegrityError
from timetable.university.models import *


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class TestStudentEnrollment(TestCase):
    fixtures = ['test_timetable_dataset.xml']

    def setUp(self):
        # save group objects for easy retrieval in test cases
        self.phy_0, self.mat_0, self.mat_1, self.mat_2 = Group.objects.select_related().all()
        self.student = Student.objects.create(
            full_name='John Doe',
            major=Major.objects.all()[0]
        )

    def test_lesson_enrollment_phy_lecture(self):
        """Test that a student can enroll to a separate lesson"""
        lesson = self.phy_0.lesson_set.all()[0]
        self.student.enroll(lesson)
        self.assertEqual(
            set([lesson]),
            set(self.student.lessons())
        )

    def test_group_enrollment_phy_lectures(self):
        """Test that individual StudentLessonSubscription objects are created
        when a student enrolls to a group (should be triggerred by signal)"""
        self.student.enroll(self.phy_0)
        self.assertEqual(
            set(self.phy_0.lesson_set.all()),
            set(self.student.lessons())
        )

    def test_group_enrollment_multiple_groups(self):
        """Test to verify that a student may enroll to multiple groups"""
        groups = [self.phy_0, self.mat_0, self.mat_1]
        for group in groups:
            self.student.enroll(group)
        self.assertEqual(
            set([l for g in groups for l in g.lesson_set.all()]),
            set(self.student.lessons())
        )

    def test_group_and_lesson_enrollment_mat(self):
        """Test to verify that a student may enroll both to group and
        single lesson"""
        self.student.enroll(self.mat_0)
        self.student.enroll(self.mat_1.lesson_set.all()[0])
        self.assertEqual(
            set(list(self.mat_0.lesson_set.all()) +
                [self.mat_1.lesson_set.all()[0]]),
            set(self.student.lessons())
        )

    def test_group_enrollment_double_save(self):
        """Test that saving existing StudentGroupMembership does not
        trigger unnecessary processing"""
        self.student.enroll(self.phy_0)
        sgm = StudentGroupMembership.objects.get()
        # here no exception should be raised
        sgm.save()
        self.assertEqual(
            set(self.phy_0.lesson_set.all()),
            set(self.student.lessons())
        )

    def test_lesson_enrollment_twice(self):
        """Test that enrolling twice to the same lesson raises
        IntegrityError"""
        lesson = self.phy_0.lesson_set.all()[0]
        self.student.enroll(lesson)
        self.assertRaises(
            IntegrityError,
            self.student.enroll,
            lesson
        )

    def test_group_enrollment_twice(self):
        """Test that enrolling twice to the same group raises
        IntegrityError"""
        self.student.enroll(self.phy_0)
        self.assertRaises(
            IntegrityError,
            self.student.enroll,
            self.phy_0
        )

    def test_group_enrollment_lesson_addition(self):
        """Test that a lesson added to a group that has students
        enrolled apears in their lesson list"""
        self.student.enroll(self.phy_0)
        lesson = self.phy_0.lesson_set.all()[0]
        new_lesson = Lesson.objects.create(
            group=lesson.group,
            room=lesson.room,
            date=lesson.date,
            lesson_number=lesson.lesson_number + 1,
        )
        self.assertEqual(
            set(self.phy_0.lesson_set.all()),
            set(self.student.lessons())
        )

    def test_lesson_group_enrollment_override(self):
        """Test that enrolling for individual lesson
        that was in group series breaks the group link"""
        self.student.enroll(self.phy_0)
        self.student.enroll(self.phy_0.lesson_set.all()[0])
        self.assertEqual(
            set(self.phy_0.lesson_set.all()),
            set(self.student.lessons())
        )

    def test_lesson_unenrollment_phy_lecture(self):
        """Test that a student can unenroll from a separate lesson"""
        lesson = self.phy_0.lesson_set.all()[0]
        self.student.enroll(lesson)
        self.assertEqual(
            set([lesson]),
            set(self.student.lessons())
        )
        self.student.unenroll(lesson)
        self.assertEqual(
            set(),
            set(self.student.lessons())
        )

    def test_group_unenrollment_phy_lectures(self):
        """Test that individual StudentLessonSubscription objects are deleted
        when a student unenrolls from a group (should be triggerred by cascade
        DB delete)"""
        self.student.enroll(self.phy_0)
        self.assertEqual(
            set(self.phy_0.lesson_set.all()),
            set(self.student.lessons())
        )
        self.student.unenroll(self.phy_0)
        self.assertEqual(
            set(),
            set(self.student.lessons())
        )

    def test_group_and_lesson_unenrollment_mat(self):
        """Test to verify that a student may unenroll both from a group and
        from a single lesson"""
        self.student.enroll(self.mat_0)
        self.student.enroll(self.mat_1.lesson_set.all()[0])
        self.assertEqual(
            set(list(self.mat_0.lesson_set.all()) +
                [self.mat_1.lesson_set.all()[0]]),
            set(self.student.lessons())
        )
        self.student.unenroll(self.mat_0)
        self.assertEqual(
            set([self.mat_1.lesson_set.all()[0]]),
            set(self.student.lessons())
        )
        self.student.unenroll(self.mat_1.lesson_set.all()[0])
        self.assertEqual(
            set(),
            set(self.student.lessons())
        )

    def test_lesson_group_unenrollment_override(self):
        """Test that enrolling for individual lesson
        that was in group series breaks the group link
        and unenrollment from group does not delete the
        overriden lesson"""
        self.student.enroll(self.phy_0)
        lesson = self.phy_0.lesson_set.all()[0]
        self.student.enroll(lesson)
        self.student.unenroll(self.phy_0)
        self.assertEqual(
            set([lesson]),
            set(self.student.lessons())
        )
