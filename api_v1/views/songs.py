from rest_framework import generics
from api_v1.models import Song
from api_v1.serializers import SongSerializer

class SongsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = Song.objects.all()
    serializer_class = SongSerializer