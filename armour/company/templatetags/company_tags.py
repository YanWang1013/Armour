from django import template
from ..models import Topic, Location

register = template.Library()


@register.filter
def in_list(value, values):
    if not values:
        return False

    val = str(value)
    valint = int(val)

    if val in values or valint in values:
        return True
    return False


@register.filter
def is_topic_active(value, ):
    return Topic.objects.get(id=value).published


@register.filter
def is_location_active(value, ):
    return Location.objects.get(id=value).published


@register.filter
def repr_string(value, ):
    return repr(value).replace("'", '')
