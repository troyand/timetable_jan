# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'GroupMembership'
        db.delete_table('university_groupmembership')

        # Adding model 'Student'
        db.create_table('university_student', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('university', ['Student'])

        # Adding model 'StudentLessonSubscription'
        db.create_table('university_studentlessonsubscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Student'])),
            ('lesson', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Lesson'])),
            ('via_group_membership', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.StudentGroupMembership'], null=True, blank=True)),
        ))
        db.send_create_signal('university', ['StudentLessonSubscription'])

        # Adding unique constraint on 'StudentLessonSubscription', fields ['student', 'lesson']
        db.create_unique('university_studentlessonsubscription', ['student_id', 'lesson_id'])

        # Adding model 'StudentGroupMembership'
        db.create_table('university_studentgroupmembership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Student'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Group'])),
        ))
        db.send_create_signal('university', ['StudentGroupMembership'])

        # Adding unique constraint on 'StudentGroupMembership', fields ['student', 'group']
        db.create_unique('university_studentgroupmembership', ['student_id', 'group_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'StudentGroupMembership', fields ['student', 'group']
        db.delete_unique('university_studentgroupmembership', ['student_id', 'group_id'])

        # Removing unique constraint on 'StudentLessonSubscription', fields ['student', 'lesson']
        db.delete_unique('university_studentlessonsubscription', ['student_id', 'lesson_id'])

        # Adding model 'GroupMembership'
        db.create_table('university_groupmembership', (
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['university.Group'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('university', ['GroupMembership'])

        # Deleting model 'Student'
        db.delete_table('university_student')

        # Deleting model 'StudentLessonSubscription'
        db.delete_table('university_studentlessonsubscription')

        # Deleting model 'StudentGroupMembership'
        db.delete_table('university_studentgroupmembership')

    models = {
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
        'university.student': {
            'Meta': {'object_name': 'Student'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'university.studentgroupmembership': {
            'Meta': {'unique_together': "(('student', 'group'),)", 'object_name': 'StudentGroupMembership'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Student']"})
        },
        'university.studentlessonsubscription': {
            'Meta': {'unique_together': "(('student', 'lesson'),)", 'object_name': 'StudentLessonSubscription'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lesson': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Lesson']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Student']"}),
            'via_group_membership': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.StudentGroupMembership']", 'null': 'True', 'blank': 'True'})
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