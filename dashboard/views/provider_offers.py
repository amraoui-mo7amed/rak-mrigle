from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext as _, get_language
from django.core.paginator import Paginator
from django.db import transaction
from django.views.decorators.http import require_POST, require_http_methods

from dashboard.models import Offer, Category
from dashboard.decorator import provider_required


def get_localized_category_choices(categories):
    """Returns category choices localized based on current language."""
    lang = get_language()
    return [(c.pk, c.get_name(lang)) for c in categories]


@provider_required
def provider_offer_list(request):
    query = request.GET.get("q", "")
    status = request.GET.get("status", "")

    offers_list = (
        Offer.objects.filter(provider=request.user)
        .select_related("category")
        .order_by("-created_at")
    )

    if query:
        offers_list = (
            offers_list.filter(title_ar__icontains=query)
            | offers_list.filter(title_fr__icontains=query)
            | offers_list.filter(title_en__icontains=query)
        )

    if status:
        offers_list = offers_list.filter(status=status)

    paginator = Paginator(offers_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    status_choices = [
        ("", _("All Status")),
        ("draft", _("Draft")),
        ("pending", _("Pending")),
        ("active", _("Active")),
        ("rejected", _("Rejected")),
        ("expired", _("Expired")),
    ]

    categories = Category.objects.filter(is_active=True)

    context = {
        "page_obj": page_obj,
        "offers": page_obj,
        "status_choices": status_choices,
        "categories": get_localized_category_choices(categories),
        "query": query,
        "selected_status": status,
    }

    return render(request, "offers/provider/list.html", context)


@provider_required
def provider_offer_create(request):
    categories = Category.objects.filter(is_active=True)

    if request.method == "POST":
        errors = []
        title_ar = request.POST.get("title_ar", "").strip()
        title_fr = request.POST.get("title_fr", "").strip()
        title_en = request.POST.get("title_en", "").strip()
        description_ar = request.POST.get("description_ar", "").strip()
        description_fr = request.POST.get("description_fr", "").strip()
        description_en = request.POST.get("description_en", "").strip()
        category_id = request.POST.get("category", "").strip()
        pricing_type = request.POST.get("pricing_type", "").strip()
        base_price = request.POST.get("base_price", "").strip()
        price_per_km = request.POST.get("price_per_km", "").strip() or None
        price_per_hour = request.POST.get("price_per_hour", "").strip() or None
        fuel_cost = request.POST.get("fuel_cost", "").strip() or None
        operator_cost = request.POST.get("operator_cost", "").strip() or None
        wait_time_cost = request.POST.get("wait_time_cost", "").strip() or None
        capacity = request.POST.get("capacity", "").strip()
        location_ar = request.POST.get("location_ar", "").strip()
        location_fr = request.POST.get("location_fr", "").strip()
        location_en = request.POST.get("location_en", "").strip()
        is_available = request.POST.get("is_available") == "on"
        action = request.POST.get("action", "draft")

        if not title_ar:
            errors.append(_("Title in Arabic is required."))
        if not title_fr:
            errors.append(_("Title in French is required."))
        if not title_en:
            errors.append(_("Title in English is required."))
        if not description_ar:
            errors.append(_("Description in Arabic is required."))
        if not description_fr:
            errors.append(_("Description in French is required."))
        if not description_en:
            errors.append(_("Description in English is required."))
        if not category_id:
            errors.append(_("Category is required."))
        if not pricing_type:
            errors.append(_("Pricing type is required."))
        if not base_price:
            errors.append(_("Base price is required."))

        try:
            base_price_val = float(base_price) if base_price else 0
            if base_price_val <= 0:
                errors.append(_("Base price must be greater than zero."))
        except ValueError:
            errors.append(_("Base price must be a valid number."))

        if pricing_type == "distance" and price_per_km:
            try:
                float(price_per_km)
            except ValueError:
                errors.append(_("Price per km must be a valid number."))

        if pricing_type == "hourly" and price_per_hour:
            try:
                float(price_per_hour)
            except ValueError:
                errors.append(_("Price per hour must be a valid number."))

        if errors:
            return JsonResponse({"success": False, "errors": errors})

        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return JsonResponse(
                {"success": False, "errors": [_("Invalid category selected.")]}
            )

        status = Offer.OfferStatus.DRAFT
        if action == "submit":
            status = Offer.OfferStatus.PENDING

        try:
            with transaction.atomic():
                offer = Offer.objects.create(
                    provider=request.user,
                    category=category,
                    title_ar=title_ar,
                    title_fr=title_fr,
                    title_en=title_en,
                    description_ar=description_ar,
                    description_fr=description_fr,
                    description_en=description_en,
                    pricing_type=pricing_type,
                    base_price=base_price_val,
                    price_per_km=float(price_per_km) if price_per_km else None,
                    price_per_hour=float(price_per_hour) if price_per_hour else None,
                    fuel_cost=float(fuel_cost) if fuel_cost else None,
                    operator_cost=float(operator_cost) if operator_cost else None,
                    wait_time_cost=float(wait_time_cost) if wait_time_cost else None,
                    capacity=capacity,
                    location_ar=location_ar,
                    location_fr=location_fr,
                    location_en=location_en,
                    is_available=is_available,
                    status=status,
                )

                if request.FILES.get("image"):
                    offer.image = request.FILES["image"]
                    offer.save()

                message = (
                    _("Offer submitted for approval successfully.")
                    if action == "submit"
                    else _("Offer saved as draft successfully.")
                )

                return JsonResponse(
                    {
                        "success": True,
                        "message": message,
                        "redirect_url": reverse(
                            "dash:provider_offer_details", kwargs={"pk": offer.pk}
                        ),
                    }
                )
        except Exception as e:
            return JsonResponse({"success": False, "errors": [str(e)]})

    context = {
        "categories": get_localized_category_choices(categories),
        "pricing_choices": Offer.PricingType.choices,
    }
    return render(request, "offers/provider/create.html", context)


@provider_required
def provider_offer_details(request, pk):
    offer = get_object_or_404(Offer, pk=pk, provider=request.user)
    context = {"offer": offer}
    return render(request, "offers/provider/details.html", context)


@provider_required
@require_http_methods(["GET", "POST"])
def provider_offer_edit(request, pk):
    offer = get_object_or_404(Offer, pk=pk, provider=request.user)
    categories = Category.objects.filter(is_active=True)

    if request.method == "POST":
        errors = []
        title_ar = request.POST.get("title_ar", "").strip()
        title_fr = request.POST.get("title_fr", "").strip()
        title_en = request.POST.get("title_en", "").strip()
        description_ar = request.POST.get("description_ar", "").strip()
        description_fr = request.POST.get("description_fr", "").strip()
        description_en = request.POST.get("description_en", "").strip()
        category_id = request.POST.get("category", "").strip()
        pricing_type = request.POST.get("pricing_type", "").strip()
        base_price = request.POST.get("base_price", "").strip()
        price_per_km = request.POST.get("price_per_km", "").strip() or None
        price_per_hour = request.POST.get("price_per_hour", "").strip() or None
        fuel_cost = request.POST.get("fuel_cost", "").strip() or None
        operator_cost = request.POST.get("operator_cost", "").strip() or None
        wait_time_cost = request.POST.get("wait_time_cost", "").strip() or None
        capacity = request.POST.get("capacity", "").strip()
        location_ar = request.POST.get("location_ar", "").strip()
        location_fr = request.POST.get("location_fr", "").strip()
        location_en = request.POST.get("location_en", "").strip()
        is_available = request.POST.get("is_available") == "on"
        action = request.POST.get("action", "draft")

        if not title_ar:
            errors.append(_("Title in Arabic is required."))
        if not title_fr:
            errors.append(_("Title in French is required."))
        if not title_en:
            errors.append(_("Title in English is required."))
        if not description_ar:
            errors.append(_("Description in Arabic is required."))
        if not description_fr:
            errors.append(_("Description in French is required."))
        if not description_en:
            errors.append(_("Description in English is required."))
        if not category_id:
            errors.append(_("Category is required."))
        if not pricing_type:
            errors.append(_("Pricing type is required."))
        if not base_price:
            errors.append(_("Base price is required."))

        try:
            base_price_val = float(base_price) if base_price else 0
            if base_price_val <= 0:
                errors.append(_("Base price must be greater than zero."))
        except ValueError:
            errors.append(_("Base price must be a valid number."))

        if pricing_type == "distance" and price_per_km:
            try:
                float(price_per_km)
            except ValueError:
                errors.append(_("Price per km must be a valid number."))

        if pricing_type == "hourly" and price_per_hour:
            try:
                float(price_per_hour)
            except ValueError:
                errors.append(_("Price per hour must be a valid number."))

        if errors:
            return JsonResponse({"success": False, "errors": errors})

        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return JsonResponse(
                {"success": False, "errors": [_("Invalid category selected.")]}
            )

        status = offer.status
        if action == "submit":
            status = Offer.OfferStatus.PENDING
        elif action == "draft" and offer.status in [Offer.OfferStatus.REJECTED]:
            status = Offer.OfferStatus.DRAFT

        try:
            with transaction.atomic():
                offer.category = category
                offer.title_ar = title_ar
                offer.title_fr = title_fr
                offer.title_en = title_en
                offer.description_ar = description_ar
                offer.description_fr = description_fr
                offer.description_en = description_en
                offer.pricing_type = pricing_type
                offer.base_price = base_price_val
                offer.price_per_km = float(price_per_km) if price_per_km else None
                offer.price_per_hour = float(price_per_hour) if price_per_hour else None
                offer.fuel_cost = float(fuel_cost) if fuel_cost else None
                offer.operator_cost = float(operator_cost) if operator_cost else None
                offer.wait_time_cost = float(wait_time_cost) if wait_time_cost else None
                offer.capacity = capacity
                offer.location_ar = location_ar
                offer.location_fr = location_fr
                offer.location_en = location_en
                offer.is_available = is_available
                offer.status = status
                offer.admin_note = ""

                if request.FILES.get("image"):
                    offer.image = request.FILES["image"]

                offer.save()

                message = (
                    _("Offer submitted for approval successfully.")
                    if action == "submit"
                    else _("Offer updated successfully.")
                )

                return JsonResponse(
                    {
                        "success": True,
                        "message": message,
                        "redirect_url": reverse(
                            "dash:provider_offer_details", kwargs={"pk": offer.pk}
                        ),
                    }
                )
        except Exception as e:
            return JsonResponse({"success": False, "errors": [str(e)]})

    context = {
        "offer": offer,
        "categories": get_localized_category_choices(categories),
        "pricing_choices": Offer.PricingType.choices,
    }
    return render(request, "offers/provider/edit.html", context)


@provider_required
@require_POST
def provider_offer_delete(request, pk):
    offer = get_object_or_404(Offer, pk=pk, provider=request.user)

    try:
        title = offer.title_ar
        offer.delete()

        return JsonResponse(
            {
                "success": True,
                "message": _("Offer '%(title)s' deleted successfully.")
                % {"title": title},
                "redirect_url": reverse("dash:provider_offer_list"),
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": _("An error occurred: %(error)s") % {"error": str(e)},
            }
        )
