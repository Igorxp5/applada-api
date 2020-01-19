from django.http.response import Http404
from django.utils.translation import gettext as _

from rest_framework import generics, filters
from rest_framework.pagination import LimitOffsetPagination

from api_v1.models import User
from api_v1.core import IsAuthenticated
from api_v1.serializers import UserSerializer
from api_v1.core import IsOwnerUser 


class UsersSearch(generics.ListAPIView):
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ['username', 'first_name']


class UserRetrieveUpdate(generics.RetrieveUpdateAPIView):
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwnerUser)

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(exc, Http404):
            response.data['errors'] = [_('User not found')]
        return response

