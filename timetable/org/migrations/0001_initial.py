# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'OrgUnit'
        db.create_table('org_orgunit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['org.OrgUnit'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('entity', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('org', ['OrgUnit'])

        # Adding unique constraint on 'OrgUnit', fields ['parent', 'name']
        db.create_unique('org_orgunit', ['parent_id', 'name'])

    def backwards(self, orm):
        # Removing unique constraint on 'OrgUnit', fields ['parent', 'name']
        db.delete_unique('org_orgunit', ['parent_id', 'name'])

        # Deleting model 'OrgUnit'
        db.delete_table('org_orgunit')

    models = {
        'org.orgunit': {
            'Meta': {'unique_together': "(('parent', 'name'),)", 'object_name': 'OrgUnit'},
            'entity': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['org.OrgUnit']", 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['org']