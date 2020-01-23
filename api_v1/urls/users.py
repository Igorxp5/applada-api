from django.urls import path
from api_v1.views import UsersSearch, UserRetrieveUpdate, UsersMatch

urlpatterns = [
    path('users', UsersSearch.as_view()),
    path('users/<str:username>', UserRetrieveUpdate.as_view()),
    path(r'users/<str:username>/matches', UsersMatch.as_view())
]
