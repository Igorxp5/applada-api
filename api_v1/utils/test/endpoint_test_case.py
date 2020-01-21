import urllib
import inspect
import django.test

from rest_framework.test import APIClient

from api_v1.models import User


class EndpointTestCase(django.test.TestCase):
    url_preffix = '/v1'
    endpoint = ''
    generic_tests_classes = [
        # NeedAuthenticationEndpointGenericTest,
        # RequiredQueryParamsEndpointGenericTest,
        # NullableFieldsEndpointGenericTest,
        # NotNullableFieldsEndpointGenericTest,
        # BlankableFieldsEndpointGenericTest,
        # NotBlankableFieldsEndpointGenericTest,
        # PublicFieldsEndpointGenericTest,
        # CreateRequiredFieldsEndpointGenericTest,
        # OnlyOwnerCanEditEndpointGenericTest,
        # OwnershipCannotBeChangedEndpointGenericTest,
        # NotUpdatableFieldsEndpointGenericTest,
        # PaginationEndpointGenericTest,
        # UniqueColumnEndpointGenericTest
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_user = None
        self.other_user = None
    
    def setUp(self):
        self.client = APIClient()

    def get_endpoint(self, path=''):
        url = urllib.parse.urljoin(f'{self.url_preffix}/', f"{self.endpoint.strip('/')}/")
        return urllib.parse.urljoin(url, f"{str(path).strip('/')}").rstrip('/')
    
    def get_auth_user(self):
        self.auth_user = self.auth_user or User.objects.create_user(username='auth', email='auth@gmail.com', password='auth')
        return self.auth_user

    def get_other_user(self):
        self.other_user = self.other_user or User.objects.create_user(username='other', email='other@gmail.com', password='other')
    
    def get_model_properties_example(self):
        raise NotImplementedError
    
    def get_instance_example(self):
        raise NotImplementedError

    def get_required_fields(self):
        raise NotImplementedError
    
    def get_nullable_fields(self):
        raise NotImplementedError
    
    def get_not_nullable_fields(self):
        raise NotImplementedError

    def get_blankable_fields(self):
        raise NotImplementedError

    def get_not_blankable_fields(self):
        raise NotImplementedError
    
    def get_public_fields(self):
        raise NotImplementedError
    
    def get_create_required_fields(self):
        raise NotImplementedError
    
    def get_owner_field_name(self):
        return 'owner'
    
    def get_not_updatable_fields(self):
        raise NotImplementedError
    
    def get_unique_columns(self):
        return NotImplementedError

    def assertJSONContentType(self, response):
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEquals(response.get('Content-Type'), 'application/json')

    def assertJSONEqual(self, response, *args, **kwargs):
        """
        Assert two JSON data are equals. Before that, the method check if the Content-Type header
        is 'application/json'.

        :param response: response from django.test.Client request
        """
        self.assertJSONContentType(response)
        super().assertJSONEqual(response.content, *args, **kwargs)
    
    def assertJSONContains(self, response, expected_data, value_equals=False, 
                           only_expected_keys=True):
        """
        Assert two JSON data have same structure.

        :param response: response from django.test.Client request
        :param expected_data: dict object to use as template for the test
        :param value_equals: If this parameter is True, then values in template object will be tested too.
                             Otherwise, only keys will be checked.
        :param only_expected_keys: If this parameter is True, then if there is a key in reponse data that
                                   is not in expected data, the assertion is false. Otherwise, other keys
                                   in response data will be ignored.
        """
        def _deep_key_string(deep_keys, current_key):
            keys = ['root'] + [k for k in deep_keys] + [current_key]
            return ' > '.join(keys)

        def _dict_presence_test(dict_data, expected_dict, deep_keys=tuple()):
            for key in expected_dict:
                assert key in dict_data, f'{_deep_key_string(deep_keys, key)} not found'
                
                if value_equals:
                    assert type(dict_data[key]) == type(expected_dict[key]), \
                        f'{_deep_key_string(deep_keys, key)} do not have same type'
                    if isinstance(dict_data[key], dict):
                        new_deep_keys = [k for k in deep_keys] + [key]
                        _dict_presence_test(dict_data[key], expected_dict[key], new_deep_keys)
                    else:
                        assert dict_data[key] == expected_dict[key], \
                            f'{_deep_key_string(deep_keys, key)} are not equals'
        
        def _only_expected_keys_test(dict_data, expected_dict):
            for key in dict_data:
                assert key in expected_dict, f"Unexpected '{key}' key"
        
        self.assertJSONContentType(response)
        
        data = response.json()
        if only_expected_keys:
            _only_expected_keys_test(data, expected_data)
        
        _dict_presence_test(data, expected_data)

    @staticmethod
    def set_endpoint(model_class, endpoint):
        def wrapper(cls):
            cls.model_class = model_class
            cls.model_class_name = model_class.__name__
            cls.endpoint = endpoint
            class_members = inspect.getmembers(cls)
            class_members_dict = {k: v for k, v in class_members}
            for name, member in class_members_dict.items():
                if name.startswith('test_'):
                    member.__doc__ = member.__doc__ % dict(class_members_dict)
            return cls
        return wrapper
