from allauth.socialaccount.models import SocialApp


def social_apps(request):
    """
    Context processor to provide configured social apps to templates.
    """
    configured_providers = []
    try:
        apps = SocialApp.objects.values_list("provider", flat=True)
        configured_providers = list(apps)
    except Exception:
        pass

    return {
        "configured_social_providers": configured_providers,
    }
