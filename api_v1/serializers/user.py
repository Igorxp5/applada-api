from rest_framework import serializers
from api_v1.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'level', 'registred_date')
        read_only_fields = ('username', 'level', 'registred_date')
        extra_kwargs = {
            'password': {'write_only': True}
        }