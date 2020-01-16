from rest_framework.views import exception_handler
from rest_framework import status


def core_exception_handler(exc, context=None):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response.status_code == status.HTTP_404_NOT_FOUND:
        del response.data['detail']
        response.data['errors'] = ['Resource or item not found']

    return response