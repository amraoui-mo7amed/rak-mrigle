from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext as _, get_language
from django.core.paginator import Paginator
from django.db import transaction
from django.views.decorators.http import require_POST

from dashboard.models import Offer, Category
from dashboard.decorator import admin_required
from dashboard.utils import notify_user


def get_localized_category_choices(categories):
    """Returns category choices localized based on current language."""
    lang = get_language()
    return [(c.pk, c.get_name(lang)) for c in categories]


@admin_required
def offer_list(request):
    query = request.GET.get("q", "")
    status = request.GET.get("status", "")
    category_id = request.GET.get("category", "")

    offers_list = Offer.objects.select_related("provider", "category").order_by(
        "-created_at"
    )

    if query:
        offers_list = (
            offers_list.filter(title_ar__icontains=query)
            | offers_list.filter(title_fr__icontains=query)
            | offers_list.filter(title_en__icontains=query)
        )

    if status:
        offers_list = offers_list.filter(status=status)

    if category_id:
        offers_list = offers_list.filter(category_id=category_id)

    paginator = Paginator(offers_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True)

    status_choices = [
        ("", _("All Status")),
        ("draft", _("Draft")),
        ("pending", _("Pending")),
        ("active", _("Active")),
        ("rejected", _("Rejected")),
        ("expired", _("Expired")),
    ]

    context = {
        "page_obj": page_obj,
        "offers": page_obj,
        "categories": get_localized_category_choices(categories),
        "status_choices": status_choices,
        "query": query,
        "selected_status": status,
        "selected_category": category_id,
    }

    return render(request, "offers/admin/list.html", context)


@admin_required
def offer_details(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    return render(request, "offers/admin/details.html", {"offer": offer})


@admin_required
@require_POST
def offer_approve(request, pk):
    offer = get_object_or_404(Offer, pk=pk)

    try:
        with transaction.atomic():
            offer.status = Offer.OfferStatus.ACTIVE
            offer.save()

            notify_user(
                offer.provider,
                _("Offer Approved"),
                _("Your offer '%(title)s' has been approved and is now active.")
                % {"title": offer.title_ar},
                notification_type="success",
                link=reverse("dash:provider_offer_details", kwargs={"pk": offer.pk}),
            )

            return JsonResponse(
                {
                    "success": True,
                    "message": _("Offer approved successfully."),
                }
            )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": _("An error occurred: %(error)s") % {"error": str(e)},
            }
        )


@admin_required
@require_POST
def offer_reject(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    reason = request.POST.get("reason", "")

    try:
        with transaction.atomic():
            offer.status = Offer.OfferStatus.REJECTED
            offer.admin_note = reason
            offer.save()

            notify_user(
                offer.provider,
                _("Offer Rejected"),
                _("Your offer '%(title)s' has been rejected. Reason: %(reason)s")
                % {"title": offer.title_ar, "reason": reason},
                notification_type="warning",
                link=reverse("dash:provider_offer_details", kwargs={"pk": offer.pk}),
            )

            return JsonResponse(
                {
                    "success": True,
                    "message": _("Offer rejected successfully."),
                }
            )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": _("An error occurred: %(error)s") % {"error": str(e)},
            }
        )


@admin_required
@require_POST
def offer_delete(request, pk):
    offer = get_object_or_404(Offer, pk=pk)

    try:
        title = offer.title_ar
        offer.delete()

        return JsonResponse(
            {
                "success": True,
                "message": _("Offer '%(title)s' deleted successfully.")
                % {"title": title},
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": _("An error occurred: %(error)s") % {"error": str(e)},
            }
        )
