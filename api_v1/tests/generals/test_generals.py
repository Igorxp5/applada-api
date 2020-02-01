from api_v1.utils import TestCase

from rest_framework.test import APIClient

URL_PREFFIX = '/v1'
DEFAULT_ENCODE = 'utf-8'


class GeneralTestCase(TestCase):
    """General Tests"""

    def test_error_404(self):
        """Request a invalid url should return 404 error response"""
        response = self.client.get(f'{URL_PREFFIX}/some-invalid-url', follow=True)
        self.assertEquals(response.status_code, 404)
        self.assertJSONEqual(response, {'errors': ['Resource or item not found']})