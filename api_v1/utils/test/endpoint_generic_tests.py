import inspect
import django.test


class GenericEndpointTest:
    pass


class PublicFieldsEndpointGenericTest:
    def test_public_fields(self):
        """GET %(endpoint)s: Get a %(model_class_name)s should return correct %(model_class_name)s structure"""
        auth_user = self.get_auth_user()
        model_instance = self.model_class.objects.create(**self.get_model_properties_example())
        self.client.force_authenticate(user=auth_user)
        response = self.client.get(f'{self.get_endpoint()}/{model_instance.id}', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertJSONContains(response, self.get_public_fields())
    
    def get_public_fields(self):
        raise NotImplementedError

    def get_model_properties_example(self):
        raise NotImplementedError
