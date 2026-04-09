from django.utils.translation import gettext_lazy as _


def dashboard_sidebar(request):
    menu_items = [
        {
            "title": _("Dashboard"),
            "icon": "fas fa-th-large",
            "url_name": "dash:dash_home",
            "admin_only": False,
            "provider_only": False,
            "customer_only": False,
        },
        {
            "title": _("Users"),
            "icon": "fas fa-users",
            "url_name": "dash:user_list",
            "admin_only": True,
            "provider_only": False,
            "customer_only": False,
        },
        {
            "title": _("All Offers"),
            "icon": "fas fa-box-open",
            "url_name": "dash:offer_list",
            "admin_only": True,
            "provider_only": False,
            "customer_only": False,
        },
        {
            "title": _("My Offers"),
            "icon": "fas fa-truck",
            "url_name": "dash:provider_offer_list",
            "admin_only": False,
            "provider_only": True,
            "customer_only": False,
        },
        {
            "title": _("Browse Services"),
            "icon": "fas fa-search",
            "url_name": "dash:catalog_list",
            "admin_only": False,
            "provider_only": False,
            "customer_only": True,
        },
        {
            "title": _("My Requests"),
            "icon": "fas fa-clipboard-list",
            "url_name": "dash:customer_requests",
            "admin_only": False,
            "provider_only": False,
            "customer_only": True,
        },
        {
            "title": _("Incoming Requests"),
            "icon": "fas fa-inbox",
            "url_name": "dash:provider_requests",
            "admin_only": False,
            "provider_only": True,
            "customer_only": False,
        },
        {
            "title": _("Social Auth"),
            "icon": "fas fa-plug",
            "url_name": "dash:social_app_list",
            "admin_only": True,
            "provider_only": False,
            "customer_only": False,
        },
    ]

    filtered_menu = []

    for item in menu_items:
        if request.user.is_superuser and item["admin_only"] is True:
            filtered_menu.append(item)
        elif (
            not item["admin_only"]
            and not item["provider_only"]
            and not item["customer_only"]
        ):
            filtered_menu.append(item)
        elif hasattr(request.user, "profile"):
            user_role = getattr(request.user.profile, "role", None)
            if item["provider_only"] and user_role == "provider":
                filtered_menu.append(item)
            elif item["customer_only"] and user_role == "customer":
                filtered_menu.append(item)
    return {
        "dashboard_menu": filtered_menu,
    }
