import rest_framework_simplejwt.serializers
from rest_framework_simplejwt.serializers import PasswordField

from django.utils.translation import gettext as _

from api_v1.translation import error_messages as e_


class TokenObtainPairSerializer(rest_framework_simplejwt.serializers.TokenObtainPairSerializer):
    
    default_error_messages = {
        'no_active_account': _('No active account found with the given credentials')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'] = PasswordField(error_messages=e_('Password'))

class TokenRefreshSerializer(rest_framework_simplejwt.serializers.TokenRefreshSerializer):
    pass
