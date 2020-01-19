from rest_framework import filters, status
from rest_framework.response import Response

from api_v1.models import Match, MatchStatus
from api_v1.utils.validation import validate_required_params, validate_location, \
                                    validate_float_values, validate_radius

from django.contrib.gis.geos import Point
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.contrib.gis.measure import Distance as D
from django.contrib.gis.db.models.functions import Distance


class LocationRangeFilter(filters.BaseFilterBackend):
    """
    Filter to get objects by location range (centerpoint latitude, 
    centerpoint longitude and range). Range parameter must be in km.
    """
    def filter_queryset(self, request, queryset, view):
        params = validate_required_params(request.query_params, ('latitude', 'longitude'))
        params['radius'] = request.query_params.get('radius', '15')
        
        params = validate_float_values(params)
        params['radius'] = validate_radius(params['radius'])

        origin = validate_location(params)
        
        location_distance = (origin, D(km=params['radius']))
        result = Match.objects.filter(location__distance_lte=location_distance)
        return result.annotate(distance=Distance('location', origin)).order_by('-distance')


class MatchStatusFilter(filters.BaseFilterBackend):
    """
    Filter match object by status value.
    """
    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('status'):
            status_value = request.query_params.get('status')
            if status_value:
                try:
                    match_status = MatchStatus(status_value)
                except ValueError:
                    raise ValidationError({'status': [_('Choose a valid status value')]})
                queryset_filter = match_status.get_queryset_filter()
                return queryset.filter(**queryset_filter)
        return queryset

