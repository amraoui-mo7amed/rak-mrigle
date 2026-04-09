"""
Provider Order Management Views
================================

This module contains views for providers to manage incoming service requests.

Views:
- provider_request_list: List all incoming requests for provider's offers
- provider_request_details: View detailed request information
- approve_request: Approve a pending request
- reject_request: Reject a pending request

All views require:
- User authentication
- User role: provider
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
def provider_request_list(request):
    """
    Display paginated list of incoming service requests for the provider.

    Args:
        request: HTTP request object

    Returns:
        Rendered template with:
            - requests: Paginated ServiceRequest queryset
            - page_obj: Pagination object
            - status_filter: Current status filter
            - status_choices: Available status choices

    Template: orders/provider/list.html
    """
    requests = ServiceRequest.objects.filter(
        offer__provider=request.user
    ).select_related("offer", "customer")

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
    return render(request, "orders/provider/list.html", context)


@login_required
def provider_request_details(request, request_id):
    """
    Display detailed view of a service request.

    Shows customer information and request details.
    Phone number is only visible if request status is 'approved'.

    Args:
        request: HTTP request object
        request_id: ServiceRequest primary key

    Returns:
        Rendered template with request and offer details

    Template: orders/provider/details.html
    """
    service_request = get_object_or_404(
        ServiceRequest, pk=request_id, offer__provider=request.user
    )

    context = {
        "service_request": service_request,
        "offer": service_request.offer,
    }
    return render(request, "orders/provider/details.html", context)


@login_required
@require_POST
def approve_request(request, request_id):
    """
    Approve a pending service request.

    Updates request status to 'approved' and sends notification to customer.
    Phone number becomes visible to provider after approval.

    Args:
        request: HTTP request object (POST only)
        request_id: ServiceRequest primary key

    Returns:
        JSON response with:
            - success: True/False
            - message: Success/error message
            - redirect_url: URL to redirect after approval
    """
    service_request = get_object_or_404(
        ServiceRequest, pk=request_id, offer__provider=request.user
    )

    if service_request.status != ServiceRequest.RequestStatus.PENDING:
        return JsonResponse(
            {
                "success": False,
                "errors": [_("This request is no longer pending.")],
            }
        )

    service_request.status = ServiceRequest.RequestStatus.APPROVED
    service_request.save()

    notify_user(
        service_request.customer,
        _("Request Approved"),
        _("Your request for {offer} has been approved!").format(
            offer=service_request.offer.title_ar
        ),
        notification_type="success",
        link=reverse(
            "dash:customer_request_details",
            kwargs={"request_id": service_request.pk},
        ),
    )

    return JsonResponse(
        {
            "success": True,
            "message": _("Request approved successfully!"),
            "redirect_url": reverse(
                "dash:provider_request_details", kwargs={"request_id": request_id}
            ),
        }
    )


@login_required
@require_POST
def reject_request(request, request_id):
    """
    Reject a pending service request.

    Updates request status to 'rejected' and sends notification to customer.

    Args:
        request: HTTP request object (POST only)
        request_id: ServiceRequest primary key

    Returns:
        JSON response with:
            - success: True/False
            - message: Success/error message
            - redirect_url: URL to redirect after rejection
    """
    service_request = get_object_or_404(
        ServiceRequest, pk=request_id, offer__provider=request.user
    )

    if service_request.status != ServiceRequest.RequestStatus.PENDING:
        return JsonResponse(
            {
                "success": False,
                "errors": [_("This request is no longer pending.")],
            }
        )

    service_request.status = ServiceRequest.RequestStatus.REJECTED
    service_request.save()

    notify_user(
        service_request.customer,
        _("Request Rejected"),
        _("Your request for {offer} was rejected.").format(
            offer=service_request.offer.title_ar
        ),
        notification_type="warning",
        link=reverse(
            "dash:customer_request_details",
            kwargs={"request_id": service_request.pk},
        ),
    )

    return JsonResponse(
        {
            "success": True,
            "message": _("Request rejected."),
            "redirect_url": reverse(
                "dash:provider_request_details", kwargs={"request_id": request_id}
            ),
        }
    )
