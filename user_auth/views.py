from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db import transaction
from dashboard.utils import notify_user
from django.contrib.auth import get_user_model

from .models import UserProfile
from .utils import (
    create_user_account,
    user_profile_upload_path,
)

userModel = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse_lazy("dash:dash_home"))

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        errors = []

        if not username or not password:
            errors.append(_("Please fill in all required fields."))

        if errors:
            return JsonResponse({"success": False, "errors": errors})

        try:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse(
                    {"success": True, "redirect_url": reverse("dash:dash_home")}
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "errors": [
                            _("Invalid username or password. Please try again.")
                        ],
                    }
                )
        except Exception as e:
            return JsonResponse({"success": False, "errors": [str(e)]})

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("user_auth:login")


def signup_view(request):
    if request.user.is_authenticated:
        return redirect(reverse_lazy("dash:dash_home"))

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        phone_number = request.POST.get("phone_number", "")
        role = request.POST.get("role")
        driver_license = request.FILES.get("driver_license")

        errors = []

        if not first_name:
            errors.append(_("First name is required."))
        if not last_name:
            errors.append(_("Last name is required."))
        if not email:
            errors.append(_("Email is required."))
        if not password:
            errors.append(_("Password is required."))
        if password != confirm_password:
            errors.append(_("Passwords do not match."))
        elif len(password) < 8:
            errors.append(_("Password must be at least 8 characters long."))
        if not role:
            errors.append(_("Please select a role."))
        if role == "provider" and not driver_license:
            errors.append(_("Driver license is required for providers."))

        if errors:
            return JsonResponse({"success": False, "errors": errors})

        if User.objects.filter(username=email).exists():
            return JsonResponse(
                {"success": False, "errors": [_("This email is already registered.")]}
            )

        try:
            user_data = {
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
            }
            profile_data = {
                "phone_number": phone_number,
            }

            with transaction.atomic():
                admins = userModel.objects.filter(is_superuser=True)
                user = create_user_account(
                    user_data, profile_data, None, role=role, driver_license=driver_license
                )

                for admin in admins:
                    notify_user(admins, _("New user has been created, please review it .", link=reverse("dash:user_details", pk=user.profile.pk)))

                return JsonResponse(
                    {
                        "success": True,
                        "message": _("Your account has been created successfully."),
                        "redirect_url": reverse("user_auth:login"),
                    }
                )
        except Exception as e:
            return JsonResponse({"success": False, "errors": [str(e)]})

    return render(
        request,
        "auth/signup.html",
        {
            "role_choices": UserProfile.roleChoices.choices,
        },
    )


@login_required
def profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "is_approved": True,
            "role": "customer",
        },
    )

    if request.method == "POST":
        first_name = request.POST.get("first_name", user.first_name)
        last_name = request.POST.get("last_name", user.last_name)
        phone_number = request.POST.get("phone_number", profile.phone_number)
        bio = request.POST.get("bio", profile.bio)
        address = request.POST.get("address", profile.address)
        birth_date = request.POST.get("birth_date") or None
        sex = request.POST.get("sex") if not profile.sex else profile.sex
        role = request.POST.get("role", profile.role)
        driver_license = request.FILES.get("driver_license")
        profile_picture = request.FILES.get("profile_picture")

        errors = []

        if not first_name:
            errors.append(_("First name is required."))
        if not last_name:
            errors.append(_("Last name is required."))
        if not phone_number:
            errors.append(_("Phone number is required."))
        if role == "provider" and not profile.driver_license and not driver_license:
            errors.append(_("Driver license is required for providers."))

        if errors:
            return JsonResponse({"success": False, "errors": errors})

        try:
            with transaction.atomic():
                user.first_name = first_name
                user.last_name = last_name
                user.save()

                profile.phone_number = phone_number
                profile.bio = bio
                profile.address = address
                profile.birth_date = birth_date
                profile.sex = sex

                if role and not profile.role:
                    profile.role = role

                if driver_license:
                    profile.driver_license = driver_license

                if profile_picture:
                    profile.profile_picture = profile_picture

                profile.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": _("Profile updated successfully."),
                    "redirect_url": reverse("user_auth:profile"),
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "errors": [str(e)]})

    context = {
        "profile": profile,
        "role_choices": UserProfile.roleChoices.choices,
        "sex_choices": UserProfile.sexChoices.choices,
    }
    return render(request, "user/profile.html", context)


@login_required
def upgrade_to_provider(request):
    if request.method == "POST":
        profile = request.user.profile
        driver_license = request.FILES.get("driver_license")

        if not driver_license:
            return JsonResponse(
                {"success": False, "errors": [_("Driver license is required.")]}
            )

        if profile.role == "provider":
            return JsonResponse(
                {"success": False, "errors": [_("You are already a provider.")]}
            )

        try:
            profile.driver_license = driver_license
            profile.role = "provider"
            profile.is_approved = False
            profile.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": _(
                        "Congratulations! Your account has been upgraded to Provider. Please wait for approval."
                    ),
                    "redirect_url": reverse("user_auth:profile"),
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "errors": [str(e)]})

    return redirect("user_auth:profile")


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        try:
            user.delete()
            return JsonResponse(
                {
                    "success": True,
                    "message": _("Your account has been deleted successfully."),
                    "redirect_url": reverse("user_auth:login"),
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "errors": [str(e)]})

    return redirect("user_auth:profile")
