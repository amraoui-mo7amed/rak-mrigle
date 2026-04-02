from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from user_auth.models import UserProfile
from django.db.models import Q
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse
from dashboard.utils import send_account_activation_email
from dashboard.decorator import admin_required
from django.db import transaction
from django.contrib.auth import get_user_model
from dashboard.utils import notify_user

userModel = get_user_model()


@admin_required
def user_list(request):
    query = request.GET.get("q", "")
    status = request.GET.get("status", "")

    users_list = (
        userModel.objects.select_related("profile")
        .exclude(is_superuser=True)
        .order_by("-date_joined")
    )

    if query:
        users_list = users_list.filter(
            Q(email__icontains=query)
            | Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    if status:
        is_approved = status == "approved"
        users_list = users_list.filter(profile__is_approved=is_approved)

    # Pagination
    paginator = Paginator(users_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    status_choices = [
        ("", _("All Status")),
        ("approved", _("Approved")),
        ("pending", _("Pending")),
    ]

    selected_status_label = _("All Status")
    for val, label in status_choices:
        if val == status:
            selected_status_label = label
            break

    context = {
        "page_obj": page_obj,
        "users": page_obj,
        "status_choices": status_choices,
        "query": query,
        "selected_status": status,
        "selected_status_label": selected_status_label,
    }

    return render(request, "users/list.html", context)


@admin_required
def user_details(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    return render(request, "users/details.html", {"profile": profile})


@admin_required
def user_delete(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    if request.method == "POST":
        full_name = profile.user.get_full_name() or profile.user.username
        profile.user.delete()  # Cascade will delete the profile

        return JsonResponse(
            {
                "success": True,
                "message": _("User %(name)s deleted successfully.")
                % {"name": full_name},
                "redirect_url": reverse("dash:user_list"),
            }
        )

    return redirect("dash:user_details", pk=pk)


@admin_required
def user_approve(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    user = get_object_or_404(userModel, pk=profile.user.pk)
    if request.method == "POST":
        try:
            with transaction.atomic():
                profile.is_approved = True
                profile.save()

                # Send notification email
                notify_user(profile.user, str(_("طلب ترقية جديد")) , str(_("تم قبول طلب الترقية")))
                notify_user(profile.user, str(_("New Provider Request")) , str(_("Your request to upgrade to provider has been approved.")))

                return JsonResponse(
                        {
                            "success": True,
                            "message": _(
                                "User %(name)s approved successfully."
                            ) % {
                                "name": profile.user.get_full_name() or profile.user.username
                            },
                        }
                    )

                full_name = profile.user.get_full_name() or profile.user.username
                success_msg = _("User %(name)s approved successfully.") % {
                    "name": full_name
                }
                return JsonResponse({"success": True, "message": success_msg})
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": _("An error occurred during approval: %(error)s")
                    % {"error": str(e)},
                }
            )

    return redirect("dash:user_details", pk=pk)


def user_profile(request):
    user = request.user
    profile = get_object_or_404(UserProfile, user=user)
    return render(request, "user/profile.html", {"user": user, "profile": profile})
