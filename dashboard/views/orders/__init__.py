"""
Order Management Views Package
==============================

This package contains views for managing service requests.

Modules:
    - provider_orders: Provider-side request management
    - customer_orders: Customer-side request management
"""

from .provider_orders import (
    provider_request_list,
    provider_request_details,
    approve_request,
    reject_request,
)
from .customer_orders import (
    customer_request_list,
    customer_request_details,
    cancel_request,
)

__all__ = [
    "provider_request_list",
    "provider_request_details",
    "approve_request",
    "reject_request",
    "customer_request_list",
    "customer_request_details",
    "cancel_request",
]
