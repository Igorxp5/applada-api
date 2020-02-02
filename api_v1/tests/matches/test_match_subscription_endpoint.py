from api_v1.utils import TestCase
from api_v1.models import User, Match, MatchCategory

from django.conf import settings
from django.utils import timezone
from django.contrib.gis.geos import Point

from rest_framework.test import APIClient

import time
import unittest.mock as mock
from datetime import timedelta

URL_PREFFIX = '/v1'
DEFAULT_ENCODE = 'utf-8'


class MatchSubscriptionEndpointTestCase(TestCase):
    """Match Subscription Endpoint"""
    expected_structure = {
        'match_id': None,
        'user': {'username': None, 'name': None,
                 'level': None,'registred_date': None
        },
        'date': None
    }

    def setUp(self):
        self.client = APIClient()
    
    def test_not_authenticated_get_match(self):
        """GET /matches/{id}/subscriptions: Non-Authenticated request should return 401 response code and appropriate error message"""
        response = self.client.get(f'{URL_PREFFIX}/matches/1/subscriptions', follow=True)
        self.assertEquals(response.status_code, 401)
        self.assertJSONEqual(response, {'errors': ['Authentication credentials were not provided.']})
    
    def test_get_match_not_created(self):
        """GET /matches/{id}/subscriptions: Get a match that does not exist should return 404 response code and appropriate error message"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        response = self.client.get(f'{URL_PREFFIX}/matches/1/subscriptions', follow=True)
        self.assertEquals(response.status_code, 404)
        self.assertJSONEqual(response, {'errors':['Match not found']})

    def test_get_match_subscriptions(self):
        """GET /matches/{id}/subscriptions: Should return a pagination view containing Match subscriptions"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        test_match = self._create_test_match(owner=test_user)
        response = self.client.get(f'{URL_PREFFIX}/matches/{test_match.id}/subscriptions', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'count', 'next', 'previous', 'results'})
        self.assertEquals(len(response.json()['results']), 1)
        self.assertJSONContains(response.json()['results'][0], self.expected_structure)
    
    def test_subscribe_to_match(self):
        """POST /matches/{id}/subscriptions: Subscribe for the match"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        other_user = User.objects.create_user(username='other', email='other@gmail.com', password='1234')
        test_match = self._create_test_match(owner=other_user)
        response = self.client.post(f'{URL_PREFFIX}/matches/{test_match.id}/subscriptions', follow=True)
        self.assertEquals(response.status_code, 201)
        self.assertJSONContains(response, self.expected_structure)
    
    def test_cant_resubscribe_to_match(self):
        """POST /matches/{id}/subscriptions: User cannot subscribe twice in a match"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        other_user = User.objects.create_user(username='other', email='other@gmail.com', password='1234')
        test_match = self._create_test_match(owner=other_user)
        response = self.client.post(f'{URL_PREFFIX}/matches/{test_match.id}/subscriptions', follow=True)
        self.assertEquals(response.status_code, 201)
        self.assertJSONContains(response, self.expected_structure)
        response = self.client.post(f'{URL_PREFFIX}/matches/{test_match.id}/subscriptions', follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors':['You already registered in this match']})
    
    def test_cant_subscribe_in_finished_match(self):
        """POST /matches/{id}/subscriptions: User cannot subscribe for a finished match"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        other_user = User.objects.create_user(username='other', email='other@gmail.com', password='1234')

        testtime = timezone.now() - timedelta(days=1)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = testtime
            test_match = self._create_test_match(owner=other_user,
                                                 date=(timezone.now() + timedelta(hours=2)))
        response = self.client.post(f'{URL_PREFFIX}/matches/{test_match.id}/subscriptions', follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors':['You cannot subscribe for a finished match']})
    
    def test_unsubscribe_match(self):
        """DELETE /matches/{id}/subscriptions: User should be able to unsubscribe for a match"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        other_user = User.objects.create_user(username='other', email='other@gmail.com', password='1234')
        test_match = self._create_test_match(owner=other_user)
        response = self.client.post(f'{URL_PREFFIX}/matches/{test_match.id}/subscriptions', follow=True)
        self.assertEquals(response.status_code, 201)
        self.assertJSONContains(response, self.expected_structure)
        response = self.client.delete(f'{URL_PREFFIX}/matches/{test_match.id}/subscriptions', follow=True)
        self.assertEquals(response.status_code, 204)

    def test_cant_reunsubscribe_match(self):
        """DELETE /matches/{id}/subscriptions: User cannot unsubscribe for a match that he is not participating"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        other_user = User.objects.create_user(username='other', email='other@gmail.com', password='1234')
        test_match = self._create_test_match(owner=other_user)
        response = self.client.delete(f'{URL_PREFFIX}/matches/{test_match.id}/subscriptions', follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors':['You are not subscribed for this match']})

    def _create_test_user(self):
        return User.objects.create_user(username='whatever', email='whatever@gmail.com', password='1234')
    
    def _create_test_match(self, **kwargs):
        match_properties = {
            'title': kwargs.get('title', 'Match title'),
            'description': kwargs.get('description', 'a description'),
            'location': Point(kwargs.get('longitude', -34.944717), kwargs.get('latitude', -8.0651966)),
            'date': kwargs.get('date', timezone.now() + timedelta(days=5)),
            'duration': kwargs.get('duration', timedelta(hours=1)),
            'owner': kwargs.get('owner'),
            'category': kwargs.get('category', str(MatchCategory.SOCCER))
        }
        return Match.objects.create(**match_properties)
