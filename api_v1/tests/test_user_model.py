from django.test import TestCase
from api_v1.models.user import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class UserModelTestCase(TestCase):
    """User Model"""
    
    def test_cant_create_user_without_password(self):
        """Create a new user without a password raises a ValidationError"""
        with self.assertRaises(ValidationError) as error:
            User.create_user(username='user', email='user@gmail.com', password=None)
        
        assert 'password_digest' in error.exception.message_dict, 'Password field is not in errors'

        self.assertEquals(error.exception.message_dict['password_digest'][0], 'Password cannot be null')

    def test_cant_create_user_without_email(self):
        """Create a new user without a email raises a ValidationError"""
        with self.assertRaises(ValidationError) as error:
            User.create_user(username='user', email=None, password='1234')
        
        assert 'email' in error.exception.message_dict, 'Email field is not in errors'
        
        self.assertEquals(error.exception.message_dict['email'][0], 'Email cannot be null')
        
    def test_cant_create_two_users_with_same_username(self):
        """Create a new user with same username of other user already created raises a ValidationError"""
        with self.assertRaises(ValidationError) as error:
            User.create_user(username='user', email='user_1@gmail.com', password='1234')
            User.create_user(username='user', email='user_2@gmail.com', password='4321')
        
        assert 'username' in error.exception.message_dict, 'Username field is not in errors'

        self.assertEquals(error.exception.message_dict['username'][0], 'User with this Username already exists.')

    def test_cant_create_two_users_with_same_email(self):
        """Create a new user with same email of other user already created raises a ValidationError"""
        with self.assertRaises(ValidationError) as error:
            User.create_user(username='user_1', email='user_1@gmail.com', password='1234')
            User.create_user(username='user_2', email='user_1@gmail.com', password='4321')
        
        assert 'email' in error.exception.message_dict, 'Email field is not in errors'
                
        self.assertEquals(error.exception.message_dict['email'][0], 'User with this Email already exists.')

    def test_find_user_created(self):
        """Find user after create it"""
        created_user = User.create_user(username='user_1', email='user_1@gmail.com', password='1234')
        found_user = User.objects.get(username='user_1')

        self.assertEquals(created_user.username, found_user.username)
        self.assertEquals(created_user.email, found_user.email)
    
    def test_authenticate_user_with_correct_password(self):
        """Authenticate user passing just username and plain-text correct password"""
        password = '1234'
        created_user = User.create_user(username='user_1', email='user_1@gmail.com', password=password)
        
        assert created_user.authenticate(password), 'Can not authenticate user using correct password'

    def test_authenticate_user_with_incorrect_password(self):
        """Authenticate user passing username and plain-text incorrect password should fail"""
        correct_password, incorrect_password = '1234', '4321'
        created_user = User.create_user(username='user_1', email='user_1@gmail.com', 
                                        password=correct_password)
        
        assert not created_user.authenticate(incorrect_password), \
            'User should not be authenticated using incorrect password'