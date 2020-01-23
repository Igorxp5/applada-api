from rest_framework import serializers

from django.utils.translation import gettext as _
from api_v1.utils.validation import validate_location

from api_v1.fields import LocationField
from api_v1.serializers import UserSerializer
from api_v1.models import Match, MatchStatus, MatchSubscription


class MatchSerializer(serializers.ModelSerializer):
    location = LocationField(source='*', required=True)
    status = serializers.SerializerMethodField(read_only=True)
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)
    
    class Meta:
        model = Match
        fields = ('id', 'title', 'description', 'limit_participants', 'category', 
                  'location', 'date', 'duration', 'status', 'owner', 'created_date')
    
    def get_status(self, obj):
        return obj.status.value
    
    def validate(self, data):
        validated_data = super().validate(data)
        if 'location' in data:
            validated_data['location'] = validate_location(data['location'])
        return validated_data
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user 
        return super().create(validated_data)


class MatchSubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    date = serializers.DateTimeField(read_only=True)
    match_id = serializers.PrimaryKeyRelatedField(source='match',
                                                  queryset=Match.objects.all())

    class Meta:
        model = MatchSubscription
        fields = ('match_id', 'date', 'user')

    def validate(self, data):
        validated_data = super().validate(data)
        validated_data['user'] = self.context['request'].user
        return validated_data