from api_v1.models import User
from rest_framework import generics
from api_v1.serializers import UserSerializer
from api_v1.utils import core_exception_handler
from django.http.response import Http404


class UsersSearch(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()


class UserRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def handle_exception(self, exc):
        response = core_exception_handler(exc)
        if isinstance(exc, Http404):
            response.data['errors'] = ['User not found']
        return response

