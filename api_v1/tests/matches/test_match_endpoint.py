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


class MatchEndpointTestCase(TestCase):
    """Match Endpoint"""
    expected_structure = {'id': None, 'title': None, 'description': None, 
                          'owner': None, 'duration': None, 'category': None,
                          'location': {'latitude', 'longitude'}, 'date': None,
                          'status': None, 'created_date': None, 'limit_participants': None}

    def setUp(self):
        self.client = APIClient()
    
    def test_not_authenticated_get_match(self):
        """GET /matches/{id}: Non-Authenticated request should return 401 response code and appropriate error message"""
        response = self.client.get(f'{URL_PREFFIX}/matches/1', follow=True)
        self.assertEquals(response.status_code, 401)
        self.assertJSONEqual(response, {'errors': ['Authentication credentials were not provided.']})
    
    def test_get_match_not_created(self):
        """GET /matches/{id}: Get a match that does not exist should return 404 response code and appropriate error message"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        response = self.client.get(f'{URL_PREFFIX}/matches/1', follow=True)
        self.assertEquals(response.status_code, 404)
        self.assertJSONEqual(response, {'errors':['Match not found']})
    
    def test_get_match_structure(self):
        """GET /matches/{id}: Get a match should return correct match structure"""        
        test_user = self._create_test_user()
        test_match = self._create_test_match(owner=test_user)
        self.client.force_authenticate(user=test_user)
        response = self.client.get(f'{URL_PREFFIX}/matches/{test_match.id}', follow=True)
        expected_data = {'title': test_match.title, 
                         'description': test_match.description,
                         'owner': test_user.username,
                         'date': test_match.date.astimezone().strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT']),
                         'duration': '01:00:00',
                         'category': test_match.category,
                         'limit_participants': None}
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, self.expected_structure)
        self.assertJSONContains(response, expected_data, only_expected_keys=False, value_equals=True)
    
    def test_only_owner_can_edit_match(self):
        """PATCH /matches/{id}: A match can be updated only by the owner's it"""
        test_user = self._create_test_user()
        other_user = User.objects.create_user(username='other', email='other@gmail.com', password='1234')
        test_match = self._create_test_match(owner=test_user)
        self.client.force_authenticate(user=other_user)
        response = self.client.patch(f'{URL_PREFFIX}/matches/{test_match.id}', 
                                   {'title': 'New title'}, format='json', follow=True)
        self.assertEquals(response.status_code, 403)
        self.assertJSONEqual(response, {'errors': ['You do not have permission to perform this action.']})

        response = self.client.put(f'{URL_PREFFIX}/matches/{test_match.id}', 
                                   {'title': 'New title'}, format='json', follow=True)
        self.assertEquals(response.status_code, 403)
        self.assertJSONEqual(response, {'errors': ['You do not have permission to perform this action.']})
    
    def test_create_match(self):
        """POST /matches: Should create a match"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        match_properties = {
            'title': 'Match title',
            'description': 'a description',
            'location': {'latitude': -8.0651966, 'longitude': -34.944717},
            'date': timezone.now() + timedelta(days=5),
            'duration': '01:00:00',
            'category': str(MatchCategory.SOCCER)
        }
        response = self.client.post(f'{URL_PREFFIX}/matches', 
                                    match_properties, format='json', follow=True)
        self.assertEquals(response.status_code, 201)
        self.assertJSONContains(response, self.expected_structure)
    
    def test_match_owner_cant_be_edited(self):
        """PATCH /matches/{id}: Match owner should not be changed"""
        test_user = self._create_test_user()
        other_user = User.objects.create_user(username='other', email='other@gmail.com', password='1234')
        self.client.force_authenticate(user=test_user)
        test_match = self._create_test_match(owner=test_user)
        response = self.client.patch(f'{URL_PREFFIX}/matches/{test_match.id}', 
                                    {'owner': other_user.username}, format='json', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()['owner'], test_user.username)

    def test_match_status(self):
        """GET /matches/{id}: Status value should be based on match date and match duration"""
        test_user = self._create_test_user()
        

        self.client.force_authenticate(user=test_user)
        test_match = self._create_test_match(owner=test_user)
        response = self.client.get(f'{URL_PREFFIX}/matches/{test_match.id}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()['status'], 'on_hold')
        
        testtime = timezone.now() - timedelta(days=1)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = testtime
            test_match = self._create_test_match(owner=test_user,
                                                 date=(timezone.now() + timedelta(days=1)))
        
        response = self.client.get(f'{URL_PREFFIX}/matches/{test_match.id}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()['status'], 'on_going')

        testtime = timezone.now() - timedelta(days=1)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = testtime
            test_match = self._create_test_match(owner=test_user,
                                                 date=(timezone.now() + timedelta(hours=2)))
        
        response = self.client.get(f'{URL_PREFFIX}/matches/{test_match.id}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()['status'], 'finished')
    
    def test_cant_create_match_in_past(self):
        """POST /matches: User cant create a match in the past"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        match_properties = {
            'title': 'Match title',
            'description': 'a description',
            'location': {'latitude': -8.0651966, 'longitude': -34.944717},
            'date': timezone.now() - timedelta(days=1),
            'duration': '01:00:00',
            'category': str(MatchCategory.SOCCER)
        }
        response = self.client.post(f'{URL_PREFFIX}/matches', 
                                    match_properties, format='json', follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Match date cannot be in the past']})
    
    def test_cant_create_match_longer_than_one_hour(self):
        """POST /matches: Match date must be at least one hour longer than current time"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        match_properties = {
            'title': 'Match title',
            'description': 'a description',
            'location': {'latitude': -8.0651966, 'longitude': -34.944717},
            'date': timezone.now() + timedelta(minutes=30),
            'duration': '01:00:00',
            'category': str(MatchCategory.SOCCER)
        }
        response = self.client.post(f'{URL_PREFFIX}/matches', 
                                    match_properties, format='json', follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Match date must be at least one hour longer than now']})
    
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
