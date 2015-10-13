import os

from django import template
from django.conf import settings

from util.file_stat import bytes2human, bytes2harddrive
from util.remote import Remote

register = template.Library()

@register.filter
def internalise_url(url):
    """
    Convert a URL from the external url to the internal
    """
    return url.replace(settings.EXTERNAL_BASE_URL, settings.INTERNAL_BASE_URL)
