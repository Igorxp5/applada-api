from django.test import Client
from api_v1.utils import TestCase
from api_v1.models.user import User
from django.utils.translation import gettext as _

URL_PREFFIX = '/v1/'
DEFAULT_ENCODE = 'utf-8'


class UserEndpointTestCase(TestCase):
    """User Endpoint"""
    
    def setUp(self):
        self.client = Client()

    def test_get_user_by_username(self):
        """GET /users/{username}: Get a user should return only public data about the user"""
        test_user = self._create_test_user()
        response = self.client.get(URL_PREFFIX + 'users/' + test_user.username, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'username', 'name', 'email', 'level', 'registred_date'})
        self.assertEquals(response.json()['username'], test_user.username)

    def test_user_not_found(self):
        """GET /users/{username}: Get a user who does not exist should return 404 response code and appropriate error message"""
        response = self.client.get(URL_PREFFIX + 'users/whatever', follow=True)
        self.assertEquals(response.status_code, 404)
        self.assertJSONEqual(response, {'errors':['User not found']})

    def _create_test_user(self):
        new_user = User.create_user(username='whatever', email='whatever@gmail.com', password='1234')
        new_user.save()
        return new_user
