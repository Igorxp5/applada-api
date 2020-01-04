from django.urls import path
from api_v1.views import SongsView


urlpatterns = [
    path('songs/', SongsView.as_view(), name="songs-all")
]
