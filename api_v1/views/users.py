from django.http.response import Http404
from django.utils.translation import gettext as _

from rest_framework import generics

from api_v1.models import User
from api_v1.core import IsAuthenticated
from api_v1.serializers import UserSerializer
from api_v1.core import core_exception_handler


class UsersSearch(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(is_staff=False)


class UserRetrieveUpdate(generics.RetrieveUpdateAPIView):
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    
    def handle_exception(self, exc):
        response = core_exception_handler(exc)
        if isinstance(exc, Http404):
            response.data['errors'] = [_('User not found')]
        return response

