import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_hooks.models import Hook

from .models import Invite, Rating


class APITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.adminclient = APIClient()


class AuthenticatedAPITestCase(APITestCase):

    def make_invite(self, identity="210ac8c7-1f23-46af-a186-2468c89f7cc1"):
        data = {
            "identity": identity,
            "invite": {
                "to_addr": "+27123",
                "content": "Please dial *120*1234# and rate our service",
                "metadata": {}
            },
            "created_by": self.user,
            "updated_by": self.user
        }
        return Invite.objects.create(**data)

    def make_rating(self, invite,
                    identity="210ac8c7-1f23-46af-a186-2468c89f7cc1",
                    version=1, question_id=1,
                    question_text="What is the moon made from",
                    answer_text="Cheese", answer_value="cheese"):
        data = {
            "identity": identity,
            "invite": invite,
            "version": version,
            "question_id": question_id,
            "question_text": question_text,
            "answer_text": answer_text,
            "answer_value": answer_value,
            "created_by": self.user,
            "updated_by": self.user
        }
        return Rating.objects.create(**data)

    def setUp(self):
        super(AuthenticatedAPITestCase, self).setUp()
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(self.username,
                                             'testuser@example.com',
                                             self.password)
        token = Token.objects.create(user=self.user)
        self.token = token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # Admin User setup
        self.adminusername = 'testadminuser'
        self.adminpassword = 'testadminpass'
        self.adminuser = User.objects.create_superuser(
            self.adminusername,
            'testadminuser@example.com',
            self.adminpassword)
        admintoken = Token.objects.create(user=self.adminuser)
        self.admintoken = admintoken.key
        self.adminclient.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admintoken)


