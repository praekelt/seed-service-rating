===================
Seed Service Rating
===================

Service Rating is built around two models: Invites and Ratings.

If you want the user to rate the service they received, you first create an Invite for them. The user then gets sent a message to invite them to rate the service they received.

When the user rates the service they received, the feedback they provide is stored in Ratings. A Rating is created for each question they answered, and it stores the question and the answer in the model.

Invite creation typically happens via a POST request to the :code:`/invite` endpoint.

When a user has completed their service rating by answering all the questions, their Invite field :code:`completed` should be set to True to prevent sending additional invitations.

A special endpoint :code:`/invite/send` should be hit in order to send all the invites that need to go out. Hitting this endpoint activates the SendInviteMessages task, which in turn activates the task that sends out the individual invite messages. This can be automated by adding a schedule to the scheduler that hits the endpoint at predetermined times (typically it could hit the endpoint once every weekday)

Some environment variables to take note of (see settings.py):

* TOTAL_INVITES_TO_SEND: The number of messages that will be sent to invite users to rate their service.
* DAYS_BETWEEN_INVITES: The number of days to wait between sending invite messages to users.
* INVITE_TEXT: The invite message to be sent to the user.
