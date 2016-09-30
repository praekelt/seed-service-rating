import uuid

from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Invite(models.Model):

    """
    An invitation for Rating
    invite should be in a format suitable for posting to the message sender
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identity = models.CharField(max_length=36, null=False, blank=False)
    version = models.IntegerField(default=1)
    invited = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)
    invite = JSONField(null=True, blank=True)
    invites_sent = models.IntegerField(default=0)
    send_after = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='invites_created',
                                   null=True)
    updated_by = models.ForeignKey(User, related_name='invites_updated',
                                   null=True)
    user = property(lambda self: self.created_by)

    def serialize_hook(self, hook):
        # optional, there are serialization defaults
        # we recommend always sending the Hook
        # metadata along for the ride as well
        return {
            'hook': hook.dict(),
            'data': {
                'id': str(self.id),
                'identity': self.identity,
                'version': self.version,
                'invited': self.invited,
                'completed': self.completed,
                'expired': self.expired,
                'invite': self.invite,
                'expires_at': self.expires_at,
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            }
        }

    def __str__(self):  # __unicode__ on Python 2
        return "Invite for rating version %s to identity %s" % (
            self.version, self.identity)


@python_2_unicode_compatible
class Rating(models.Model):

    """
    Feedback provided by service rating respondee
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identity = models.CharField(max_length=36, null=False, blank=False)
    invite = models.ForeignKey(Invite, related_name='ratings_feedback',
                               null=True)
    version = models.IntegerField(default=1)
    question_id = models.IntegerField()
    question_text = models.CharField(max_length=255)
    answer_text = models.CharField(max_length=255)
    answer_value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='ratings_created',
                                   null=True)
    updated_by = models.ForeignKey(User, related_name='ratings_updated',
                                   null=True)
    user = property(lambda self: self.created_by)

    def serialize_hook(self, hook):
        # optional, there are serialization defaults
        # we recommend always sending the Hook
        # metadata along for the ride as well
        return {
            'hook': hook.dict(),
            'data': {
                'id': str(self.id),
                'identity': self.identity,
                'invite': self.invite,
                'version': self.version,
                'question_id': self.question_id,
                'question_text': self.question_text,
                'answer_text': self.answer_text,
                'answer_value': self.answer_value,
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            }
        }

    def __str__(self):  # __unicode__ on Python 2
        return "Rating for question %s for identity %s" % (
            self.question_id, self.identity)
