from api_v1.utils import TestCase
from api_v1.models.user import User

from rest_framework.test import APIClient

URL_PREFFIX = '/v1'
DEFAULT_ENCODE = 'utf-8'


class UserEndpointTestCase(TestCase):
    """User Endpoint"""
    
    def setUp(self):
        self.client = APIClient()

    def test_unable_to_get_staff_user(self):
        """GET /users/{username}: Should not be able to get staff user profile"""
        self.client.force_authenticate(user=self._create_test_user())
        staff_user = User.objects.create_user(username='staff', email='staff@gmail.com', password='1234', is_staff=True)
        response = self.client.get(f'{URL_PREFFIX}/users/{staff_user.username}', follow=True)
        self.assertEquals(response.status_code, 404)
        self.assertJSONEqual(response, {'errors': ['User not found']})

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
        """GET /users?search={username}: Should return count, next and previous link, and results"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        response = self.client.get(f'{URL_PREFFIX}/users?search={test_user.username}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'count', 'next', 'previous', 'results'})
    
    def test_search_user_limit_20(self):
        """GET /users?search={username}: Should return a maximum at 20 users per result"""
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
        """GET /users?search={username}: Should be able pass offset and limit"""
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
        
    def test_user_can_edit_own_name(self):
        """PATCH /users/{username}: User can edit own name"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        new_name = 'New Name'
        response = self.client.patch(f'{URL_PREFFIX}/users/{test_user.username}', 
                                     {'name': new_name}, format='json', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContentType(response)

        self.assertEquals(response.json()['name'], new_name)

        response_get = self.client.get(f'{URL_PREFFIX}/users/{test_user.username}', follow=True)
        self.assertEquals(response_get.status_code, 200)
        self.assertJSONContentType(response_get)

        self.assertEquals(response_get.json()['name'], new_name)
    
    def test_cant_edit_other_user_profile(self):
        """PATCH /users/{username}: Other user should not be able to edit non-own profile"""
        test_user = self._create_test_user()
        other_user = User.objects.create_user(username='other', email='other@gmail.com', password='1234')
        self.client.force_authenticate(user=other_user)

        new_name = 'New Name'
        response = self.client.patch(f'{URL_PREFFIX}/users/{test_user.username}', 
                                     {'name': new_name}, format='json', follow=True)
        self.assertEquals(response.status_code, 403)
        self.assertJSONContentType(response)
    
    def test_cant_edit_username(self):
        """PATCH /users/{username}: User should not be able to change username"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        new_username = 'new_username'
        response = self.client.patch(f'{URL_PREFFIX}/users/{test_user.username}', 
                                     {'username': new_username}, format='json', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContentType(response)
        self.assertEquals(response.json()['username'], test_user.username)
    
    def test_user_cant_set_blank_name(self):
        """PATCH /users/{username}: User should not be able to set blank name"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        response = self.client.patch(f'{URL_PREFFIX}/users/{test_user.username}', 
                                     {'name': ''}, format='json', follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Name cannot be empty']})
    
    def test_change_user_password(self):
        """PATCH /users/{username}: To change user password, need provide old password"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        
        password = '1234'
        wrong_password = '123'
        new_password = '4321'
        response = self.client.patch(f'{URL_PREFFIX}/users/{test_user.username}', 
                                     {'password': new_password}, format='json', follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Provide old password']})

        response = self.client.patch(f'{URL_PREFFIX}/users/{test_user.username}', 
                                     {'old_password': wrong_password, 'password': new_password}, 
                                     format='json', follow=True)
        
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['Wrong password']})

        response = self.client.patch(f'{URL_PREFFIX}/users/{test_user.username}', 
                                     {'old_password': password, 'password': new_password}, 
                                     format='json', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'username', 'name', 'email', 'level', 'registred_date'})
        
        sign_response = self.client.post(f'{URL_PREFFIX}/sign-in', 
                                     {'username': test_user.username, 'password': new_password}, 
                                     format='json', follow=True)
        self.assertEquals(sign_response.status_code, 200)
        self.assertJSONContains(sign_response, {'refresh', 'access'})

    def test_not_authenticated_get_user(self):
        """GET /users/{username}: Non-Authenticated request should return 401 response code and appropriate error message"""
        response = self.client.get(f'{URL_PREFFIX}/users/whoever', follow=True)
        self.assertEquals(response.status_code, 401)
        self.assertJSONEqual(response, {'errors': ['Authentication credentials were not provided.']})

    def test_get_user_by_username(self):
        """GET /users/{username}: Get a user should return only public data about the user"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        response = self.client.get(f'{URL_PREFFIX}/users/{test_user.username}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'username', 'name', 'email', 'level', 'registred_date'})
        self.assertEquals(response.json()['username'], test_user.username)

    def test_user_not_found(self):
        """GET /users/{username}: Get a user who does not exist should return 404 response code and appropriate error message"""
        self.client.force_authenticate(user=self._create_test_user())
        response = self.client.get(f'{URL_PREFFIX}/users/whoever', follow=True)
        self.assertEquals(response.status_code, 404)
        self.assertJSONEqual(response, {'errors':['User not found']})

    def _create_test_user(self):
        return User.objects.create_user(username='whatever', email='whatever@gmail.com', password='1234')
