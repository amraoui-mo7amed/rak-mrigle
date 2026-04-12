from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _
from django_eventstream import send_event
from .models import Notification
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


from decouple import config


def get_wilayas_choices():
    """
    Load wilayas from algeria.json and return as choices list.
    Returns list of tuples based on current language.
    """
    from django.utils.translation import get_language

    json_path = Path(__file__).parent.parent / "algeria.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            wilayas = json.load(f)

        lang = get_language()
        if lang == "ar":
            return [(w["ar_name"], w["ar_name"]) for w in wilayas]
        else:
            return [(w["name"], w["name"]) for w in wilayas]
    except Exception as e:
        logger.error(f"Failed to load wilayas: {str(e)}")
        return []


def get_localized_wilaya_name(wilaya_name):
    """
    Get localized wilaya name from algeria.json.

    Args:
        wilaya_name: The wilaya name (in any language)

    Returns:
        Localized wilaya name based on current language
    """
    from django.utils.translation import get_language

    json_path = Path(__file__).parent.parent / "algeria.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            wilayas = json.load(f)

        lang = get_language()
        for w in wilayas:
            if w["name"] == wilaya_name or w["ar_name"] == wilaya_name:
                if lang == "ar":
                    return w["ar_name"]
                else:
                    return w["name"]
        return wilaya_name
    except Exception as e:
        logger.error(f"Failed to get localized wilaya: {str(e)}")
        return wilaya_name


def get_localized_category_choices(categories):
    """
    Get category choices based on current language.

    Args:
        categories: QuerySet of Category objects

    Returns:
        List of tuples (id, localized_name)
    """
    from django.utils.translation import get_language

    lang = get_language()
    return [(cat.id, cat.get_name(lang)) for cat in categories]


def get_status_choices():
    """
    Get localized status choices for ServiceRequest.

    Returns:
        List of tuples (value, localized_label)
    """
    from django.utils.translation import gettext_lazy as _
    from .models import ServiceRequest

    return [
        (ServiceRequest.RequestStatus.PENDING, _("Pending")),
        (ServiceRequest.RequestStatus.APPROVED, _("Approved")),
        (ServiceRequest.RequestStatus.REJECTED, _("Rejected")),
        (ServiceRequest.RequestStatus.CANCELLED, _("Cancelled")),
    ]


def send_account_activation_email(request, profile):
    """
    Sends an account activation email to the user after approval.
    """
    site_name = config("SITE_NAME", default="StarterKit")
    subject = _("Your %(site)s Account has been Activated!") % {"site": site_name}
    login_url = request.build_absolute_uri(reverse("user_auth:login"))

    context = {
        "profile": profile,
        "login_url": login_url,
        "LANGUAGE_CODE": getattr(request, "LANGUAGE_CODE", settings.LANGUAGE_CODE),
    }

    html_content = render_to_string("email/account_activation.html", context)
    text_content = strip_tags(html_content)

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")

    email = EmailMultiAlternatives(
        subject, text_content, from_email, [profile.user.email]
    )
    email.attach_alternative(html_content, "text/html")

    try:
        print(f"DEBUG: Attempting to send email to {profile.user.email}")
        print(f"DEBUG: Subject: {subject}")
        print(f"DEBUG: From: {from_email}")
        print(
            f"DEBUG: Email Backend: {settings.EMAIL_BACKEND if hasattr(settings, 'EMAIL_BACKEND') else 'Default'}"
        )

        email.send()
        print("DEBUG: Email sent successfully!")
        return True
    except Exception as e:
        # In a real production app, we would log this properly
        print(f"DEBUG: Failed to send email to {profile.user.email}")
        print(f"DEBUG: Exception type: {type(e).__name__}")
        print(f"DEBUG: Exception message: {str(e)}")
        import traceback

        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return False


def notify_user(user, title, message, notification_type="info", link=""):
    """
    Create a notification for a user and send it via eventstream.

    Args:
        user: The user to notify
        title: Notification title
        message: Notification message
        notification_type: One of 'info', 'success', 'warning', 'error'
        link: Optional link to navigate to when clicked

    Returns:
        The created Notification instance
    """
    try:
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
        )

        channel = f"user-{user.id}"
        event_data = {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.notification_type,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
            "link": notification.link,
        }

        send_event(channel, "notification", event_data)

        logger.info(f"Notification sent to user {user.username}: {title}")
        return notification

    except Exception as e:
        logger.error(
            f"Failed to create notification for user {user.username}: {str(e)}"
        )
        return None


def send_bilingual_notification(
    user,
    title_ar,
    title_en,
    message_ar,
    message_en,
    link="",
    notification_type="warning",
):
    """
    Send notification in both Arabic and English.

    Args:
        user: The user to notify
        title_ar: Arabic title
        title_en: English title
        message_ar: Arabic message
        message_en: English message
        link: Optional link to navigate to when clicked
        notification_type: Type of notification
    """
    notify_user(
        user, title_ar, message_ar, notification_type=notification_type, link=link
    )
    notify_user(
        user, title_en, message_en, notification_type=notification_type, link=link
    )


def get_or_create_commission_balance(provider):
    """
    Get or create commission balance for provider.

    Args:
        provider: User instance (provider role)

    Returns:
        CommissionBalance instance
    """
    from django.db import transaction
    from .models import CommissionBalance

    balance, created = CommissionBalance.objects.get_or_create(provider=provider)
    return balance


def add_commission(provider, service_request, offer):
    """
    Add commission when provider approves a request.
    Commission = 1% of offer's base_price

    Args:
        provider: User instance (provider)
        service_request: ServiceRequest instance
        offer: Offer instance

    Returns:
        tuple: (balance, threshold_reached)
    """
    from decimal import Decimal
    from django.db import transaction
    from .models import CommissionBalance, CommissionTransaction, Offer

    commission_amount = offer.base_price * Decimal("0.01")

    with transaction.atomic():
        CommissionTransaction.objects.create(
            provider=provider,
            service_request=service_request,
            offer=offer,
            amount=commission_amount,
        )

        balance = get_or_create_commission_balance(provider)
        balance.total_commission += commission_amount
        balance.save()

        threshold_reached = balance.total_commission >= Decimal("1000")

        if threshold_reached and not balance.is_blocked:
            balance.is_blocked = True
            balance.save()

            offer.status = Offer.OfferStatus.PENDING
            offer.is_available = False
            offer.save()

        return balance, threshold_reached


def suspend_offer(offer):
    """
    Suspend an offer.

    Args:
        offer: Offer instance
    """
    from .models import Offer

    offer.status = Offer.OfferStatus.PENDING
    offer.is_available = False
    offer.save()


def reactivate_offer(offer):
    """
    Reactivate an offer after payment.

    Args:
        offer: Offer instance
    """
    from .models import Offer

    offer.status = Offer.OfferStatus.ACTIVE
    offer.is_available = True
    offer.save()
