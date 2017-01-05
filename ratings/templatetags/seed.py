from django import template

import seed_service_rating

register = template.Library()


@register.simple_tag
def current_version():
    return seed_service_rating.__version__
