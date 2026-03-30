from django.urls import path
from dashboard.views import dashboard, users, notifications, social_auth

app_name = "dash"

urlpatterns = [
    path("home/", dashboard.dash_home, name="dash_home"),
    path("users/", users.user_list, name="user_list"),
    path("users/<int:pk>/", users.user_details, name="user_details"),
    path("users/<int:pk>/delete/", users.user_delete, name="user_delete"),
    path("users/<int:pk>/approve/", users.user_approve, name="user_approve"),
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
]
