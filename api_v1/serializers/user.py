from rest_framework import serializers

from django.utils.translation import gettext as _

from api_v1.models import User


class UserSerializer(serializers.ModelSerializer):
    registred_date = serializers.DateTimeField(source='date_joined', read_only=True)
    old_password = serializers.CharField(max_length=30, write_only=True, required=False)
    password = serializers.CharField(max_length=30, write_only=True)
    name = serializers.CharField(source='first_name', required=False)
    
    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'level', 'registred_date', 'old_password', 'password')
        read_only_fields = ('level',)
        extra_kwargs = {
            'email': {'write_only': True}
        }
    
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            fields['username'].required = True
            fields['password'].required = True
        elif request and request.method in ['PUT', 'PATCH']:
            fields['username'].read_only = True
        return fields
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            old_password = validated_data.get('old_password')
            if not old_password: 
                raise serializers.ValidationError({'old_password': [_('Provide old password')]})
            if not self.context['request'].user.check_password(old_password):
                raise serializers.ValidationError({'old_password': [_('Wrong password')]})
        
        instance = super().update(instance, validated_data)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()
        return instance
