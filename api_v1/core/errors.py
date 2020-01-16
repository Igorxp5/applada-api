from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken


def core_exception_handler(exc, context=None):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    
    if response is None:
        return exc

    if response.status_code == status.HTTP_404_NOT_FOUND:
        response.data['detail'] = 'Resource or item not found'

    if isinstance(exc, ValidationError):
        response.data = {'errors': [e for errors in exc.detail.values() for e in errors]}

    if response.status_code >= 400 and 'detail' in response.data:
        response.data = {'errors': [response.data['detail']]}

    return response
