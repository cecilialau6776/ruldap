import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


# stolen from https://github.com/mozilla/mozilla-django-oidc/blob/3.0.0/mozilla_django_oidc/utils.py#L23
def import_from_settings(attr, *args):
    """
    Load an attribute from the django settings.

    :raises:
        ImproperlyConfigured
    """
    try:
        if args:
            return getattr(settings, attr, args[0])
        return getattr(settings, attr)
    except AttributeError:
        raise ImproperlyConfigured("Setting {0} not found".format(attr))
