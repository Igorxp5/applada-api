from django.http.response import Http404
from django.db.utils import IntegrityError 
from django.utils.translation import gettext as _

from psycopg2 import errorcodes

from rest_framework import generics, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination

from api_v1.models import User, Match, MatchSubscription
from api_v1.filters import LocationRangeFilter, MatchStatusFilter
from api_v1.serializers import MatchSerializer, MatchSubscriptionSerializer
from api_v1.core import IsAuthenticated, IsOwnerOrReadOnly, IsOwnerUser, \
                        IsMatchSubscriptionUserOrReadOnly


class MatchRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == status.HTTP_404_NOT_FOUND: 
            response.data['errors'] = [_('Match not found')]
        return response


class MatchCreateSearch(generics.ListCreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    filter_backends = (LocationRangeFilter, MatchStatusFilter)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.order_by('-created_date')


class UsersMatch(generics.ListCreateAPIView):
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    serializer_class = MatchSerializer
    filter_backends = (MatchStatusFilter,)
    permission_classes = (IsAuthenticated, IsOwnerUser)

    def get_queryset(self):
        user = User.objects.get(username=self.kwargs['username'])
        return Match.objects.filter(matchsubscription__user=user)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.order_by('-created_date')
    
    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == status.HTTP_404_NOT_FOUND: 
            response.data['errors'] = [_('User not found')]
        return response


class MatchSubscriptionView(mixins.CreateModelMixin,
                            mixins.DestroyModelMixin,
                            generics.ListAPIView):
    serializer_class = MatchSubscriptionSerializer
    permission_classes = (IsAuthenticated, IsMatchSubscriptionUserOrReadOnly)

    def get_queryset(self):
        match = Match.objects.get(id=self.kwargs['pk'])
        return MatchSubscription.objects.filter(user=self.request.user, match=match)
    
    def get_object(self):
        match = Match.objects.get(id=self.kwargs['pk'])
        return MatchSubscription.objects.get(user=self.request.user, match=match)
    
    def post(self, request, *args, **kwargs):
        request.data['match_id'] = self.kwargs['pk']
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(exc, MatchSubscription.DoesNotExist):
            response.status_code = status.HTTP_400_BAD_REQUEST
            response.data['errors'] = [_('You are not subscribed for this match')]
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            response.data['errors'] = [_('Match not found')]
        return response