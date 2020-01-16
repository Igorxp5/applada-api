from django.urls import path
from api_v1.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('sign-in', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('sign-in/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]
