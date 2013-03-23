#-*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
import datetime
from django.db.models.signals import post_save
from django_auth_ldap.backend import populate_user, populate_user_profile
from django.dispatch import receiver

import logging
logger = logging.getLogger(__name__)

lesson_times = {
    1: (u'8:30', u'9:50'),
    2: (u'10:00', u'11:20'),
    3: (u'11:40', u'13:00'),
    4: (u'13:30', u'14:50'),
    5: (u'15:00', u'16:20'),
    6: (u'16:30', u'17:50'),
    7: (u'18:00', u'19:20')
}

day_names = {
        1: u'Пн',
        2: u'Вт',
        3: u'Ср',
        4: u'Чт',
        5: u'Пт',
        6: u'Сб',
        7: u'Нд',
        }



class University(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbr = models.CharField(max_length=16, unique=True)

    def __unicode__(self):
        return u'%s' % (
            self.abbr
        )


class AcademicTerm(models.Model):
    ACADEMIC_TERMS = (
        (u'семестр', u'семестр'),
        (u'триместр', u'триместр'),
    )
    SEASONS = (
        (u'осінній', u'осінній'),
        (u'весняний', u'весняний'),
        (u'літній', u'літній'),
    )

    class Week:
        def __init__(self, academic_term, week_number):
            if week_number < 0 or week_number > academic_term.number_of_weeks:
                raise ValueError(u'Invalid week number %d for %s' % (
                    week_number, academic_term)
                    )
            self.academic_term = academic_term
            self.week_number = week_number

        def __getitem__(self, key):
            if type(key) == type(1):
                return self.academic_term.start_date + datetime.timedelta(
                    days=7 * (self.week_number - 1) + key)
            else:
                raise AttributeError('Int expected, got %s' % key)

        def __repr__(self):
            return smart_str(
                u'Week #%d of %s' % (
                    self.week_number,
                    self.academic_term
                ))
    university = models.ForeignKey(University)
    year = models.IntegerField()
    kind = models.CharField(max_length=16, choices=ACADEMIC_TERMS)
    season = models.CharField(max_length=16, choices=SEASONS)
    number_of_weeks = models.IntegerField()
    tcp_week = models.IntegerField(null=True, blank=True)
    start_date = models.DateField()
    exams_start_date = models.DateField()
    exams_end_date = models.DateField()

    def __unicode__(self):
        return u'%s: %s %s %d-%d навчального року (%d т. із %s)' % (
            self.university,
            self.season,
            self.kind,
            self.year,
            self.year + 1,
            self.number_of_weeks,
            self.start_date,
        )

    def __getitem__(self, key):
        """Week getter, at[5][2] gets the wednesday of 5th week"""
        if type(key) == type(1):
            return self.Week(academic_term=self, week_number=key)
        else:
            raise AttributeError('Int expected, got %s' % key)

    def get_week(self, date):
        """Get the Week object corresponding to the given date"""
        delta = date - self.start_date
        week_number = delta.days / 7 + 1
        if 0 < week_number <= self.number_of_weeks:
            return self.Week(academic_term=self, week_number=week_number)
        else:
            raise ValueError('There is no week #%d in %s' % (
                week_number,
                self,
            ))


class Building(models.Model):
    university = models.ForeignKey(University)
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


class Room(models.Model):
    building = models.ForeignKey(Building)
    number = models.IntegerField(null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    floor = models.IntegerField()

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


class Faculty(models.Model):
    university = models.ForeignKey(University)
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


class Department(models.Model):
    faculty = models.ForeignKey(Faculty)
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('faculty', 'name')

    def __unicode__(self):
        return self.name


class Major(models.Model):
    faculty = models.ForeignKey(Faculty)
    code = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    kind = models.CharField(max_length=16)

    class Meta:
        unique_together = ('faculty', 'name', 'kind')

    def __unicode__(self):
        return u'%s - %s' % (
            self.code,
            self.name,
        )


#TODO finish this class
class Person(models.Model):
    """Represents generic person"""
    user = models.OneToOneField(User, null=True, blank=True)
    full_name = models.CharField(max_length=255)

    #class Meta:
    #    abstract = True

    def __unicode__(self):
        return self.full_name

    def short_name(self):
        parts = self.full_name.split(' ')
        result = parts[0]
        if len(parts) > 1:
            result += ' '
            for p in parts[1:]:
                if len(p) > 0:
                    result += '%s. ' % p[0]
        return result

    def surname(self):
        return self.full_name.split(' ')[0]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        p = Person(user=instance)
        p.save()


@receiver(populate_user)
def ldap_sync(user, ldap_user, **kwargs):
    user.first_name = ldap_user.attrs['givenName'][0]
    user.last_name = ldap_user.attrs['sn'][0]


@receiver(populate_user_profile)
def ldap_sync_profile(profile, ldap_user, **kwargs):
    ldap_major_mapping = {
        # TODO add other majors from
        # http://wiki.usic.org.ua/wiki/UMS_utilities
        u'40203': u'6.040203',
        u'50103': u'6.050103',
    }
    person = profile
    person.full_name = ldap_user.attrs['cn'][0]
    ldap_profession = ldap_user.attrs['profession'][0]
    try:
        if ldap_profession in [u'0', u'1']:
            # the user is a Student
            student = Student(person_ptr=person)
            ldap_faculty = ldap_user.attrs['faculty'][0]
            if ldap_faculty in ldap_major_mapping.keys():
                student.major = Major.objects.get(
                    code=ldap_major_mapping[ldap_faculty]
                )
            student.save()
    except Exception, e:
        logging.error(e)


class Student(Person):
    """Represents student that can enroll to courses"""
    major = models.ForeignKey(Major)

    def __unicode__(self):
        return self.full_name

    def enroll(self, target):
        if isinstance(target, Group):
            StudentGroupMembership.objects.create(
                student=self,
                group=target,
            )
        elif isinstance(target, Lesson):
            try:
                sls = StudentLessonSubscription.objects.get(
                    student=self,
                    lesson=target,
                    via_group_membership__isnull=False
                )
                sls.via_group_membership = None
                sls.save()
            except StudentLessonSubscription.DoesNotExist:
                StudentLessonSubscription.objects.create(
                    student=self,
                    lesson=target,
                )
        else:
            raise NotImplementedError(
                'Enroll is not implemented for %s %s' % (
                    type(target), target
                ))

    def unenroll(self, target):
        if isinstance(target, Group):
            StudentGroupMembership.objects.get(
                student=self,
                group=target,
            ).delete()
        elif isinstance(target, Lesson):
            StudentLessonSubscription.objects.get(
                student=self,
                lesson=target,
            ).delete()
        else:
            raise NotImplementedError(
                'Unenroll is not implemented for %s %s' % (
                    type(target), target
                ))

    def lessons(self, q_filter=None):
        """q_filter - Q object to provide additional
        filtering condtions"""
        lesson_subscriptions = StudentLessonSubscription.objects.select_related(
                ).filter(student=self)
        if q_filter:
            lesson_subscriptions = lesson_subscriptions.filter(q_filter)
        return [ls.lesson for ls in lesson_subscriptions]


class Lecturer(Person):
    departments = models.ManyToManyField(Department)

    def __unicode__(self):
        return self.full_name


class Discipline(models.Model):
    department = models.ForeignKey(Department, null=True, blank=True)
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
                [word[0].upper() for word in self.name.split(' ')
                 if len(word) > 2])

    def __unicode__(self):
        return '%s (%d)' % (
            self.name,
            self.code
        )


class Course(models.Model):
    discipline = models.ForeignKey(Discipline)
    academic_term = models.ForeignKey(AcademicTerm)

    def abbr(self):
        return self.discipline.abbr()

    def __unicode__(self):
        return u'%s' % (
            self.discipline,
        )

    def full_description(self):
        timetables = self.timetable_set.select_related('major__faculty').all()
        together_with = u','.join(set([u'%s-%d' % (t.major.name,
                                               t.year)
                                   for t in timetables]))
        return u'%s (%s)' % (
            self.discipline.name,
            #self.academic_term.season,
            #self.academic_term.kind,
            #self.academic_term.year,
            #self.academic_term.year + 1,
            together_with
        )



class Timetable(models.Model):
    major = models.ForeignKey(Major)
    year = models.IntegerField()
    courses = models.ManyToManyField(Course)
    academic_term = models.ForeignKey(AcademicTerm)

    def __unicode__(self):
        return u'%s %s %d р.н.' % (
                self.major.name,
                self.major.kind,
                self.year,
                )


class Group(models.Model):
    course = models.ForeignKey(Course)
    number = models.IntegerField()  # group #0 for lectures
    lecturer = models.ForeignKey(Lecturer)

    def __unicode__(self):
        return u'%s-%d' % (
            self.course.abbr(),
            self.number,
        )


class StudentGroupMembership(models.Model):
    student = models.ForeignKey(Student)
    group = models.ForeignKey(Group)

    class Meta:
        unique_together = ('student', 'group')


@receiver(post_save, sender=StudentGroupMembership)
def student_group_membership_post_save(sender, instance, created,
                                       raw, using, **kwargs):
    if created:
        for lesson in instance.group.lesson_set.all():
            StudentLessonSubscription.objects.create(
                student=instance.student,
                lesson=lesson,
                via_group_membership=instance)

# delete is handled with cascade DB deletion of related objects


class Lesson(models.Model):
    group = models.ForeignKey(Group)
    room = models.ForeignKey(Room, null=True, blank=True, verbose_name=u'аудиторія')
    date = models.DateField(verbose_name=u'дата')
    lesson_number = models.IntegerField(verbose_name=u'номер пари')

    #class Meta:
    #    unique_together = ('room', 'date', 'lesson_number')

    def __unicode__(self):
        return '%s %d %s - %d' % (
            self.date,
            self.lesson_number,
            self.group.course.discipline.name,
            self.group.number,
        )

    def notify_subscribers(self, changer):
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import get_template
        from django.template import Context
        old_self = Lesson.objects.get(pk=self.pk)
        print changer
        changeset = []
        for field in Lesson._meta.fields:
            field_name = field.name
            field_verbose_name = field.verbose_name
            old_value = old_self.__getattribute__(field_name)
            new_value = self.__getattribute__(field_name)
            if old_value != new_value:
                changeset.append((field_verbose_name, old_value, new_value))
        if changeset:
            context = Context({
                'changer': changer,
                'changeset': changeset,
                'lesson': old_self,
            })
            plaintext_template = get_template(
                'notifications/lesson_update.txt')
            plaintext_message = plaintext_template.render(context)
            for sls in StudentLessonSubscription.objects.select_related().filter(lesson=old_self):
                user = sls.student.user
                if user.email:
                    user.email_user(
                        u'Зміни у розкладі',
                        plaintext_message,
                        from_email=u'Розклад <noreply@universitytimetable.org.ua>'
                    )

    def icalendar_event(self):
        import icalendar
        import pytz
        lesson_start_time, lesson_end_time = lesson_times[self.lesson_number]
        lesson_start_hour, lesson_start_minute = map(int,
                                                     lesson_start_time.split(':'))
        lesson_end_hour, lesson_end_minute = map(int,
                                                 lesson_end_time.split(':'))
        tz = pytz.timezone('Europe/Kiev')
        dtstart = datetime.datetime.combine(self.date, datetime.time(
            lesson_start_hour,
            lesson_start_minute,
            tzinfo=tz))
        dtend = datetime.datetime.combine(self.date, datetime.time(
            lesson_end_hour,
            lesson_end_minute,
            tzinfo=tz))
        event = icalendar.Event()
        if self.group.number != 0:
            summary_str = u'%s (група %d)' % (
                self.group.course.discipline.name,
                self.group.number,
            )
        else:
            summary_str = u'%s (лекція)' % self.group.course.discipline.name
        event.add('summary', summary_str)
        event.add('description', u'Викладач: %s' % self.group.lecturer.short_name())
        if self.room:
            event.add('location', unicode(self.room))
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)
        event['uid'] = 'lesson-%d@universitytimetable.org.ua' % self.id
        return event


@receiver(post_save, sender=Lesson)
def lesson_post_save(sender, instance, created, raw, using, **kwargs):
    if created:
        for sgm in StudentGroupMembership.objects.filter(group=instance.group):
            StudentLessonSubscription.objects.create(
                student=sgm.student,
                lesson=instance,
                via_group_membership=sgm)


class StudentLessonSubscription(models.Model):
    student = models.ForeignKey(Student)
    lesson = models.ForeignKey(Lesson)
    # remember the group membership that caused this object to be created
    # for easy deletion later.
    # Single lesson subscriptions have this field to None
    via_group_membership = models.ForeignKey(
        StudentGroupMembership, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'lesson')
