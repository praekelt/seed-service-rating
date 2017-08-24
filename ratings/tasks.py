import json
import requests
import datetime

from celery.task import Task
from celery.utils.log import get_task_logger
from django.conf import settings
from seed_services_client import (
    IdentityStoreApiClient,
    MessageSenderApiClient,
)

from .models import Invite


ms_client = MessageSenderApiClient(
    api_url=settings.MESSAGE_SENDER_URL,
    auth_token=settings.MESSAGE_SENDER_TOKEN
)

identity_store_client = IdentityStoreApiClient(
    api_url=settings.IDENTITY_STORE_URL,
    auth_token=settings.IDENTITY_STORE_TOKEN,
)


def get_identity_address(identity_uuid):
    return identity_store_client.get_identity_address(identity_uuid)


class SendInviteMessages(Task):
    """ Task that finds invite messages that should be sent and
    creates subtasks to send each of these messages
    """
    name = "seed_service_rating.ratings.tasks.send_invite_messages"
    l = get_task_logger(__name__)

    def run(self, **kwargs):
        self.l = self.get_logger(**kwargs)
        msgs_to_send = Invite.objects.filter(
            completed=False, expired=False,
            invites_sent__lt=settings.TOTAL_INVITES_TO_SEND,
            send_after__lt=datetime.datetime.now(),
        )
        for msg in msgs_to_send:
            send_invite_message.apply_async(args=[msg.id])

        return "%s Invites queued for sending" % len(msgs_to_send)


send_invite_messages = SendInviteMessages()


class SendInviteMessage(Task):
    """ Task to send a servicerating invitation message
    """
    name = "seed_service_rating.ratings.tasks.send_invite_message"
    l = get_task_logger(__name__)

    def compile_msg_payload(self, invite):
        """ Determine recipient, message content, return it as
        a dict that can be Posted to the message sender
        """
        self.l.info("Compiling the outbound message payload")
        update_invite = False

        # Determine the recipient address
        if "to_addr" in invite.invite:
            to_addr = invite.invite["to_addr"]
        else:
            update_invite = True
            to_addr = get_identity_address(invite.identity)

        # Determine the message content
        if "content" in invite.invite:
            content = invite.invite["content"]
        else:
            update_invite = True
            content = settings.INVITE_TEXT

        # Determine the metadata
        if "metadata" in invite.invite:
            metadata = invite.invite["metadata"]
        else:
            update_invite = True
            metadata = {}

        msg_payload = {
            "to_addr": to_addr,
            "content": content,
            "metadata": metadata
        }

        if update_invite is True:
            self.l.info("Updating the invite.invite field")
            invite.invite = msg_payload
            invite.save()

        self.l.info("Compiled the outbound message payload")
        return msg_payload

    def send_message(self, payload):
        """ Create a post request to the message sender
        """
        self.l.info("Creating outbound message request")
        result = ms_client.create_outbound(payload)
        self.l.info("Created outbound message request")
        return result

    def run(self, invite_id, **kwargs):
        """ Sends a message about service rating to invitee
        """
        self.l = self.get_logger(**kwargs)
        self.l.info("Looking up the invite")
        invite = Invite.objects.get(id=invite_id)
        msg_payload = self.compile_msg_payload(invite)
        result = self.send_message(msg_payload)
        self.l.info("Creating task to update invite after send")
        post_send_update_invite.apply_async(args=[invite_id])
        self.l.info("Created task to update invite after send")
        return "Message queued for send. ID: <%s>" % str(result["id"])


send_invite_message = SendInviteMessage()


class PostSendUpdateInvite(Task):
    """ Task that updates the necessary fields after sending
    an invite message
    """
    name = "seed_service_rating.ratings.tasks.post_send_update_invite"
    l = get_task_logger(__name__)

    def run(self, invite_id, **kwargs):
        self.l = self.get_logger(**kwargs)
        self.l.info("Looking up invite %s" % invite_id)
        invite = Invite.objects.get(id=invite_id)
        self.l.info("Updating the Invite")
        invite.invites_sent += 1
        invite.invited = True
        invite.send_after = invite.send_after + datetime.timedelta(
            days=settings.DAYS_BETWEEN_INVITES)
        invite.save()
        self.l.info("Updated the Invite")
        return "Updated Invite %s" % invite_id


post_send_update_invite = PostSendUpdateInvite()


class DeliverHook(Task):
    def run(self, target, payload, instance_id=None, hook_id=None, **kwargs):
        """
        target:     the url to receive the payload.
        payload:    a python primitive data structure
        instance_id:   a possibly None "trigger" instance ID
        hook_id:       the ID of defining Hook object
        """
        requests.post(
            url=target,
            data=json.dumps(payload),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Token %s' % settings.HOOK_AUTH_TOKEN
            }
        )


def deliver_hook_wrapper(target, payload, instance, hook):
    if instance is not None:
        instance_id = instance.id
    else:
        instance_id = None
    kwargs = dict(target=target, payload=payload,
                  instance_id=instance_id, hook_id=hook.id)
    DeliverHook.apply_async(kwargs=kwargs)
