from django.http.response import Http404
from django.utils.translation import gettext as _

from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination

from api_v1.models import Match
from api_v1.core import IsAuthenticated, IsOwnerOrReadOnly
from api_v1.serializers import MatchSerializer
from api_v1.filters import LocationRangeFilter, MatchStatusFilter


class MatchRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(exc, Http404):
            response.data['errors'] = [_('Match not found')]
        return response


class MatchCreateSearch(generics.ListCreateAPIView):
    ordering = '-id'
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (LocationRangeFilter, MatchStatusFilter)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
