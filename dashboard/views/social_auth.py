from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.sites.models import Site
from django.db import transaction
from allauth.socialaccount.models import SocialApp
from dashboard.decorator import admin_required
from django.views.decorators.http import require_POST


PROVIDER_CHOICES = [
    ("google", "Google"),
    ("facebook", "Facebook"),
]


@admin_required
def social_app_list(request):
    social_apps = SocialApp.objects.all().order_by("provider")

    configured_providers = set(social_apps.values_list("provider", flat=True))
    available_providers = [
        (key, label)
        for key, label in PROVIDER_CHOICES
        if key not in configured_providers
    ]

    context = {
        "social_apps": social_apps,
        "available_providers": available_providers,
        "provider_labels": dict(PROVIDER_CHOICES),
    }
    return render(request, "social_auth/list.html", context)


@admin_required
def social_app_create(request):
    if request.method == "POST":
        provider = request.POST.get("provider")
        name = request.POST.get("name", "").strip()
        client_id = request.POST.get("client_id", "").strip()
        secret = request.POST.get("secret", "").strip()

        if not all([provider, client_id, secret]):
            return JsonResponse(
                {
                    "success": False,
                    "errors": [_("All fields are required.")],
                }
            )

        if SocialApp.objects.filter(provider=provider).exists():
            return JsonResponse(
                {
                    "success": False,
                    "errors": [_("A configuration for this provider already exists.")],
                }
            )

        try:
            with transaction.atomic():
                social_app = SocialApp.objects.create(
                    provider=provider,
                    name=name or dict(PROVIDER_CHOICES).get(provider, provider),
                    client_id=client_id,
                    secret=secret,
                )
                social_app.sites.add(Site.objects.get_current())

            return JsonResponse(
                {
                    "success": True,
                    "message": _("Social authentication configured successfully."),
                    "redirect_url": reverse("dash:social_app_list"),
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "errors": [
                        _("Failed to create configuration: %(error)s")
                        % {"error": str(e)}
                    ],
                }
            )

    return redirect("dash:social_app_list")


@admin_required
def social_app_update(request, pk):
    social_app = get_object_or_404(SocialApp, pk=pk)

    if request.method == "POST":
        client_id = request.POST.get("client_id", "").strip()
        secret = request.POST.get("secret", "").strip()

        if not all([client_id, secret]):
            return JsonResponse(
                {
                    "success": False,
                    "errors": [_("All fields are required.")],
                }
            )

        try:
            social_app.client_id = client_id
            social_app.secret = secret
            social_app.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": _("Configuration updated successfully."),
                    "redirect_url": reverse("dash:social_app_list"),
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "errors": [
                        _("Failed to update configuration: %(error)s")
                        % {"error": str(e)}
                    ],
                }
            )

    return redirect("dash:social_app_list")


@admin_required
@require_POST
def social_app_delete(request, pk):
    social_app = get_object_or_404(SocialApp, pk=pk)
    provider_name = dict(PROVIDER_CHOICES).get(social_app.provider, social_app.provider)

    try:
        social_app.delete()
        return JsonResponse(
            {
                "success": True,
                "message": _("%(provider)s configuration deleted successfully.")
                % {"provider": provider_name},
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": _("Failed to delete configuration: %(error)s")
                % {"error": str(e)},
            }
        )
