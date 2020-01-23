import django.test

from rest_framework.response import Response


class TestCase(django.test.TestCase):
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

        :param response: response from django.test.Client request or JSON parsed to dict
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

        def _dict_presence_test(dict_data, expected_dict, deep_keys=tuple(), 
                                only_expected_keys=True):
            if only_expected_keys:
                for key in dict_data:
                    assert key in expected_dict, f"Unexpected '{_deep_key_string(deep_keys, key)}' key"
            
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
                elif isinstance(dict_data[key], dict):
                    new_deep_keys = [k for k in deep_keys] + [key]
                    _dict_presence_test(dict_data[key], expected_dict[key], new_deep_keys)
        
        if isinstance(response, Response): 
            self.assertJSONContentType(response)
            data = response.json()
        else:
            data = response
        
        _dict_presence_test(data, expected_data, only_expected_keys=only_expected_keys)