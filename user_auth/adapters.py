from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import UserProfile


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """
        Populate the User object and create a UserProfile for social signups.
        """
        user = super().save_user(request, sociallogin, form)

        # Check if the profile already exists
        if not hasattr(user, "profile"):
            # Extract data from social login
            data = sociallogin.account.extra_data
            provider = sociallogin.account.provider

            phone_number = ""
            sex = None
            # You could potentially extract more from provider-specific data
            # For now, we create a basic profile

            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "phone_number": phone_number,
                    "sex": sex,
                    "is_approved": True,  # Social logins are usually pre-verified
                },
            )

        return user
