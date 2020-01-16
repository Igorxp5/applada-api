from django.urls import path
from api_v1.views import UsersSearch, UserRetrieveUpdate

urlpatterns = [
    path('users/', UsersSearch.as_view()),
    path('users/<str:pk>/', UserRetrieveUpdate.as_view())
]
