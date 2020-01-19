import traceback

import django.core.exceptions

from django.conf import settings
from django.http import HttpResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken

from django.utils.translation import gettext as _


ERROR_MESSAGES = {
    'null': _('%s cannot be null'),
    'blank': _('%s cannot be empty'),
    'required': _('%s is required'),
}


def core_exception_handler(exc, context=None):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    
    if response is None:
        if isinstance(exc, ValidationError) or isinstance(exc, django.core.exceptions.ValidationError):
            response = Response({'errors': [_('Bad input parameters')]}, status=status.HTTP_400_BAD_REQUEST)
        elif settings.DEBUG:
            return HttpResponse(traceback.format_exc(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return resource_not_found_response()

    if response.status_code == status.HTTP_404_NOT_FOUND:
        return resource_not_found_response()

    if isinstance(exc, ValidationError) or isinstance(exc, django.core.exceptions.ValidationError):
        errors = getattr(exc, 'detail', None)
        errors = errors if errors else exc.args[0] 
        if isinstance(errors, str):
            response.data = {'errors': [errors]}
        elif isinstance(errors, list) or isinstance(errors, tuple):
            response.data = {'errors': errors}
        else:
            if errors:
                response.data = {'errors': [__translate_error(f, e) for f, ers in errors.items() for e in ers]}

    if response.status_code >= 400 and 'detail' in response.data:
        response.data = {'errors': [response.data['detail']]}

    return response


def __translate_error(field, error):
    if hasattr(error, 'code') and error.code in ERROR_MESSAGES:
        return _(ERROR_MESSAGES[error.code]) % _(field.replace('_', ' ')).capitalize() 
    return _(error)


def resource_not_found_response():
    return Response({'errors': [_('Resource or item not found')]}, 
                           status=status.HTTP_404_NOT_FOUND)