class TestRatingApp(AuthenticatedAPITestCase):

    def test_login(self):
        request = self.client.post(
            '/api/token-auth/',
            {"username": "testuser", "password": "testpass"})
        token = request.data.get('token', None)
        self.assertIsNotNone(
            token, "Could not receive authentication token on login post.")
        self.assertEqual(request.status_code, 200,
                         "Status code on /api/token-auth was %s -should be 200"
                         % request.status_code)

    # Test Invite API
    def test_create_invite(self):
        post_data = {
            "identity": "210ac8c7-1f23-46af-a186-2468c89f7cc1",
            "invite": {
                "to_addr": "+27123",
                "content": "Please dial *120*1234# and rate our service",
                "metadata": {}
            }
        }
        response = self.client.post('/api/v1/invite/',
                                    json.dumps(post_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Invite.objects.last()
        self.assertEqual(d.identity, '210ac8c7-1f23-46af-a186-2468c89f7cc1')
        self.assertEqual(d.invite, {
            "to_addr": "+27123",
            "content": "Please dial *120*1234# and rate our service",
            "metadata": {}
        })
        self.assertEqual(d.invited, False)
        self.assertEqual(d.completed, False)
        self.assertEqual(d.expired, False)
        self.assertEqual(d.version, 1)
        self.assertEqual(d.expires_at, None)
        self.assertEqual(d.created_by, self.user)
        self.assertEqual(d.updated_by, self.user)

    def test_get_invite_list(self):
        # Setup
        self.make_invite(
            identity="210ac8c7-1f23-46af-a186-2468c89f7cc1")
        self.make_invite(
            identity="ea7069c7-6e6d-48fd-a839-d41b13d3a54a")
        self.make_invite(
            identity="48630fb3-862d-4974-8e69-ac3ee7b0e88e")

        # Execute
        response = self.client.get('/api/v1/invite/',
                                   content_type='application/json')
        results = response.json()

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results["count"], 3)
        self.assertEqual(len(results["results"]), 3)

    def test_get_invite_list_filtered(self):
        # Setup
        self.make_invite(
            identity="210ac8c7-1f23-46af-a186-2468c89f7cc1")
        self.make_invite(
            identity="ea7069c7-6e6d-48fd-a839-d41b13d3a54a")
        self.make_invite(
            identity="48630fb3-862d-4974-8e69-ac3ee7b0e88e")

        # Execute
        response = self.client.get(
            '/api/v1/invite/',
            {'identity': "210ac8c7-1f23-46af-a186-2468c89f7cc1"},
            content_type='application/json')
        results = response.json()

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results["count"], 1)
        self.assertEqual(len(results["results"]), 1)

    def test_get_invite_list_filtered_completed(self):
        # Setup
        invite = self.make_invite(
            identity="210ac8c7-1f23-46af-a186-2468c89f7cc1")
        invite.completed = True
        invite.save()
        self.make_invite(
            identity="210ac8c7-1f23-46af-a186-2468c89f7cc1")
        self.make_invite(
            identity="ea7069c7-6e6d-48fd-a839-d41b13d3a54a")
        self.make_invite(
            identity="48630fb3-862d-4974-8e69-ac3ee7b0e88e")

        # Execute
        response = self.client.get(
            '/api/v1/invite/',
            {'identity': "210ac8c7-1f23-46af-a186-2468c89f7cc1",
             'completed': False},
            content_type='application/json')
        results = response.json()

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results["count"], 1)
        self.assertEqual(len(results["results"]), 1)

    def test_update_invite(self):
        # Setup
        invite = self.make_invite()
        self.assertEqual(invite.invited, False)
        self.assertEqual(invite.completed, False)
        patch_data = {
            "invited": True
        }
        # Execute
        # use adminclient to make the patch request
        response = self.adminclient.patch('/api/v1/invite/%s/' % invite.id,
                                          json.dumps(patch_data),
                                          content_type='application/json')
        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invite.refresh_from_db()
        self.assertEqual(invite.invited, True)
        self.assertEqual(invite.completed, False)
        self.assertEqual(invite.created_by, self.user)
        self.assertEqual(invite.updated_by, self.adminuser)

    def test_delete_invite(self):
        # Setup
        invite = self.make_invite()
        self.assertEqual(Invite.objects.all().count(), 1)
        # Execute
        response = self.client.delete('/api/v1/invite/%s/' % invite.id,
                                      content_type='application/json')
        # Check
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Invite.objects.all().count(), 0)

    # Test Rating API
    def test_create_rating(self):
        invite = self.make_invite()
        post_data = {
            "identity": "210ac8c7-1f23-46af-a186-2468c89f7cc1",
            "invite": str(invite.id),
            "version": 1,
            "question_id": 1,
            "question_text": "What is the moon made from?",
            "answer_text": "Cheese",
            "answer_value": "cheese"
        }
        response = self.client.post('/api/v1/rating/',
                                    json.dumps(post_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Rating.objects.last()
        self.assertEqual(d.identity, '210ac8c7-1f23-46af-a186-2468c89f7cc1')
        self.assertEqual(d.invite, invite)
        self.assertEqual(d.version, 1)
        self.assertEqual(d.question_id, 1)
        self.assertEqual(d.question_text, "What is the moon made from?")
        self.assertEqual(d.answer_text, "Cheese")
        self.assertEqual(d.answer_value, "cheese")
        self.assertEqual(d.created_by, self.user)
        self.assertEqual(d.updated_by, self.user)

    def test_get_rating(self):
        # Setup
        invite = self.make_invite()
        rating = self.make_rating(invite)
        # Execute
        response = self.client.get('/api/v1/rating/%s/' % str(rating.id),
                                   content_type='application/json')
        result = response.json()
        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result["id"], str(rating.id))
        self.assertEqual(result["invite"], str(invite.id))

    def test_get_rating_list(self):
        # Setup
        invite = self.make_invite()
        self.make_rating(invite)
        self.make_rating(invite, question_id=2,
                         question_text="What jumped over the moon?",
                         answer_text="A cow", answer_value="cow")
        # Execute
        response = self.client.get('/api/v1/rating/',
                                   content_type='application/json')
        results = response.json()

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results["count"], 2)
        self.assertEqual(len(results["results"]), 2)

    def test_get_rating_list_filtered(self):
        # Setup
        invite = self.make_invite()
        self.make_rating(invite)
        self.make_rating(invite, question_id=2,
                         question_text="What jumped over the moon?",
                         answer_text="A cow", answer_value="cow")
        self.make_rating(invite, question_id=2,
                         question_text="What jumped over the moon?",
                         answer_text="A cricket", answer_value="cricket")
        self.make_rating(invite, question_id=3,
                         question_text="What reclines on the moon?",
                         answer_text="A rabbit", answer_value="rabbit")
        # Execute
        response = self.client.get('/api/v1/rating/',
                                   {"question_id": 2},
                                   content_type='application/json')
        results = response.json()

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results["count"], 2)
        self.assertEqual(len(results["results"]), 2)
        self.assertEqual(Rating.objects.all().count(), 4)

    def test_update_rating(self):
        # Setup
        invite = self.make_invite()
        rating = self.make_rating(invite)
        self.assertEqual(rating.answer_text, "Cheese")
        self.assertEqual(rating.answer_value, "cheese")
        patch_data = {
            "answer_text": "Swiss Cheese"
        }
        # Execute
        # use adminclient to make the request
        response = self.adminclient.patch('/api/v1/rating/%s/' % rating.id,
                                          json.dumps(patch_data),
                                          content_type='application/json')
        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rating.refresh_from_db()
        self.assertEqual(rating.answer_text, "Swiss Cheese")
        self.assertEqual(rating.answer_value, "cheese")
        self.assertEqual(rating.created_by, self.user)
        self.assertEqual(rating.updated_by, self.adminuser)

    def test_delete_rating(self):
        # Setup
        invite = self.make_invite()
        rating = self.make_rating(invite)
        self.assertEqual(Invite.objects.all().count(), 1)
        self.assertEqual(Rating.objects.all().count(), 1)
        # Execute
        response = self.client.delete('/api/v1/rating/%s/' % rating.id,
                                      content_type='application/json')
        # Check
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Invite.objects.all().count(), 1)
        self.assertEqual(Rating.objects.all().count(), 0)

    # Test webhook
    def test_create_webhook(self):
        # Setup
        user = User.objects.get(username='testadminuser')
        post_data = {
            "target": "http://example.com/invite/",
            "event": "invite.added"
        }
        # Execute
        response = self.adminclient.post('/api/v1/webhook/',
                                         json.dumps(post_data),
                                         content_type='application/json')
        # Check
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        d = Hook.objects.last()
        self.assertEqual(d.target, 'http://example.com/invite/')
        self.assertEqual(d.user, user)


