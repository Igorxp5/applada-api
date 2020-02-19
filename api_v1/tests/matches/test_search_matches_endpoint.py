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

    match_expected_structure = {'id': None, 'title': None, 'description': None, 
                                'owner': None, 'duration': None, 'category': None,
                                'location': {'latitude', 'longitude'}, 'date': None,
                                'status': None, 'created_date': None, 'limit_participants': None}
    
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
        test_match = self._create_test_match(owner=test_user)
        self.client.force_authenticate(user=test_user)
        lat, lon, rad = -8.0651966, -34.944717, 15
        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude={lon}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'count', 'next', 'previous', 'results'})
    
    def test_search_match_pagination_result_structure(self):
        """GET /matches: The pagination match result should have fields (match and distance)"""
        test_user = self._create_test_user()
        test_match = self._create_test_match(owner=test_user)
        self.client.force_authenticate(user=test_user)
        lat, lon, rad = -8.0651966, -34.944717, 15
        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude={lon}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertIn('results', response.json())
        self.assertEquals(len(response.json()['results']), 1)
        self.assertIn('match', response.json()['results'][0])
        self.assertIn('distance', response.json()['results'][0])
    
    def test_searh_match_distance_value(self):
        """GET /matches: Should return distance to match correctly"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        
        lat, lon, rad = -8.0651966, -34.944717, 15
        test_match = self._create_test_match(owner=test_user, latitude=lat, longitude=lon)
        close_location = -8.045210, -34.930935
        
        url = f'{URL_PREFFIX}/matches?latitude={close_location[0]}&longitude={close_location[1]}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'count', 'next', 'previous', 'results'})
        self.assertEquals(len(response.json()['results']), 1)
        self.assertIn('distance', response.json()['results'][0])
        self.assertEquals(round(response.json()['results'][0]['distance']), 3)
    
    def test_match_structure(self):
        """GET /matches: Search matches should return correct match structure"""
        test_user = self._create_test_user()
        test_match = self._create_test_match(owner=test_user)
        self.client.force_authenticate(user=test_user)
        lat, lon, rad = -8.0651966, -34.944717, 15
        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude={lon}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response.json()['results'][0]['match'], self.match_expected_structure)

    def test_search_match_radius_reach(self):
        """GET /matches: Should find matches by range area correctly"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        
        lat, lon, rad = -8.0651966, -34.944717, 15
        test_match = self._create_test_match(owner=test_user, latitude=lat, longitude=lon)
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
        self.assertEquals(response.json()['results'][0]['match']['title'], test_match.title)
        
        border_in = -7.957489, -34.868019

        url = f'{URL_PREFFIX}/matches?latitude={border_in[0]}&longitude={border_in[1]}&radius={rad}'
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'count', 'next', 'previous', 'results'})
        self.assertEquals(len(response.json()['results']), 1)
        self.assertEquals(response.json()['results'][0]['match']['title'], test_match.title)

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
            self._create_test_match(owner=test_user, 
                                    latitude=lat, 
                                    longitude=lon, 
                                    date=timezone.now() + timedelta(days=i + 1))

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
            self._create_test_match(owner=test_user, 
                                    latitude=lat, 
                                    longitude=lon,
                                    title=f'Match title {i}',
                                    date=timezone.now() + timedelta(days=i + 1))

        limit, offset = 10, 15
        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude={lon}&radius={rad}&offset={offset}&limit={limit}'        
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContentType(response)
        
        data = response.json()

        self.assertEquals(data['results'][0]['match']['title'], f'Match title {total_matches - offset - 1}')

        assert len(data['results']) == limit, f'Result do not have {limit} records'
    
    def test_search_match_order(self):
        """GET /matches: Match order should be returned in descending created date"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        
        lat, lon, rad = -8.0651966, -34.944717, 15
        
        total_matches = 2
        for i in range(total_matches):
            self._create_test_match(owner=test_user, 
                                    latitude=lat, 
                                    longitude=lon,
                                    title=f'Match title {i}',
                                    date=timezone.now() + timedelta(days=i + 1))

        url = f'{URL_PREFFIX}/matches?latitude={lat}&longitude={lon}&radius={rad}'        
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContentType(response)
        self.assertEquals(response.json()['results'][0]['match']['title'], 'Match title 1')
        self.assertEquals(response.json()['results'][1]['match']['title'], 'Match title 0')

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
