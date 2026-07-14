"""
F11 — Marketplace usług dla seniorów.

10 kategorii usług, partnerzy weryfikowani po NIP + polisie OC (anty-fraud),
zamówienia z oknem anulowania 30 min. Kategorie wysokiego ryzyka wymagają OC.
"""
from .models import (
    Partner, Service, Order, ServiceCategory, PartnerStatus, OrderStatus,
)
from .service import (
    MarketplaceService, validate_nip,
    CANCELLATION_WINDOW_MINUTES, FRAUD_SUSPEND_THRESHOLD, OC_REQUIRED_CATEGORIES,
)

__all__ = [
    "Partner", "Service", "Order", "ServiceCategory", "PartnerStatus", "OrderStatus",
    "MarketplaceService", "validate_nip",
    "CANCELLATION_WINDOW_MINUTES", "FRAUD_SUSPEND_THRESHOLD", "OC_REQUIRED_CATEGORIES",
]