class TestUserCreation(AuthenticatedAPITestCase):

    def test_create_user_and_token(self):
        # Setup
        user_request = {"email": "test@example.org"}
        # Execute
        request = self.adminclient.post('/api/v1/user/token/', user_request)
        token = request.json().get('token', None)
        # Check
        self.assertIsNotNone(
            token, "Could not receive authentication token on post.")
        self.assertEqual(
            request.status_code, 201,
            "Status code on /api/v1/user/token/ was %s (should be 201)."
            % request.status_code)

    def test_create_user_and_token_fail_nonadmin(self):
        # Setup
        user_request = {"email": "test@example.org"}
        # Execute
        request = self.client.post('/api/v1/user/token/', user_request)
        error = request.json().get('detail', None)
        # Check
        self.assertIsNotNone(
            error, "Could not receive error on post.")
        self.assertEqual(
            error, "You do not have permission to perform this action.",
            "Error message was unexpected: %s."
            % error)

    def test_create_user_and_token_not_created(self):
        # Setup
        user_request = {"email": "test@example.org"}
        # Execute
        request = self.adminclient.post('/api/v1/user/token/', user_request)
        token = request.json().get('token', None)
        # And again, to get the same token
        request2 = self.adminclient.post('/api/v1/user/token/', user_request)
        token2 = request2.json().get('token', None)

        # Check
        self.assertEqual(
            token, token2,
            "Tokens are not equal, should be the same as not recreated.")

    def test_create_user_new_token_nonadmin(self):
        # Setup
        user_request = {"email": "test@example.org"}
        request = self.adminclient.post('/api/v1/user/token/', user_request)
        token = request.json().get('token', None)
        cleanclient = APIClient()
        cleanclient.credentials(HTTP_AUTHORIZATION='Token %s' % token)
        # Execute
        request = cleanclient.post('/api/v1/user/token/', user_request)
        error = request.json().get('detail', None)
        # Check
        # new user should not be admin
        self.assertIsNotNone(
            error, "Could not receive error on post.")
        self.assertEqual(
            error, "You do not have permission to perform this action.",
            "Error message was unexpected: %s."
            % error)


class TestHealthcheckAPI(AuthenticatedAPITestCase):

    def test_healthcheck_read(self):
        # Setup
        # Execute
        response = self.client.get('/api/health/',
                                   content_type='application/json')
        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["up"], True)
        self.assertEqual(response.data["result"]["database"], "Accessible")
