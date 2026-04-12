"""
Admin Payment Views
===================

This module contains views for admins to manage provider payment proofs.

Views:
- payment_dashboard: List all pending payment proofs
- payment_details: Display payment details with approve/reject actions
- approve_payment: Approve payment proof and reactivate offer
- reject_payment: Reject payment proof with reason
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone

from dashboard.models import PaymentProof, CommissionBalance, Offer
from dashboard.utils import (
    send_bilingual_notification,
    reactivate_offer,
    get_or_create_commission_balance,
)
from dashboard.decorator import admin_required


@login_required
@admin_required
def payment_dashboard(request):
    """
    List all pending payment proofs.

    Template: payment/admin/dashboard.html
    """
    status_filter = request.GET.get("status", "pending")

    payments = PaymentProof.objects.all()

    if status_filter:
        payments = payments.filter(status=status_filter)

    payments = payments.order_by("-created_at")

    paginator = Paginator(payments, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "payments": page_obj,
        "page_obj": page_obj,
        "status_filter": status_filter,
        "status_choices": PaymentProof.PaymentStatus.choices,
    }
    return render(request, "payment/admin/dashboard.html", context)


@login_required
@admin_required
def payment_details(request, payment_id):
    """
    Display payment details.

    Shows:
    - User info (username, email, phone)
    - Offer details (title, status, base_price)
    - Payment proof file
    - Amount and date
    - Approve/Reject buttons

    Template: payment/admin/details.html
    """
    payment = get_object_or_404(PaymentProof, pk=payment_id)
    balance = get_or_create_commission_balance(payment.provider)

    context = {
        "payment": payment,
        "balance": balance,
    }
    return render(request, "payment/admin/details.html", context)


@login_required
@admin_required
def approve_payment(request, payment_id):
    """
    Approve payment proof.

    - Mark as approved
    - Reactivate provider's offer
    - Reset commission balance to 0
    - Send bilingual notification to provider

    Returns:
        JSON response with success status
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "errors": [_("Invalid request method.")]}
        )

    payment = get_object_or_404(PaymentProof, pk=payment_id)

    if payment.status != PaymentProof.PaymentStatus.PENDING:
        return JsonResponse(
            {
                "success": False,
                "errors": [_("This payment has already been processed.")],
            }
        )

    with transaction.atomic():
        payment.status = PaymentProof.PaymentStatus.APPROVED
        payment.reviewed_at = timezone.now()
        payment.save()

        offer = payment.offer
        reactivate_offer(offer)

        balance = get_or_create_commission_balance(payment.provider)
        balance.total_commission = 0
        balance.is_blocked = False
        balance.save()

    send_bilingual_notification(
        payment.provider,
        _("Payment Approved"),
        _("Payment Approved"),
        _(
            "Your payment of {amount} DA has been approved. Your offer is now active."
        ).format(amount=payment.amount),
        _(
            "Your payment of {amount} DA has been approved. Your offer is now active."
        ).format(amount=payment.amount),
        link=reverse("dash:payment_history"),
        notification_type="success",
    )

    return JsonResponse(
        {
            "success": True,
            "message": _("Payment approved successfully!"),
        }
    )


@login_required
@admin_required
def reject_payment(request, payment_id):
    """
    Reject payment proof with reason.

    - Mark as rejected
    - Provider can resubmit
    - Send bilingual rejection notification

    Returns:
        JSON response with success status
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "errors": [_("Invalid request method.")]}
        )

    payment = get_object_or_404(PaymentProof, pk=payment_id)

    if payment.status != PaymentProof.PaymentStatus.PENDING:
        return JsonResponse(
            {
                "success": False,
                "errors": [_("This payment has already been processed.")],
            }
        )

    reason = request.POST.get("reason", "").strip()

    with transaction.atomic():
        payment.status = PaymentProof.PaymentStatus.REJECTED
        payment.admin_note = reason
        payment.reviewed_at = timezone.now()
        payment.save()

    send_bilingual_notification(
        payment.provider,
        _("Payment Rejected"),
        _("Payment Rejected"),
        _("Your payment proof was rejected. Reason: {reason}").format(
            reason=reason if reason else _("No reason provided")
        ),
        _("Your payment proof was rejected. Reason: {reason}").format(
            reason=reason if reason else _("No reason provided")
        ),
        link=reverse("dash:payment_required"),
        notification_type="error",
    )

    return JsonResponse(
        {
            "success": True,
            "message": _("Payment rejected."),
        }
    )
