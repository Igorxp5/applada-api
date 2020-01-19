from api_v1.utils import TestCase
from api_v1.models import User, Match, MatchCategory

from django.utils import timezone
from django.contrib.gis.geos import Point

from rest_framework.test import APIClient

from datetime import timedelta

URL_PREFFIX = '/v1'
DEFAULT_ENCODE = 'utf-8'


class SearchMatchEndpointTestCase(TestCase):
    """Search Match Endpoint"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_not_authenticated_search_match(self):
        """GET /matches: Non-Authenticated request should return 401 response code and appropriate error message"""
        url = f'{URL_PREFFIX}/matches?latitude=-8.0651966&longitude=-34.944717'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 401)
        self.assertJSONEqual(response, {'errors': ['Authentication credentials were not provided.']})
    
    def test_search_match_pagination(self):
        """GET /matches: Should return pagination fields (count, next, previous and results)"""
        test_user = self._create_test_user()
        test_match = self._create_test_match(test_user)
        self.client.force_authenticate(user=test_user)
        lat, lon, rad = -8.0651966, -34.944717, 15
        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude={lon}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'count', 'next', 'previous', 'results'})
    
    def test_search_match_radius_reach(self):
        """GET /matches: Should find matches by range area correctly"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        
        lat, lon, rad = -8.0651966, -34.944717, 15
        test_match = self._create_test_match(test_user, lat, lon)
        far_away = -7.890995,-34.91361
        
        url = f'{URL_PREFFIX}/matches?latitude={far_away[0]}&longitude={far_away[1]}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'count', 'next', 'previous', 'results'})
        self.assertEquals(len(response.json()['results']), 0)

        close = -8.045210, -34.930935
        
        url = f'{URL_PREFFIX}/matches?latitude={close[0]}&longitude={close[1]}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'count', 'next', 'previous', 'results'})
        self.assertEquals(len(response.json()['results']), 1)
        self.assertEquals(response.json()['results'][0]['title'], test_match.title)
        
        border_in = -7.957489, -34.868019

        url = f'{URL_PREFFIX}/matches?latitude={border_in[0]}&longitude={border_in[1]}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'count', 'next', 'previous', 'results'})
        self.assertEquals(len(response.json()['results']), 1)
        self.assertEquals(response.json()['results'][0]['title'], test_match.title)

        border_out = -7.947460, -34.854756

        url = f'{URL_PREFFIX}/matches?latitude={border_out[0]}&longitude={border_out[1]}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'count', 'next', 'previous', 'results'})
        self.assertEquals(len(response.json()['results']), 0)

    def test_search_match_radius_limit(self):
        """GET /matches: Should accept a maximum of 15 km radius"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)

        lat, lon, rad = -8.0651966, -34.944717, 15
        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude={lon}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

        lat, lon, rad = -8.0651966, -34.944717, 16
        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude={lon}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Radius must be a value from 1 to 15']})
    
    def test_search_match_requires_lat_and_lon(self):
        """GET /matches: Should respond only if latitude and longitude was passed as a parameter"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        
        lat, lon, rad = -8.0651966, -34.944717, 15
        url = f'{URL_PREFFIX}/matches'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Latitude is required', 'Longitude is required']})

        url = f'{URL_PREFFIX}/matches?latitude={lat}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Longitude is required']})

        url = f'{URL_PREFFIX}/matches?longitude={lon}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Latitude is required']})

    def test_search_match_invalid_values(self):
        """GET /matches: Should not accept invalid param values"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        
        lat, lon, rad = -8.0651966, -34.944717, 15
        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude=string'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Longitude must be a float number']})
        
        url = f'{URL_PREFFIX}/matches?latitude=string&longitude={lon}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Latitude must be a float number']})
        
        url = f'{URL_PREFFIX}/matches?latitude=string&longitude=string'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertIn('Latitude must be a float number', response.json()['errors'])
        self.assertIn('Longitude must be a float number', response.json()['errors'])
        
        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude={lon}&radius=string'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Radius must be a float number']})
    
    def test_search_matches_limit_20(self):
        """GET /matches: Should return a maximum at 20 matches per result"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        
        lat, lon, rad = -8.0651966, -34.944717, 15
        
        total_matches = 25
        for i in range(total_matches):
            self._create_test_match(test_user, lat, lon, timezone.now() + timedelta(days=i + 1))

        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude={lon}&radius={rad}'        
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContentType(response)
        
        data = response.json()
        self.assertEquals(data['count'], total_matches)
        self.assertEquals(data['previous'], None)
        self.assertNotEquals(data['next'], None)
        
        assert len(data['results']) == 20, 'Result do not have 20 records'

        response_next_page = self.client.get(data['next'], follow=True)
        self.assertEquals(response_next_page.status_code, 200)
        self.assertJSONContentType(response_next_page)

        data = response_next_page.json()
        self.assertEquals(data['count'], total_matches)
        self.assertNotEquals(data['previous'], None)
        self.assertEquals(data['next'], None)
        
        assert len(data['results']) == 5, 'Next page result do not have 5 records'
        
        response_previous_page = self.client.get(data['previous'], follow=True)
        self.assertEquals(response_previous_page.status_code, 200)
        self.assertJSONContentType(response_previous_page)

        data = response_previous_page.json()
        self.assertEquals(data['count'], total_matches)
        self.assertEquals(data['previous'], None)
        self.assertNotEquals(data['next'], None)
        
        assert len(data['results']) == 20, 'Previous page Result do not have 20 records'
    
    def test_search_matches_limit_and_offset(self):
        """GET /matches: Should be able pass offset and limit"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)

        lat, lon, rad = -8.0651966, -34.944717, 15
        
        total_matches = 25
        for i in range(total_matches):
            self._create_test_match(test_user, lat, lon, 
                                    timezone.now() + timedelta(days=i + 1), title=f'Match title {i}')

        limit, offset = 10, 15
        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude={lon}&radius={rad}&offset={offset}&limit={limit}'        
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContentType(response)
        
        data = response.json()

        self.assertEquals(data['results'][0]['title'], f'Match title {offset}')

        assert len(data['results']) == limit, f'Result do not have {limit} records'

    def _create_test_user(self):
        return User.objects.create_user(username='whatever', email='whatever@gmail.com', password='1234')
    
    def _create_test_match(self, owner, latitude=-8.0651966, longitude=-34.944717, 
                           date=None, title='Match title'):
        match_properties = {
            'title': title,
            'description': 'a description',
            'location': Point(longitude, latitude),
            'date': date or (timezone.now() + timedelta(days=5)),
            'duration': timedelta(hours=1),
            'owner': owner,
            'category': str(MatchCategory.SOCCER)
        }
        return Match.objects.create(**match_properties)
