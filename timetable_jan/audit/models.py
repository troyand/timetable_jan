from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ImproperlyConfigured
from difflib import unified_diff


class Change(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    changer = models.ForeignKey(User, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    before = models.TextField()
    after = models.TextField()

    def unified_diff(self):
        diff = '\n'.join(unified_diff(
            self.before.splitlines(),
            self.after.splitlines(),
            fromfile='before',
            tofile='after'
            ))
        return diff


class Auditable(object):
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
        if self.pk:
            old_self = self._base_manager.get(pk=self.pk)
            old_serialized = serializers.serialize('json', [old_self], indent=2)
        else:
            # if the object is new, then the previous state is treated as empty
            old_serialized = ''
        super(Auditable, self).save(*args, **kwargs)
        serialized = serializers.serialize('json', [self], indent=2)
        change.before = old_serialized
        change.after = serialized
        change.content_object = self
        change.save()


class Ownership(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    owner = models.ForeignKey(User)
    delegator = models.ForeignKey(User, blank=True, null=True, related_name='delegated')
    can_delegate = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['content_type', 'object_id', 'owner']


class AuthorizableBase(object):
    # investigate http://www.python.org/dev/peps/pep-3119/
    def can_add(self, user):
        return False

    def can_edit(self, user):
        return False

    def can_delete(self, user):
        return False


class Ownable(object):
    def ownerships(self):
        content_type = ContentType.objects.get_for_model(self)
        return Ownership.objects.filter(
                content_type__pk=content_type.id,
                object_id=self.id)

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                owner = kwargs.pop('owner')
            except KeyError:
                owner = None
        else:
            # for existing objects just pop owner arg
            # to make model save method happy
            # and set owner var to None
            kwargs.pop('owner')
            owner = None
        super(Ownable, self).save(*args, **kwargs)
        if owner:
            Ownership.objects.create(
                    content_object=self,
                    owner=owner,
                    can_delegate=True
                    )


class OwnableAuthorizableBase(AuthorizableBase):
    """Base class that provides can_edit check logic.
    By default it does not create ownership on save and
    does not accept owner argument in save method and
    only relies on the authorization_related list
    that contains the names of the attributes that
    may be checked to get permission"""
    # following list may be overriden for the list of related
    # objects that may provide permission for this object
    # e.g. group ownership may grant permissions for its lessons
    authorization_related = []
    def can_add(self, user):
        # by default anyone can add a new object
        return True

    def can_edit(self, user):
        if user in [o.owner for o in self.ownerships()]:
            return True
        else:
            try:
                for related in self.authorization_related:
                    result = self.__getattribute__(related).can_edit(user)
                    if result == True:
                        return True
            except AttributeError:
                raise
                #raise ImproperlyConfigured(
                #        'No %s attribute in %s' % (related, self)
                #        )
            return False

    def can_delete(self, user):
        return self.can_edit(user)


class StandaloneOwnableAuthorizable(Ownable, OwnableAuthorizableBase):
    """Implementation that creates Ownership on object creation"""
    pass

class RelatedOwnableAuthorizable(OwnableAuthorizableBase):
    def ownerships(self):
        return []
