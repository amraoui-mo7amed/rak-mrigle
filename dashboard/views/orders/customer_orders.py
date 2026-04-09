"""
Customer Order Management Views
================================

This module contains views for customers to manage their service requests.

Views:
- customer_request_list: List all customer's service requests
- customer_request_details: View detailed request information
- cancel_request: Cancel a pending request

All views require:
- User authentication
- User role: customer
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.decorators.http import require_POST
from dashboard.models import ServiceRequest
from dashboard.utils import notify_user, get_status_choices


@login_required
def customer_request_list(request):
    """
    Display paginated list of customer's service requests.

    Args:
        request: HTTP request object

    Returns:
        Rendered template with:
            - requests: Paginated ServiceRequest queryset
            - page_obj: Pagination object
            - status_filter: Current status filter
            - status_choices: Available status choices

    Template: orders/customer/list.html
    """
    requests = ServiceRequest.objects.filter(customer=request.user).select_related(
        "offer", "offer__provider"
    )

    status_filter = request.GET.get("status", "")
    if status_filter:
        requests = requests.filter(status=status_filter)

    paginator = Paginator(requests, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "requests": page_obj,
        "page_obj": page_obj,
        "status_filter": status_filter,
        "status_choices": get_status_choices(),
    }
    return render(request, "orders/customer/list.html", context)


@login_required
def customer_request_details(request, request_id):
    """
    Display detailed view of customer's service request.

    Shows request details, status, and provider information.
    Provider phone number is only visible if request is approved.

    Args:
        request: HTTP request object
        request_id: ServiceRequest primary key

    Returns:
        Rendered template with request and offer details

    Template: orders/customer/details.html
    """
    service_request = get_object_or_404(
        ServiceRequest, pk=request_id, customer=request.user
    )

    context = {
        "service_request": service_request,
        "offer": service_request.offer,
    }
    return render(request, "orders/customer/details.html", context)


@login_required
@require_POST
def cancel_request(request, request_id):
    """
    Cancel a pending service request.

    Only pending requests can be cancelled.
    Sends notification to provider about cancellation.

    Args:
        request: HTTP request object (POST only)
        request_id: ServiceRequest primary key

    Returns:
        JSON response with:
            - success: True/False
            - message: Success/error message
            - redirect_url: URL to redirect after cancellation
    """
    service_request = get_object_or_404(
        ServiceRequest, pk=request_id, customer=request.user
    )

    if service_request.status != ServiceRequest.RequestStatus.PENDING:
        return JsonResponse(
            {
                "success": False,
                "errors": [_("Only pending requests can be cancelled.")],
            }
        )

    service_request.status = ServiceRequest.RequestStatus.CANCELLED
    service_request.save()

    notify_user(
        service_request.offer.provider,
        _("Request Cancelled"),
        _("Customer cancelled their request for {offer}").format(
            offer=service_request.offer.title_ar
        ),
        notification_type="warning",
        link=reverse(
            "dash:provider_request_details",
            kwargs={"request_id": service_request.pk},
        ),
    )

    return JsonResponse(
        {
            "success": True,
            "message": _("Request cancelled successfully!"),
            "redirect_url": reverse("dash:customer_requests"),
        }
    )
