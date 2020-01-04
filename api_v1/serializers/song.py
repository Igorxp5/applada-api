from rest_framework import serializers
from api_v1.models import Song


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ("title", "artist")
