from rest_framework import status

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

from api_v1.core import not_found_json


class NotFoundMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if (response.status_code == status.HTTP_404_NOT_FOUND
                and 'application/json' != response.get('Content-Type')):
            return JsonResponse(not_found_json(), status=status.HTTP_404_NOT_FOUND)
        return response