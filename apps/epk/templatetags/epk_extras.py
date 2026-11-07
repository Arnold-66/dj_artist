"""
Custom template filters for the EPK app.

Load in a template with:

    {% load epk_extras %}

The app must be listed in INSTALLED_APPS as "apps.epk" (or "epk"),
matching the folder name used in the project, otherwise Django will
not auto-discover this templatetags package.
"""

from django import template

register = template.Library()


@register.filter(name="get_item")
def get_item(mapping, key):
    """
    Safely fetch ``mapping[key]``.

    Returns ``None`` when:
      * ``mapping`` is None
      * ``mapping`` has no ``.get`` method
      * the key is absent
      * any other unexpected error occurs

    Never raises — templates must not crash on lookup misses.
    """
    if mapping is None:
        return None

    getter = getattr(mapping, "get", None)
    if getter is None:
        return None

    try:
        return getter(key)
    except (KeyError, TypeError, AttributeError):
        return None