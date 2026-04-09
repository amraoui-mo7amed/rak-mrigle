"""
Catalog Views for Customer Service Browsing
============================================

This module contains views for customers to browse and request services.

Views:
- catalog_list: Browse active offers with filtering
- catalog_details: View offer details
- create_request: Submit service request for an offer

All views require:
- User authentication
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from dashboard.models import Offer, Category, ServiceRequest
from dashboard.utils import (
    notify_user,
    get_wilayas_choices,
    get_localized_category_choices,
)


@login_required
def catalog_list(request):
    """
    Display paginated list of active offers with filtering options.

    Supports filtering by:
        - Search query (title in AR/FR/EN)
        - Wilaya (location)
        - Category
        - Pricing type (distance/hourly)
        - Price range (min/max)

    Args:
        request: HTTP request object

    Returns:
        Rendered template with:
            - offers: Paginated Offer queryset
            - page_obj: Pagination object
            - categories: Available categories
            - wilayas: Available wilayas
            - Various filter values

    Template: catalog/list.html
    """
    offers = Offer.objects.filter(status="active", is_available=True).select_related(
        "provider", "category"
    )

    query = request.GET.get("q", "")
    if query:
        offers = offers.filter(
            Q(title_ar__icontains=query)
            | Q(title_fr__icontains=query)
            | Q(title_en__icontains=query)
        )

    wilaya_filter = request.GET.get("wilaya", "")
    if wilaya_filter:
        offers = offers.filter(wilaya=wilaya_filter)

    category_filter = request.GET.get("category", "")
    if category_filter:
        offers = offers.filter(category_id=category_filter)

    pricing_filter = request.GET.get("pricing_type", "")
    if pricing_filter:
        offers = offers.filter(pricing_type=pricing_filter)

    min_price = request.GET.get("min_price", "")
    if min_price:
        offers = offers.filter(base_price__gte=min_price)

    max_price = request.GET.get("max_price", "")
    if max_price:
        offers = offers.filter(base_price__lte=max_price)

    paginator = Paginator(offers, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True)
    wilayas = get_wilayas_choices()

    context = {
        "offers": page_obj,
        "page_obj": page_obj,
        "categories": get_localized_category_choices(categories),
        "wilayas": wilayas,
        "query": query,
        "selected_wilaya": wilaya_filter,
        "selected_category": category_filter,
        "selected_pricing": pricing_filter,
        "min_price": min_price,
        "max_price": max_price,
    }
    return render(request, "catalog/list.html", context)


@login_required
def catalog_details(request, offer_id):
    """
    Display detailed view of a service offer.

    Shows pricing details, provider information, and related offers.
    Includes CTA button to request the service.

    Args:
        request: HTTP request object
        offer_id: Offer primary key

    Returns:
        Rendered template with:
            - offer: Offer object
            - related_offers: Similar offers (same category)

    Template: catalog/details.html
    """
    offer = get_object_or_404(Offer, pk=offer_id, status="active", is_available=True)

    related_offers = (
        Offer.objects.filter(
            category=offer.category, status="active", is_available=True
        )
        .exclude(pk=offer.pk)
        .select_related("provider")[:4]
    )

    context = {
        "offer": offer,
        "related_offers": related_offers,
    }
    return render(request, "catalog/details.html", context)


@login_required
def create_request(request, offer_id):
    """
    Create a new service request for an offer.

    GET: Display request form with offer details
    POST: Process form submission and create ServiceRequest

    Sends notification to provider on successful creation.

    Args:
        request: HTTP request object
        offer_id: Offer primary key

    Returns:
        GET: Rendered form template
        POST: JSON response with success/error status

    Template: catalog/request_form.html
    """
    offer = get_object_or_404(Offer, pk=offer_id, status="active", is_available=True)

    if request.method == "POST":
        errors = []

        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        wilaya = request.POST.get("wilaya", "").strip()
        location = request.POST.get("location", "").strip()
        destination = request.POST.get("destination", "").strip()
        notes = request.POST.get("notes", "").strip()

        if not full_name:
            errors.append(_("Full name is required."))
        if not phone:
            errors.append(_("Phone number is required."))
        if not wilaya:
            errors.append(_("Wilaya is required."))
        if not location:
            errors.append(_("Pickup location is required."))

        if errors:
            return JsonResponse({"success": False, "errors": errors})

        service_request = ServiceRequest.objects.create(
            customer=request.user,
            offer=offer,
            full_name=full_name,
            phone=phone,
            wilaya=wilaya,
            location=location,
            destination=destination,
            notes=notes,
            status=ServiceRequest.RequestStatus.PENDING,
        )

        notify_user(
            offer.provider,
            _("New Service Request"),
            _("Customer {name} requested your service: {offer}").format(
                name=full_name, offer=offer.title_ar
            ),
            notification_type="info",
            link=reverse(
                "dash:provider_request_details",
                kwargs={"request_id": service_request.pk},
            ),
        )

        return JsonResponse(
            {
                "success": True,
                "message": _("Request submitted successfully!"),
                "redirect_url": reverse("dash:customer_requests"),
            }
        )

    wilayas = get_wilayas_choices()
    context = {
        "offer": offer,
        "wilayas": wilayas,
    }
    return render(request, "catalog/request_form.html", context)
