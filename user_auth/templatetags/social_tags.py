from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def safe_provider_login_url(context, provider):
    """
    Returns the social login URL if the provider is configured,
    otherwise returns a placeholder URL that shows an error message.
    """
    try:
        from allauth.socialaccount.adapter import get_adapter

        adapter = get_adapter(context["request"])
        app = adapter.get_app(context["request"], provider=provider)
        return reverse(f"{provider}_login")
    except Exception:
        return "#"
