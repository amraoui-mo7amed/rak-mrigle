"""
Provider Payment Views
======================

This module contains views for providers to manage their commission payments.

Views:
- payment_required: Display payment requirement page with commission balance
- submit_payment_proof: Handle payment proof submission
- payment_history: Display provider's payment history
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.paginator import Paginator
from django.db import transaction
from django.conf import settings

from dashboard.models import (
    Offer,
    PaymentProof,
    CommissionBalance,
)
from dashboard.utils import (
    get_or_create_commission_balance,
    send_bilingual_notification,
    notify_user,
)
from dashboard.decorator import provider_required
import os


@login_required
@provider_required
def payment_required(request):
    """
    Display payment requirement page.

    Shows current commission balance and payment form.
    If provider has no pending balance, shows current commission status.

    Template: payment/provider/payment_required.html
    """
    balance = get_or_create_commission_balance(request.user)
    offer = Offer.objects.filter(provider=request.user).first()

    pending_proof = PaymentProof.objects.filter(
        provider=request.user, status=PaymentProof.PaymentStatus.PENDING
    ).first()

    context = {
        "balance": balance,
        "offer": offer,
        "pending_proof": pending_proof,
        "threshold": 1000,
    }
    return render(request, "payment/provider/payment_required.html", context)


@login_required
@provider_required
def submit_payment_proof(request):
    """
    Handle payment proof submission.

    POST: Accept file upload (PDF/Image only)
    Send bilingual notification to admin.

    Returns:
        JSON response with success/error status
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "errors": [_("Invalid request method.")]}
        )

    proof_file = request.FILES.get("proof_file")
    if not proof_file:
        return JsonResponse(
            {"success": False, "errors": [_("Please upload a payment proof file.")]}
        )

    allowed_extensions = [".pdf", ".png", ".jpg", ".jpeg"]
    file_ext = os.path.splitext(proof_file.name)[1].lower()
    if file_ext not in allowed_extensions:
        return JsonResponse(
            {
                "success": False,
                "errors": [_("Only PDF and image files (PNG, JPG, JPEG) are allowed.")],
            }
        )

    balance = get_or_create_commission_balance(request.user)
    offer = Offer.objects.filter(provider=request.user).first()

    if not offer:
        return JsonResponse({"success": False, "errors": [_("No offer found.")]})

    if balance.total_commission < 1000:
        return JsonResponse(
            {
                "success": False,
                "errors": [
                    _("Your commission balance is below the payment threshold.")
                ],
            }
        )

    with transaction.atomic():
        payment_proof = PaymentProof.objects.create(
            provider=request.user,
            offer=offer,
            amount=balance.total_commission,
            proof_file=proof_file,
            status=PaymentProof.PaymentStatus.PENDING,
        )

    from django.contrib.auth import get_user_model

    User = get_user_model()
    admins = User.objects.filter(is_superuser=True)

    payment_url = reverse(
        "dash:admin_payment_details", kwargs={"payment_id": payment_proof.pk}
    )

    for admin in admins:
        send_bilingual_notification(
            admin,
            _("New Payment Proof Submitted"),
            _("New Payment Proof Submitted"),
            _(
                "Provider {username} has submitted a payment proof of {amount} DA."
            ).format(username=request.user.username, amount=payment_proof.amount),
            _(
                "Provider {username} has submitted a payment proof of {amount} DA."
            ).format(username=request.user.username, amount=payment_proof.amount),
            link=payment_url,
            notification_type="info",
        )

    return JsonResponse(
        {
            "success": True,
            "message": _("Payment proof submitted successfully!"),
            "redirect_url": reverse("dash:payment_history"),
        }
    )


@login_required
@provider_required
def payment_history(request):
    """
    Display provider's payment history.

    Template: payment/provider/history.html
    """
    payments = PaymentProof.objects.filter(provider=request.user).order_by(
        "-created_at"
    )

    paginator = Paginator(payments, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    balance = get_or_create_commission_balance(request.user)
    offer = Offer.objects.filter(provider=request.user).first()

    context = {
        "payments": page_obj,
        "page_obj": page_obj,
        "balance": balance,
        "offer": offer,
    }
    return render(request, "payment/provider/history.html", context)
