from django.urls import path
from api_v1.views import MatchCreateSearch, MatchRetrieveUpdateDelete

urlpatterns = [
   path('matches', MatchCreateSearch.as_view()),
   path('matches/<int:pk>', MatchRetrieveUpdateDelete.as_view())
]
