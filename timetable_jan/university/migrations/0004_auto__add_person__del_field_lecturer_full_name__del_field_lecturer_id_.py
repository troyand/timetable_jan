# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Person'
        db.create_table('university_person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('university', ['Person'])

        # Deleting field 'Lecturer.id'
        db.delete_column('university_lecturer', 'id')

        # Adding field 'Lecturer.person_ptr'
        db.add_column('university_lecturer', 'person_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=1, to=orm['university.Person'], unique=True, primary_key=True),
                      keep_default=False)

        # Deleting field 'Lecturer.full_name'
        db.delete_column('university_lecturer', 'full_name')

        # Deleting field 'Student.id'
        db.delete_column('university_student', 'id')

        # Deleting field 'Student.full_name'
        db.delete_column('university_student', 'full_name')

        # Adding field 'Student.person_ptr'
        db.add_column('university_student', 'person_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=1, to=orm['university.Person'], unique=True, primary_key=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting model 'Person'
        db.delete_table('university_person')


        # User chose to not deal with backwards NULL issues for 'Lecturer.full_name'
        raise RuntimeError("Cannot reverse this migration. 'Lecturer.full_name' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Lecturer.id'
        raise RuntimeError("Cannot reverse this migration. 'Lecturer.id' and its values cannot be restored.")
        # Deleting field 'Lecturer.person_ptr'
        db.delete_column('university_lecturer', 'person_ptr_id')


        # User chose to not deal with backwards NULL issues for 'Student.id'
        raise RuntimeError("Cannot reverse this migration. 'Student.id' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Student.full_name'
        raise RuntimeError("Cannot reverse this migration. 'Student.full_name' and its values cannot be restored.")
        # Deleting field 'Student.person_ptr'
        db.delete_column('university_student', 'person_ptr_id')

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
            'Meta': {'object_name': 'Lecturer', '_ormbases': ['university.Person']},
            'departments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['university.Department']", 'symmetrical': 'False'}),
            'person_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['university.Person']", 'unique': 'True', 'primary_key': 'True'})
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
        'university.person': {
            'Meta': {'object_name': 'Person'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'Meta': {'object_name': 'Student', '_ormbases': ['university.Person']},
            'major': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['university.Major']"}),
            'person_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['university.Person']", 'unique': 'True', 'primary_key': 'True'})
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
