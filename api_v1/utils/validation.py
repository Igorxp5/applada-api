from copy import deepcopy

from django.contrib.gis.geos import Point
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError


def validate_required_params(params, required_params):
    params = deepcopy(params)
    missing_params = [p for p in required_params if p not in params]
    if missing_params:
        raise ValidationError({p: [ValidationError(p, code='required')] for p in missing_params})
    return params

def validate_location(location_dict):
    params = validate_required_params(location_dict, ('latitude', 'longitude'))
    location_dict = validate_float_values(location_dict)

    try:
        location = Point(params['longitude'], params['latitude'])
    except TypeError:
        raise ValidationError(_('Invalid geo coordinates'))
    
    return location

def validate_radius(radius):
    radius = validate_float_values({'radius': radius})['radius']
    if radius < 1 or radius > 15:
        raise ValidationError({'radius': [_('Radius must be a value from 1 to 15')]})
    return radius

def validate_float_values(values_dict):
    values_dict = deepcopy(values_dict)
    errors = {p: [] for p in values_dict}

    for param, value in values_dict.items():
        try:
            values_dict[param] = float(value)
        except ValueError:
            error = _('%(label_name)s must be a float number') % dict(label_name=param.capitalize())
            errors[param].append(error)
    
    if any(len(e) > 0 for e in errors.values()):
        raise ValidationError(errors)
    
    return values_dict