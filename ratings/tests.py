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
            }
        }
        return Invite.objects.create(**data)

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

    def test_create_invite_model_data(self):
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

    def test_read_invite_list_model_data(self):
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

    def test_read_invite_list_filtered_model_data(self):
        # Setup
        self.make_invite(
            identity="210ac8c7-1f23-46af-a186-2468c89f7cc1")
        self.make_invite(
            identity="ea7069c7-6e6d-48fd-a839-d41b13d3a54a")
        self.make_invite(
            identity="48630fb3-862d-4974-8e69-ac3ee7b0e88e")

        # Execute
        response = self.client.get('/api/v1/invite/?identity=%s' % (
            "210ac8c7-1f23-46af-a186-2468c89f7cc1",),
            content_type='application/json')
        results = response.json()

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results["count"], 1)
        self.assertEqual(len(results["results"]), 1)

    def test_read_invite_list_filtered_completed_model_data(self):
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
            "/api/v1/invite/?identity=%s&completed=False" % (
                "210ac8c7-1f23-46af-a186-2468c89f7cc1",),
            content_type='application/json')
        results = response.json()

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results["count"], 1)
        self.assertEqual(len(results["results"]), 1)

    def test_create_rating_model_data(self):
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
