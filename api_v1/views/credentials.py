import rest_framework_simplejwt.views

from api_v1.models import User
from api_v1.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, \
                               UserSerializer

from rest_framework import generics


class TokenObtainPairView(rest_framework_simplejwt.views.TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    queryset = User.objects.filter(is_staff=False)


class TokenRefreshView(rest_framework_simplejwt.views.TokenRefreshView):
    serializer_class = TokenRefreshSerializer
    queryset = User.objects.filter(is_staff=False)


class SignupAccountView(generics.CreateAPIView):
    serializer_class = UserSerializer
