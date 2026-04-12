from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext as _, get_language
from django.core.paginator import Paginator
from django.db import transaction
from django.views.decorators.http import require_POST, require_http_methods
from decimal import Decimal, InvalidOperation

from dashboard.models import Offer, Category
from dashboard.decorator import provider_required
from dashboard.utils import get_wilayas_choices, get_localized_category_choices


def _to_decimal(value):
    """Convert a value to Decimal, return None if empty or invalid."""
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def get_localized_pricing_choices():
    """Returns pricing type choices localized based on current language."""
    lang = get_language()
    if lang == "ar":
        return [("distance", "مسافة"), ("hourly", "ساعي")]
    elif lang == "fr":
        return [("distance", "Distance"), ("hourly", "Horaire")]
    else:  # en
        return [("distance", "Distance"), ("hourly", "Hourly")]


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
    existing_offer = Offer.objects.filter(provider=request.user).first()
    if existing_offer:
        return redirect("dash:provider_offer_edit", pk=existing_offer.pk)

    categories = Category.objects.filter(is_active=True)

    if request.method == "POST":
        errors = []
        title_ar = request.POST.get("title_ar", "").strip()
        description_ar = request.POST.get("description_ar", "").strip()
        category_id = request.POST.get("category", "").strip()
        pricing_type = request.POST.get("pricing_type", "").strip()
        base_price = request.POST.get("base_price", "").strip()
        price_per_km = request.POST.get("price_per_km", "").strip() or None
        price_per_hour = request.POST.get("price_per_hour", "").strip() or None
        fuel_cost = request.POST.get("fuel_cost", "").strip() or None
        operator_cost = request.POST.get("operator_cost", "").strip() or None
        wait_time_cost = request.POST.get("wait_time_cost", "").strip() or None
        capacity = request.POST.get("capacity", "").strip()
        wilaya = request.POST.get("wilaya", "").strip()
        location_ar = request.POST.get("location_ar", "").strip()
        is_available = request.POST.get("is_available") == "on"

        if not title_ar:
            errors.append(_("Title is required."))
        if not description_ar:
            errors.append(_("Description is required."))
        if not category_id:
            errors.append(_("Category is required."))
        if not pricing_type:
            errors.append(_("Pricing type is required."))
        if not base_price:
            errors.append(_("Base price is required."))

        base_price_val = _to_decimal(base_price)
        if base_price_val is None:
            errors.append(_("Base price must be a valid number."))
        elif base_price_val <= Decimal("0"):
            errors.append(_("Base price must be greater than zero."))

        price_per_km_val = _to_decimal(price_per_km)
        if price_per_km and price_per_km_val is None:
            errors.append(_("Price per km must be a valid number."))

        price_per_hour_val = _to_decimal(price_per_hour)
        if price_per_hour and price_per_hour_val is None:
            errors.append(_("Price per hour must be a valid number."))

        fuel_cost_val = _to_decimal(fuel_cost)
        if fuel_cost and fuel_cost_val is None:
            errors.append(_("Fuel cost must be a valid number."))

        operator_cost_val = _to_decimal(operator_cost)
        if operator_cost and operator_cost_val is None:
            errors.append(_("Operator cost must be a valid number."))

        wait_time_cost_val = _to_decimal(wait_time_cost)
        if wait_time_cost and wait_time_cost_val is None:
            errors.append(_("Wait time cost must be a valid number."))

        if errors:
            return JsonResponse({"success": False, "errors": errors})

        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return JsonResponse(
                {"success": False, "errors": [_("Invalid category selected.")]}
            )

        status = Offer.OfferStatus.ACTIVE

        try:
            with transaction.atomic():
                offer = Offer.objects.create(
                    provider=request.user,
                    category=category,
                    title_ar=title_ar,
                    title_fr=title_ar,
                    title_en=title_ar,
                    description_ar=description_ar,
                    description_fr=description_ar,
                    description_en=description_ar,
                    pricing_type=pricing_type,
                    base_price=base_price_val,
                    price_per_km=price_per_km_val,
                    price_per_hour=price_per_hour_val,
                    fuel_cost=fuel_cost_val,
                    operator_cost=operator_cost_val,
                    wait_time_cost=wait_time_cost_val,
                    capacity=capacity,
                    wilaya=wilaya,
                    location_ar=location_ar,
                    location_fr=location_ar,
                    location_en=location_ar,
                    is_available=is_available,
                    status=status,
                )

                if request.FILES.get("image"):
                    offer.image = request.FILES["image"]
                    offer.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": _("Offer created successfully."),
                    "redirect_url": reverse(
                        "dash:provider_offer_details", kwargs={"pk": offer.pk}
                    ),
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "errors": [str(e)]})

    context = {
        "categories": get_localized_category_choices(categories),
        "pricing_choices": get_localized_pricing_choices(),
        "wilayas": get_wilayas_choices(),
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
        description_ar = request.POST.get("description_ar", "").strip()
        category_id = request.POST.get("category", "").strip()
        pricing_type = request.POST.get("pricing_type", "").strip()
        base_price = request.POST.get("base_price", "").strip()
        price_per_km = request.POST.get("price_per_km", "").strip() or None
        price_per_hour = request.POST.get("price_per_hour", "").strip() or None
        fuel_cost = request.POST.get("fuel_cost", "").strip() or None
        operator_cost = request.POST.get("operator_cost", "").strip() or None
        wait_time_cost = request.POST.get("wait_time_cost", "").strip() or None
        capacity = request.POST.get("capacity", "").strip()
        wilaya = request.POST.get("wilaya", "").strip()
        location_ar = request.POST.get("location_ar", "").strip()
        is_available = request.POST.get("is_available") == "on"

    if not title_ar:
        errors.append(_("Title is required."))
    if not description_ar:
        errors.append(_("Description is required."))
    if not category_id:
        errors.append(_("Category is required."))
    if not pricing_type:
        errors.append(_("Pricing type is required."))
    if not base_price:
        errors.append(_("Base price is required."))

    base_price_val = _to_decimal(base_price)
    if base_price_val is None:
        errors.append(_("Base price must be a valid number."))
    elif base_price_val <= Decimal("0"):
        errors.append(_("Base price must be greater than zero."))

    price_per_km_val = _to_decimal(price_per_km)
    if price_per_km and price_per_km_val is None:
        errors.append(_("Price per km must be a valid number."))

    price_per_hour_val = _to_decimal(price_per_hour)
    if price_per_hour and price_per_hour_val is None:
        errors.append(_("Price per hour must be a valid number."))

    fuel_cost_val = _to_decimal(fuel_cost)
    if fuel_cost and fuel_cost_val is None:
        errors.append(_("Fuel cost must be a valid number."))

    operator_cost_val = _to_decimal(operator_cost)
    if operator_cost and operator_cost_val is None:
        errors.append(_("Operator cost must be a valid number."))

    wait_time_cost_val = _to_decimal(wait_time_cost)
    if wait_time_cost and wait_time_cost_val is None:
        errors.append(_("Wait time cost must be a valid number."))

    if errors:
        return JsonResponse({"success": False, "errors": errors})

    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return JsonResponse(
            {"success": False, "errors": [_("Invalid category selected.")]}
        )

    try:
        with transaction.atomic():
            offer.category = category
            offer.title_ar = title_ar
            offer.title_fr = title_ar
            offer.title_en = title_ar
            offer.description_ar = description_ar
            offer.description_fr = description_ar
            offer.description_en = description_ar
            offer.pricing_type = pricing_type
            offer.base_price = base_price_val
            offer.price_per_km = price_per_km_val
            offer.price_per_hour = price_per_hour_val
            offer.fuel_cost = fuel_cost_val
            offer.operator_cost = operator_cost_val
            offer.wait_time_cost = wait_time_cost_val
            offer.capacity = capacity
            offer.wilaya = wilaya
            offer.location_ar = location_ar
            offer.location_fr = location_ar
            offer.location_en = location_ar
            offer.is_available = is_available
            offer.status = Offer.OfferStatus.ACTIVE

            if request.FILES.get("image"):
                offer.image = request.FILES["image"]

            offer.save()

        return JsonResponse(
            {
                "success": True,
                "message": _("Offer updated successfully."),
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
        "pricing_choices": get_localized_pricing_choices(),
        "wilayas": get_wilayas_choices(),
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
