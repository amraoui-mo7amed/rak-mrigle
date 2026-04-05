from django import template
from django.utils.translation import get_language

register = template.Library()


@register.inclusion_tag("components/pagination.html", takes_context=True)
def render_pagination(context, page_obj):
    request = context["request"]
    querydict = request.GET.copy()
    if "page" in querydict:
        querydict.pop("page")

    base_url = request.path + "?" + querydict.urlencode()
    if base_url and not base_url.endswith("&") and not base_url.endswith("?"):
        base_url += "&"

    return {
        "page_obj": page_obj,
        "base_url": base_url,
    }


@register.filter
def humanize_number(value):
    """
    Converts a large number into a human-readable format with k, M, B, etc.
    Example:
        1500 -> 1.5k
        2500000 -> 2.5M
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        return value

    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}k"
    else:
        return f"{num:.0f}"


@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using variable key.
    Usage: {{ mydict|get_item:key }}
    """
    if dictionary is None:
        return None
    if not isinstance(dictionary, dict):
        return dictionary
    return dictionary.get(key)


@register.filter
def localized_name(obj):
    """
    Returns the name based on current active language.
    Works with Category, Offer models and any model with get_name method.
    Usage: {{ category|localized_name }}
    """
    lang = get_language()
    if hasattr(obj, "get_name"):
        return obj.get_name(lang)
    return str(obj)
