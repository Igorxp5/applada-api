import rest_framework_simplejwt.views

from api_v1.models import User
from api_v1.core import core_exception_handler
from api_v1.serializers import TokenObtainPairSerializer, TokenRefreshSerializer


class TokenObtainPairView(rest_framework_simplejwt.views.TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    queryset = User.objects.filter(is_staff=False)

    def handle_exception(self, exc):
        return core_exception_handler(exc)


class TokenRefreshView(rest_framework_simplejwt.views.TokenRefreshView):
    serializer_class = TokenRefreshSerializer
    queryset = User.objects.filter(is_staff=False)

    def handle_exception(self, exc):
        return core_exception_handler(exc)
