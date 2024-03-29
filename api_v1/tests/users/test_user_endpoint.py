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
        """GET /users/{username}: Get own user should return username, name, email, level and registred date"""
        test_user = self._create_test_user()
        self.client.force_authenticate(user=test_user)
        response = self.client.get(f'{URL_PREFFIX}/users/{test_user.username}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'username', 'name', 'email', 'level', 'registred_date'})
        self.assertEquals(response.json()['username'], test_user.username)

    def test_get_other_user(self):
        """GET /users/{username}: Get other user profile should not return email, just: username, name, level an registred date"""
        test_user = self._create_test_user()
        other_user = User.objects.create_user(username='other', email='other@gmail.com', password='1234')
        self.client.force_authenticate(user=test_user)
        response = self.client.get(f'{URL_PREFFIX}/users/{other_user.username}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'username', 'name', 'level', 'registred_date'})

    def test_user_not_found(self):
        """GET /users/{username}: Get a user who does not exist should return 404 response code and appropriate error message"""
        self.client.force_authenticate(user=self._create_test_user())
        response = self.client.get(f'{URL_PREFFIX}/users/whoever', follow=True)
        self.assertEquals(response.status_code, 404)
        self.assertJSONEqual(response, {'errors':['User not found']})

    def _create_test_user(self):
        return User.objects.create_user(username='whatever', email='whatever@gmail.com', password='1234')
