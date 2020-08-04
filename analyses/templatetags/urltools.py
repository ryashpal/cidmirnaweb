import os

from django import template
from django.conf import settings

register = template.Library()

@register.filter
def internalise_url(url):
    """
    Convert a URL from the external url to the internal
    """
    if getattr(settings, 'INTERNAL_BASE_URL'):
        return url.replace(settings.EXTERNAL_BASE_URL, settings.INTERNAL_BASE_URL)
    else:
        return url
