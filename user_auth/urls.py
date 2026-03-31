from django.urls import path
from . import views

app_name = "user_auth"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/upgrade/", views.upgrade_to_provider, name="upgrade_to_provider"),
    path("profile/delete/", views.delete_account, name="delete_account"),
]
