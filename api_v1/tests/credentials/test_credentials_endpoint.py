from api_v1.utils import TestCase
from api_v1.models.user import User

from rest_framework.test import APIClient

URL_PREFFIX = '/v1'
DEFAULT_ENCODE = 'utf-8'


class UserEndpointTestCase(TestCase):
    """Credentials Endpoint"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_signup_account(self):
        """POST /sign-up: By passing username, email and password should create a new account"""
        account_data = dict(username='new_account', email='new_account@gmail.com', password='1234')
        response = self.client.post(f'{URL_PREFFIX}/sign-up', 
                                    account_data, format='json', follow=True)
        self.assertEquals(response.status_code, 201)
        self.assertJSONContains(response, {'username', 'name', 'level', 'registred_date'})
        
        expected_data = dict(username=account_data['username'], level=1, name=None)
        self.assertJSONContains(response, expected_data, value_equals=True, only_expected_keys=False)
    
    def test_account_same_username_error(self):
        """POST /sign-up: Cannot create an account with another user's username"""
        other_user = User.objects.create_user(username='other', email='other@gmail.com', password='1234')
        account_data = dict(username=other_user.username, email='new_account@gmail.com', password='1234')

        response = self.client.post(f'{URL_PREFFIX}/sign-up', 
                                    account_data, format='json', follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['A user with that username already exists.']})
    
    def test_account_same_email_error(self):
        """POST /sign-up: Cannot create an account with another user's email"""
        other_user = User.objects.create_user(username='other', email='other@gmail.com', password='1234')
        account_data = dict(username='new_account', email=other_user.email, password='1234')

        response = self.client.post(f'{URL_PREFFIX}/sign-up', 
                                    account_data, format='json', follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertJSONEqual(response, {'errors': ['User with this email already exists.']})
    
    def test_login_after_create_account(self):
        """POST /sign-in: Should return access token if it's passed correct credentials"""
        test_user_password = '1234'
        test_user = User.objects.create_user(username='test', email='test@gmail.com', 
                                             password=test_user_password)
        response = self.client.post(f'{URL_PREFFIX}/sign-in', 
                                    {'username': test_user.username, 'password':test_user_password}, 
                                    format='json', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, {'access', 'refresh'})

    def test_login_with_bad_credentials(self):
        """POST /sign-in: By passing bad credentials should return 'User or password incorrect'"""
        bad_user = dict(username='bad_username', password='bad_password')
        response = self.client.post(f'{URL_PREFFIX}/sign-in', 
                                    {'username': bad_user['username'], 'password': bad_user['password']}, 
                                    format='json', follow=True)
        self.assertEquals(response.status_code, 401)
        self.assertJSONEqual(response, {'errors': ['User or password incorrect']})
