import rest_framework_simplejwt.serializers
from rest_framework_simplejwt.serializers import PasswordField

from api_v1.serializers import UserSerializer

from django.utils.translation import gettext as _


class TokenObtainPairSerializer(rest_framework_simplejwt.serializers.TokenObtainPairSerializer):
    
    default_error_messages = {
        'no_active_account': _('No active account found with the given credentials')
    }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        del token['user_id']  # remove default field in payload
        token['user'] = UserSerializer(user).data
        return token

class TokenRefreshSerializer(rest_framework_simplejwt.serializers.TokenRefreshSerializer):
    pass
