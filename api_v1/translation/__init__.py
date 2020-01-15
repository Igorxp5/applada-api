from django.utils.translation import gettext as _


__all__ = ['error_message']

ERROR_MESSAGES = {
    'null': _('%(label_name)s cannot be null'),
    'blank': _('%(label_name)s cannot be empty'),
}


def error_messages(label_name):
    """
    Return error messages dictionary using translated 
    label name as parameter to format string
    """
    return {c: m % dict(label_name=_(label_name)) for c, m in ERROR_MESSAGES.items()}