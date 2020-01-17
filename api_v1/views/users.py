from django.http.response import Http404
from django.utils.translation import gettext as _

from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination

from api_v1.models import User
from api_v1.core import IsAuthenticated
from api_v1.serializers import UserSerializer
from api_v1.core import IsOwnerUser, core_exception_handler 


class UsersSearch(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        search = self.request.query_params.get('search') or None
        return User.objects.filter(username__icontains=search, is_staff=False) \
             | User.objects.filter(first_name__icontains=search, is_staff=False)
    
    def handle_exception(self, exc):
        return core_exception_handler(exc)


class UserRetrieveUpdate(generics.RetrieveUpdateAPIView):
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (IsAuthenticated,)
        if self.request.method in ('PATCH', 'PUT'):
            self.permission_classes = (IsAuthenticated, IsOwnerUser)
        return super().get_permissions()
    
    def handle_exception(self, exc):
        response = core_exception_handler(exc)
        if isinstance(exc, Http404):
            response.data['errors'] = [_('User not found')]
        return response

