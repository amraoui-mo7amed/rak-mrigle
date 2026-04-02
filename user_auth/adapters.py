import requests
from datetime import date
from django.core.files.base import ContentFile
from django.db.transaction import atomic
from django.urls import reverse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import UserProfile
from django.contrib.auth import get_user_model
from dashboard.utils import notify_user
from django.utils.translation import gettext_lazy as _

userModel = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        if not hasattr(user, "profile"):
            data = sociallogin.account.extra_data
            provider = sociallogin.account.provider

            access_token = None
            if sociallogin.token:
                access_token = sociallogin.token.token

            phone_number = ""
            gender = None
            birth_date = None
            address = ""

            if provider == "google" and access_token:
                profile_data = self.get_google_profile_data(access_token)
                phone_number = profile_data.get("phone_number", "")
                gender = profile_data.get("gender")
                birth_date = profile_data.get("birth_date")
                address = profile_data.get("address", "")

            profile_picture = self.get_profile_picture(data, provider, user)

            with atomic():
                try:
                    user.first_name = data.get("given_name", "") or data.get(
                        "first_name", ""
                    )
                    user.last_name = data.get("family_name", "") or data.get(
                        "last_name", ""
                    )
                    user.save()

                    profile, created = UserProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            "phone_number": phone_number or "",
                            "sex": gender,
                            "birth_date": birth_date,
                            "address": address,
                            "is_approved": True,
                            "role": "customer",
                        },
                    )

                    if profile_picture:
                        profile.profile_picture = profile_picture
                        profile.save()

                    # Notify Admins 
                    admins = userModel.objects.filter(is_superuser=True)
                    for admin in admins:
                        notify_user(admin, str(_("تم تسجيل مستخدم جديد" )), str(_("تم تسجيل مستخدم جديد, يرجى مراجعته")), link=reverse("dash:user_details", kwargs={"pk":user.profile.pk}))
                        notify_user(admin, str(_("New user has been created")),  str(_("New user has been created, please review it .")), link=reverse("dash:user_details", kwargs={"pk":user.profile.pk}))
                except Exception as e:
                    print(f"Error creating user profile: {e}")
        return user

    def get_google_profile_data(self, access_token):
        data = {}
        try:
            response = requests.get(
                "https://people.googleapis.com/v1/people/me",
                params={"personFields": "phoneNumbers,genders,birthdays,addresses"},
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            print(f"Google People API status: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"Google People API response: {user_data}")

                phone_numbers = user_data.get("phoneNumbers", [])
                if phone_numbers:
                    data["phone_number"] = phone_numbers[0].get("value")

                genders = user_data.get("genders", [])
                if genders:
                    gender_value = genders[0].get("value", "").lower()
                    if gender_value in ["male", "m", "1"]:
                        data["gender"] = "male"
                    elif gender_value in ["female", "f", "2"]:
                        data["gender"] = "female"
                    elif gender_value in ["unspecified", "unknown"]:
                        data["gender"] = None
                    else:
                        data["gender"] = gender_value

                birthdays = user_data.get("birthdays", [])
                if birthdays:
                    bdate = birthdays[0].get("date", {})
                    if bdate:
                        year = bdate.get("year")
                        month = bdate.get("month")
                        day = bdate.get("day")
                        if year and month and day:
                            data["birth_date"] = date(year, month, day)

                addresses = user_data.get("addresses", [])
                if addresses:
                    data["address"] = addresses[0].get("formattedValue") or addresses[
                        0
                    ].get("streetAddress")
            else:
                print(f"Google People API error: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Google People API exception: {e}")
        return data

    def get_profile_picture(self, data, provider, user):
        picture_url = None

        if provider == "google":
            picture_url = data.get("picture") or data.get("avatar", {}).get("url")
        elif provider == "facebook":
            picture_data = data.get("picture", {})
            if picture_data:
                if isinstance(picture_data, dict):
                    picture_url = picture_data.get("data", {}).get("url")
                elif isinstance(picture_data, str):
                    picture_url = picture_data
            if not picture_url:
                picture_url = (
                    f"https://graph.facebook.com/{data.get('id')}/picture?type=large"
                )

        if picture_url:
            try:
                response = requests.get(picture_url, timeout=10)
                if response.status_code == 200:
                    ext = self.get_extension(
                        picture_url, response.headers.get("content-type", "")
                    )
                    filename = f"user_{user.id}_social{ext}"
                    return ContentFile(
                        response.content, name=f"profile_pictures/{filename}"
                    )
            except requests.exceptions.RequestException:
                pass

        return None

    def get_extension(self, url, content_type):
        if "jpeg" in content_type or "jpg" in content_type:
            return ".jpg"
        elif "png" in content_type:
            return ".png"
        elif "gif" in content_type:
            return ".gif"
        elif "webp" in content_type:
            return ".webp"
        elif ".jpg" in url or ".jpeg" in url:
            return ".jpg"
        elif ".png" in url:
            return ".png"
        elif ".gif" in url:
            return ".gif"
        else:
            return ".jpg"

    def get_login_redirect_url(self, request):
        user = request.user
        if hasattr(user, "profile") and not user.profile.phone_number:
            return reverse("user_auth:profile")
        return reverse("dash:dash_home")
