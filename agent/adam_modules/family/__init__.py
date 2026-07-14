"""
F9 — Dashboard rodzinny + notyfikacje.

Opiekunowie (FamilyMember) otrzymują powiadomienia wg poziomu semafora:
digest (żółty) / immediate (czerwony) / bypass-DND (fioletowy). Adaptery
SMS/email/push są pluggable. feed() zasila endpoint SSE /api/events.
"""
from .models import (
    FamilyMember, Notification, FamilyRole, NotifyChannel,
    DeliveryMode, NotificationStatus,
)
from .adapters import (
    NotificationAdapter, DeliveryResult, NullAdapter, MemoryAdapter,
    SmsAdapter, EmailAdapter, PushAdapter,
    TwilioSmsAdapter, SendGridEmailAdapter, FcmPushAdapter, build_adapters,
)
from .service import FamilyService

__all__ = [
    "FamilyMember", "Notification", "FamilyRole", "NotifyChannel",
    "DeliveryMode", "NotificationStatus",
    "NotificationAdapter", "DeliveryResult", "NullAdapter", "MemoryAdapter",
    "SmsAdapter", "EmailAdapter", "PushAdapter",
    "TwilioSmsAdapter", "SendGridEmailAdapter", "FcmPushAdapter", "build_adapters",
    "FamilyService",
]
