from api_v1.utils import TestCase
from api_v1.models.user import User

from django.utils.translation import gettext as _

from rest_framework.test import APIClient

URL_PREFFIX = '/v1'
DEFAULT_ENCODE = 'utf-8'


class UserEndpointTestCase(TestCase):
    """User Endpoint"""
    
    def setUp(self):
        self.client = APIClient()

    def test_unable_to_get_staff_user(self):
        """GET /users: Should not be able to get staff user profile"""
        self.client.force_authenticate(user=self._create_test_user())
        staff_user = User.objects.create_user(username='staff', email='staff@gmail.com', password='1234', is_staff=True)
        response = self.client.get(f'{URL_PREFFIX}/users/{staff_user.username}', follow=True)
        self.assertEquals(response.status_code, 404)
        self.assertJSONEqual(response, {'errors': ['User not found']})

    def test_not_authenticated_search_user(self):
        """GET /users: Non-Authenticated request should return 401 response code and appropriate error message"""
        response = self.client.get(f'{URL_PREFFIX}/users', follow=True)
        self.assertEquals(response.status_code, 401)
        self.assertJSONEqual(response, {'errors': ['Authentication credentials were not provided.']})

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
