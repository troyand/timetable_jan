# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'University'
        db.create_table('university_university', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('abbr', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
        ))
        db.send_create_signal('university', ['University'])

        # Adding model 'AcademicTerm'
        db.create_table('university_academicterm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.University'])),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('season', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('number_of_weeks', self.gf('django.db.models.fields.IntegerField')()),
            ('tcp_week', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('exams_start_date', self.gf('django.db.models.fields.DateField')()),
            ('exams_end_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('university', ['AcademicTerm'])

        # Adding model 'Building'
        db.create_table('university_building', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.University'])),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('university', ['Building'])

        # Adding unique constraint on 'Building', fields ['university', 'number', 'label']
        db.create_unique('university_building', ['university_id', 'number', 'label'])

        # Adding model 'Room'
        db.create_table('university_room', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Building'])),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('floor', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('university', ['Room'])

        # Adding unique constraint on 'Room', fields ['building', 'number', 'label']
        db.create_unique('university_room', ['building_id', 'number', 'label'])

        # Adding model 'Faculty'
        db.create_table('university_faculty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.University'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('abbr', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('university', ['Faculty'])

        # Adding unique constraint on 'Faculty', fields ['university', 'name']
        db.create_unique('university_faculty', ['university_id', 'name'])

        # Adding unique constraint on 'Faculty', fields ['university', 'abbr']
        db.create_unique('university_faculty', ['university_id', 'abbr'])

        # Adding model 'Department'
        db.create_table('university_department', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('faculty', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Faculty'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('university', ['Department'])

        # Adding unique constraint on 'Department', fields ['faculty', 'name']
        db.create_unique('university_department', ['faculty_id', 'name'])

        # Adding model 'Major'
        db.create_table('university_major', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('faculty', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Faculty'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('university', ['Major'])

        # Adding unique constraint on 'Major', fields ['faculty', 'name', 'kind']
        db.create_unique('university_major', ['faculty_id', 'name', 'kind'])

        # Adding model 'Lecturer'
        db.create_table('university_lecturer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('university', ['Lecturer'])

        # Adding M2M table for field departments on 'Lecturer'
        db.create_table('university_lecturer_departments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('lecturer', models.ForeignKey(orm['university.lecturer'], null=False)),
            ('department', models.ForeignKey(orm['university.department'], null=False))
        ))
        db.create_unique('university_lecturer_departments', ['lecturer_id', 'department_id'])

        # Adding model 'Discipline'
        db.create_table('university_discipline', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Department'], null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('university', ['Discipline'])

        # Adding unique constraint on 'Discipline', fields ['department', 'code']
        db.create_unique('university_discipline', ['department_id', 'code'])

        # Adding model 'Course'
        db.create_table('university_course', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('discipline', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Discipline'])),
            ('academic_term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.AcademicTerm'])),
        ))
        db.send_create_signal('university', ['Course'])

        # Adding model 'Timetable'
        db.create_table('university_timetable', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('major', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Major'])),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('university', ['Timetable'])

        # Adding M2M table for field courses on 'Timetable'
        db.create_table('university_timetable_courses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('timetable', models.ForeignKey(orm['university.timetable'], null=False)),
            ('course', models.ForeignKey(orm['university.course'], null=False))
        ))
        db.create_unique('university_timetable_courses', ['timetable_id', 'course_id'])

        # Adding model 'Group'
        db.create_table('university_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Course'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('lecturer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Lecturer'])),
        ))
        db.send_create_signal('university', ['Group'])

        # Adding model 'GroupMembership'
        db.create_table('university_groupmembership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Group'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('university', ['GroupMembership'])

        # Adding model 'Lesson'
        db.create_table('university_lesson', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Group'])),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Room'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('lesson_number', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('university', ['Lesson'])

        # Adding unique constraint on 'Lesson', fields ['room', 'date', 'lesson_number']
        db.create_unique('university_lesson', ['room_id', 'date', 'lesson_number'])

    def backwards(self, orm):
        # Removing unique constraint on 'Lesson', fields ['room', 'date', 'lesson_number']
        db.delete_unique('university_lesson', ['room_id', 'date', 'lesson_number'])

        # Removing unique constraint on 'Discipline', fields ['department', 'code']
        db.delete_unique('university_discipline', ['department_id', 'code'])

        # Removing unique constraint on 'Major', fields ['faculty', 'name', 'kind']
        db.delete_unique('university_major', ['faculty_id', 'name', 'kind'])

        # Removing unique constraint on 'Department', fields ['faculty', 'name']
        db.delete_unique('university_department', ['faculty_id', 'name'])

        # Removing unique constraint on 'Faculty', fields ['university', 'abbr']
        db.delete_unique('university_faculty', ['university_id', 'abbr'])

        # Removing unique constraint on 'Faculty', fields ['university', 'name']
        db.delete_unique('university_faculty', ['university_id', 'name'])

        # Removing unique constraint on 'Room', fields ['building', 'number', 'label']
        db.delete_unique('university_room', ['building_id', 'number', 'label'])

        # Removing unique constraint on 'Building', fields ['university', 'number', 'label']
        db.delete_unique('university_building', ['university_id', 'number', 'label'])

        # Deleting model 'University'
        db.delete_table('university_university')

        # Deleting model 'AcademicTerm'
        db.delete_table('university_academicterm')

        # Deleting model 'Building'
        db.delete_table('university_building')

        # Deleting model 'Room'
        db.delete_table('university_room')

        # Deleting model 'Faculty'
        db.delete_table('university_faculty')

        # Deleting model 'Department'
        db.delete_table('university_department')

        # Deleting model 'Major'
        db.delete_table('university_major')

        # Deleting model 'Lecturer'
        db.delete_table('university_lecturer')

        # Removing M2M table for field departments on 'Lecturer'
        db.delete_table('university_lecturer_departments')

        # Deleting model 'Discipline'
        db.delete_table('university_discipline')

        # Deleting model 'Course'
        db.delete_table('university_course')

        # Deleting model 'Timetable'
        db.delete_table('university_timetable')

        # Removing M2M table for field courses on 'Timetable'
        db.delete_table('university_timetable_courses')

        # Deleting model 'Group'
        db.delete_table('university_group')

        # Deleting model 'GroupMembership'
        db.delete_table('university_groupmembership')

        # Deleting model 'Lesson'
        db.delete_table('university_lesson')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'university.academicterm': {
            'Meta': {'object_name': 'AcademicTerm'},
            'exams_end_date': ('django.db.models.fields.DateField', [], {}),
            'exams_start_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'number_of_weeks': ('django.db.models.fields.IntegerField', [], {}),
            'season': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'tcp_week': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.University']"}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'university.building': {
            'Meta': {'unique_together': "(('university', 'number', 'label'),)", 'object_name': 'Building'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.University']"})
        },
        'university.course': {
            'Meta': {'object_name': 'Course'},
            'academic_term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.AcademicTerm']"}),
            'discipline': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Discipline']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'university.department': {
            'Meta': {'unique_together': "(('faculty', 'name'),)", 'object_name': 'Department'},
            'faculty': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Faculty']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'university.discipline': {
            'Meta': {'unique_together': "(('department', 'code'),)", 'object_name': 'Discipline'},
            'code': ('django.db.models.fields.IntegerField', [], {}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Department']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'university.faculty': {
            'Meta': {'unique_together': "(('university', 'name'), ('university', 'abbr'))", 'object_name': 'Faculty'},
            'abbr': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.University']"})
        },
        'university.group': {
            'Meta': {'object_name': 'Group'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lecturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Lecturer']"}),
            'number': ('django.db.models.fields.IntegerField', [], {})
        },
        'university.groupmembership': {
            'Meta': {'object_name': 'GroupMembership'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'university.lecturer': {
            'Meta': {'object_name': 'Lecturer'},
            'departments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['university.Department']", 'symmetrical': 'False'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'university.lesson': {
            'Meta': {'unique_together': "(('room', 'date', 'lesson_number'),)", 'object_name': 'Lesson'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lesson_number': ('django.db.models.fields.IntegerField', [], {}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Room']"})
        },
        'university.major': {
            'Meta': {'unique_together': "(('faculty', 'name', 'kind'),)", 'object_name': 'Major'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'faculty': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Faculty']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'university.room': {
            'Meta': {'unique_together': "(('building', 'number', 'label'),)", 'object_name': 'Room'},
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Building']"}),
            'floor': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'university.timetable': {
            'Meta': {'object_name': 'Timetable'},
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['university.Course']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'major': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Major']"}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'university.university': {
            'Meta': {'object_name': 'University'},
            'abbr': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['university']