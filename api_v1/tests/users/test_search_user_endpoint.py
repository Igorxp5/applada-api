from api_v1.utils import TestCase
from api_v1.models.user import User

from rest_framework.test import APIClient

URL_PREFFIX = '/v1'
DEFAULT_ENCODE = 'utf-8'


class SearchUserEndpointTestCase(TestCase):
    """Search User Endpoint"""
    
    def setUp(self):
        self.client = APIClient()

    def test_not_authenticated_search_user(self):
        """GET /users: Non-Authenticated request should return 401 response code and appropriate error message"""
        test_user = self._create_test_user()
        response = self.client.get(f'{URL_PREFFIX}/users?search={test_user.username}', follow=True)
        self.assertEquals(response.status_code, 401)
        self.assertJSONEqual(response, {'errors': ['Authentication credentials were not provided.']})

    def test_unable_to_search_staff_user(self):
        """GET /users: Should not be able to search staff user"""
        self.client.force_authenticate(user=self._create_test_user())
        staff_user = User.objects.create_user(username='staff', email='staff@gmail.com', password='1234', is_staff=True)
        response = self.client.get(f'{URL_PREFFIX}/users?search={staff_user.username}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContentType(response)
        self.assertEquals(response.json()['results'], [])
    
    def test_search_user_structure(self):
        """GET /users: Should return count, next and previous link, and results"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        response = self.client.get(f'{URL_PREFFIX}/users?search={test_user.username}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'count', 'next', 'previous', 'results'})
    
    def test_search_user_by_username(self):
        """GET /users: Should be able search user by username"""
        auth_user = self._create_test_user()
        test_user = User.objects.create_user(username='user', first_name='test', email='user@gmail.com', password='1234')
        self.client.force_authenticate(user=auth_user)
        response = self.client.get(f'{URL_PREFFIX}/users?search={test_user.username}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()['results'][0]['username'], test_user.username)

    def test_search_user_by_name(self):
        """GET /users: Should be able search user by name"""
        auth_user = self._create_test_user()
        test_user = User.objects.create_user(username='user', first_name='test', email='user@gmail.com', password='1234')
        self.client.force_authenticate(user=auth_user)
        response = self.client.get(f'{URL_PREFFIX}/users?search={test_user.first_name}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()['results'][0]['name'], test_user.first_name)
    
    def test_search_user_limit_20(self):
        """GET /users: Should return a maximum at 20 users per result"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        
        total_users = 25
        for i in range(total_users):
            User.objects.create_user(username=f'user{i}', email=f'user{i}@gmail.com', password='1234')

        response = self.client.get(f'{URL_PREFFIX}/users?search=user', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContentType(response)
        
        data = response.json()
        self.assertEquals(data['count'], total_users)
        self.assertEquals(data['previous'], None)
        self.assertNotEquals(data['next'], None)
        
        assert len(data['results']) == 20, 'Result do not have 20 records'

        response_next_page = self.client.get(data['next'], follow=True)
        self.assertEquals(response_next_page.status_code, 200)
        self.assertJSONContentType(response_next_page)

        data = response_next_page.json()
        self.assertEquals(data['count'], total_users)
        self.assertNotEquals(data['previous'], None)
        self.assertEquals(data['next'], None)
        
        assert len(data['results']) == 5, 'Next page result do not have 5 records'
        
        response_previous_page = self.client.get(data['previous'], follow=True)
        self.assertEquals(response_previous_page.status_code, 200)
        self.assertJSONContentType(response_previous_page)

        data = response_previous_page.json()
        self.assertEquals(data['count'], total_users)
        self.assertEquals(data['previous'], None)
        self.assertNotEquals(data['next'], None)
        
        assert len(data['results']) == 20, 'Previous page Result do not have 20 records'
    
    def test_search_user_limit_and_offset(self):
        """GET /users: Should be able pass offset and limit"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        
        total_users = 25
        for i in range(total_users):
            User.objects.create_user(username=f'user{i}', email=f'user{i}@gmail.com', password='1234')

        limit = 10
        offset = 15
        response = self.client.get(f'{URL_PREFFIX}/users?search=user&offset={offset}&limit={limit}', 
                                   follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContentType(response)
        
        data = response.json()

        self.assertEquals(data['results'][0]['username'], f'user{offset}')

        assert len(data['results']) == limit, f'Result do not have {limit} records'
    
    def _create_test_user(self):
        return User.objects.create_user(username='whatever', email='whatever@gmail.com', password='1234')
