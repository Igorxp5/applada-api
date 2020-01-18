from django.urls import path
from api_v1.views import TokenObtainPairView, TokenRefreshView, SignupAccountView

urlpatterns = [
    path('sign-in', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('sign-in/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('sign-up', SignupAccountView.as_view(), name='signup_account'),
]
