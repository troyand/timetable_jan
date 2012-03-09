from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.core import serializers
from difflib import unified_diff


class Change(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    changer = models.ForeignKey(User, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    diff = models.TextField()


class Auditable(object):
    #changes = generic.GenericRelation(Change)
    def changes(self):
        content_type = ContentType.objects.get_for_model(self)
        return Change.objects.filter(
                content_type__pk=content_type.id,
                object_id=self.id)


    def save(self, *args, **kwargs):
        change = Change()
        try:
            change.changer = kwargs.pop('changer')
        except KeyError:
            change.changer = None
        serialized = serializers.serialize('xml', [self], indent=2)
        if self.pk:
            old_self = self._base_manager.get(pk=self.pk)
            old_serialized = serializers.serialize('xml', [old_self], indent=2)
        else:
            # if the object is new, then the previous state is treated as empty
            old_serialized = ''
        diff = '\n'.join(unified_diff(
            old_serialized.splitlines(),
            serialized.splitlines(),
            ))
        change.diff = diff
        super(Auditable, self).save(*args, **kwargs)
        change.content_object=self
        change.save()
