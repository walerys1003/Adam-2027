"""
F13 — AI Act compliance.

Rejestr systemu AI wysokiego ryzyka (SYSTEM_REGISTER) + log ujawnień natury AI
(DisclosureLog) jako dowód spełnienia obowiązku transparentności (art. 50).
"""
from .models import DisclosureLog, DisclosureChannel
from .service import ComplianceService, SYSTEM_REGISTER

__all__ = [
    "DisclosureLog", "DisclosureChannel",
    "ComplianceService", "SYSTEM_REGISTER",
]
