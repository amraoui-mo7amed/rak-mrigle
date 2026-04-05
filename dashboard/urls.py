from django.urls import path
from dashboard.views import dashboard, users, notifications, social_auth
from dashboard.views import admin_offers, provider_offers

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
]
