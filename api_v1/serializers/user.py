from rest_framework import serializers

from django.utils.translation import gettext as _

from api_v1.models import User


class UserSerializer(serializers.ModelSerializer):
    registred_date = serializers.DateTimeField(source='date_joined', read_only=True)
    old_password = serializers.CharField(max_length=30, write_only=True)
    password = serializers.CharField(max_length=30, write_only=True)
    name = serializers.CharField(source='first_name')
    
    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'level', 'registred_date', 'old_password', 'password')
        read_only_fields = ('username', 'level')
    
    def validate(self, data):
        # If it's a attempt to change password, need provide old password
        if 'password' in data:
            old_password = data.get('old_password')
            if not old_password: 
                raise serializers.ValidationError({'old_password': _('Provide old password')})
            if not self.context['request'].user.check_password(old_password):
                raise serializers.ValidationError({'old_password': _('Wrong password')})

        return data

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()
        return instance
