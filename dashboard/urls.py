from django.urls import path
from dashboard.views import dashboard, users, notifications, social_auth
from dashboard.views import admin_offers, provider_offers, orders, catalog
from dashboard.views.payment import admin_payment, provider_payment

app_name = "dash"

urlpatterns = [
    path("home/", dashboard.dash_home, name="dash_home"),
    path("users/", users.user_list, name="user_list"),
    path("users/<int:pk>/", users.user_details, name="user_details"),
    path("users/<int:pk>/delete/", users.user_delete, name="user_delete"),
    path("users/<int:pk>/approve/", users.user_approve, name="user_approve"),
    path("users/profile/", users.user_profile, name="user_profile"),
    # Notifications
    path(
        "notifications/stream/",
        notifications.notifications_stream,
        name="notifications_stream",
    ),
    path(
        "notifications/unread-count/",
        notifications.get_unread_count,
        name="notifications_unread_count",
    ),
    path(
        "notifications/list/",
        notifications.get_notifications,
        name="notifications_list",
    ),
    path(
        "notifications/<int:notification_id>/read/",
        notifications.mark_as_read,
        name="notification_mark_read",
    ),
    path(
        "notifications/mark-all-read/",
        notifications.mark_all_as_read,
        name="notifications_mark_all_read",
    ),
    path(
        "notifications/<int:notification_id>/delete/",
        notifications.delete_notification,
        name="notification_delete",
    ),
    # Social Auth Settings
    path("social-auth/", social_auth.social_app_list, name="social_app_list"),
    path(
        "social-auth/create/", social_auth.social_app_create, name="social_app_create"
    ),
    path(
        "social-auth/<int:pk>/update/",
        social_auth.social_app_update,
        name="social_app_update",
    ),
    path(
        "social-auth/<int:pk>/delete/",
        social_auth.social_app_delete,
        name="social_app_delete",
    ),
    # Offers - Admin
    path("offers/", admin_offers.offer_list, name="offer_list"),
    path("offers/<int:pk>/", admin_offers.offer_details, name="offer_details"),
    path("offers/<int:pk>/approve/", admin_offers.offer_approve, name="offer_approve"),
    path("offers/<int:pk>/reject/", admin_offers.offer_reject, name="offer_reject"),
    path("offers/<int:pk>/delete/", admin_offers.offer_delete, name="offer_delete"),
    # Offers - Provider
    path("my-offers/", provider_offers.provider_offer_list, name="provider_offer_list"),
    path(
        "my-offers/create/",
        provider_offers.provider_offer_create,
        name="provider_offer_create",
    ),
    path(
        "my-offers/<int:pk>/",
        provider_offers.provider_offer_details,
        name="provider_offer_details",
    ),
    path(
        "my-offers/<int:pk>/edit/",
        provider_offers.provider_offer_edit,
        name="provider_offer_edit",
    ),
    path(
        "my-offers/<int:pk>/delete/",
        provider_offers.provider_offer_delete,
        name="provider_offer_delete",
    ),
    # Catalog - Customer
    path("catalog/", catalog.catalog_list, name="catalog_list"),
    path("catalog/<int:offer_id>/", catalog.catalog_details, name="catalog_details"),
    path(
        "catalog/<int:offer_id>/request/", catalog.create_request, name="create_request"
    ),
    # Service Requests - Customer
    path("my-requests/", orders.customer_request_list, name="customer_requests"),
    path(
        "my-requests/<int:request_id>/",
        orders.customer_request_details,
        name="customer_request_details",
    ),
    path(
        "my-requests/<int:request_id>/cancel/",
        orders.cancel_request,
        name="cancel_request",
    ),
    # Service Requests - Provider
    path("incoming-requests/", orders.provider_request_list, name="provider_requests"),
    path(
        "incoming-requests/<int:request_id>/",
        orders.provider_request_details,
        name="provider_request_details",
    ),
    path(
        "incoming-requests/<int:request_id>/approve/",
        orders.approve_request,
        name="approve_request",
    ),
    path(
        "incoming-requests/<int:request_id>/reject/",
        orders.reject_request,
        name="reject_request",
    ),
    # Payment - Provider
    path("payment/", provider_payment.payment_required, name="payment_required"),
    path(
        "payment/submit/",
        provider_payment.submit_payment_proof,
        name="submit_payment_proof",
    ),
    path("payment/history/", provider_payment.payment_history, name="payment_history"),
    # Payment - Admin
    path(
        "admin/payments/",
        admin_payment.payment_dashboard,
        name="admin_payment_dashboard",
    ),
    path(
        "admin/payments/<int:payment_id>/",
        admin_payment.payment_details,
        name="admin_payment_details",
    ),
    path(
        "admin/payments/<int:payment_id>/approve/",
        admin_payment.approve_payment,
        name="admin_payment_approve",
    ),
    path(
        "admin/payments/<int:payment_id>/reject/",
        admin_payment.reject_payment,
        name="admin_payment_reject",
    ),
]
