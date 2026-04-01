from django.conf import settings
from django.utils.translation import gettext_lazy as _, get_language


def site_settings(request):
    """
    Returns global site configuration and branding details.
    """
    return {
        "site_config": {
            "name": _("Rak-Mrigel"),
            "ar_name": "راك مريقل",
            "tagline": _("Transport Marketplace & Heavy Machinery "),
            "logo": "/static/icons/rak_mrigle_square.png",
            "favicon": "/static/icons/rak_mrigle_square.png",
            "contact_email": "contact@rak-mrigle.com",
            "phone": "+213 600 000 000",
            "social": {
                "facebook": "https://facebook.com/rakmrigle",
                "twitter": "https://twitter.com/rakmrigle",
                "instagram": "https://instagram.com/rakmrigle",
            },
            "seo": {
                "description": _(
                    "The leading marketplace for transport and heavy machinery in Algeria."
                ),
                "keywords": _(
                    "transport, machinery, construction, logistics, algeria, trucks, cranes"
                ),
            },
            "branding": {
                "primary_color": "#0B1E3B",  # hsl(215, 68%, 14%)
                "secondary_color": "#0F172A",  # hsl(222, 47%, 11%)
                "accent_color": "#D97706",  # hsl(43, 82%, 46%)
                "success_color": "#198754",
                "danger_color": "#dc3545",
                "dark_color": "#0F172A",
                "light_color": "#F5F5F5",  # hsl(0, 0%, 96%)
            },
        }
    }
