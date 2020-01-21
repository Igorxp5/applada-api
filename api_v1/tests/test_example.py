from django.utils import timezone
from django.contrib.gis.geos import Point

from datetime import timedelta

from api_v1.models import Match
from api_v1.utils.test import EndpointTestCase, PublicFieldsEndpointGenericTest, APublicFieldsEndpointGenericTest


included_tests = (PublicFieldsEndpointGenericTest, EndpointTestCase)

@EndpointTestCase.set_endpoint(model_class=Match, endpoint='/matches')
class MatchEndpointTestCase(*included_tests):
    """Match Endpoint"""

    def get_public_fields(self):
        return {'id': None, 'title': None, 'description': None, 
                'owner': None, 'duration': None, 'category': None,
                'location': {'latitude', 'longitude'}, 'date': None,
                'status': None, 'created_date': None, 'limit_participants': None}
    
    def get_model_properties_example(self):
        return {'title': 'Match title',
                'description': 'A description',
                'location': Point(-8.0651966, -34.944717),
                'owner': self.get_auth_user(),
                'date': timezone.now() + timedelta(days=5),
                'duration': '01:00:00',
                'category': 'soccer',
                'limit_participants': None
        }
    
