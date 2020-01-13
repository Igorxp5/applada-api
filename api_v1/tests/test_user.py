from django.test import TestCase
from api_v1.models import User

class ExampleTestCase(TestCase):
    def setUp(self):
        igorxp5 = User(username='igorxp5', name='Igor Fernandes', email='rogixp5@gmail.com')
        igorxp5.set_password('1234')
        igorxp5.save()

    def test_case_1(self):
        """Test case 1"""
        igorxp5 = User.objects.get(username="igorxp5")
        self.assertEqual(igorxp5.name, 'Igor Fernandes')

    def test_case_2(self):
        """Test case 2"""
        igorxp5 = User.objects.get(username="igorxp5")
        self.assertEqual(igorxp5.name, 'Igor Fernandes')