"""
Adaptery dostarczania powiadomień (F9.1) — interfejsy + implementacje null/test.

Produkcyjnie (Frankfurt DC) rejestruje się realne adaptery (np. Twilio SMS,
SMTP/SendGrid email, FCM/APNs push). Tu definiujemy protokół i bezpieczne
implementacje null (nic nie wysyłają) oraz in-memory (zbierają — do testów).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class DeliveryResult:
    ok: bool
    provider_id: str | None = None
    error: str | None = None


class NotificationAdapter(Protocol):
    channel: str

    def send(self, *, to: str, title: str, body: str, bypass_dnd: bool = False) -> DeliveryResult:
        ...  # pragma: no cover


class NullAdapter:
    """Nic nie wysyła — bezpieczny domyślny (dev/offline)."""
    channel = "null"

    def send(self, *, to: str, title: str, body: str, bypass_dnd: bool = False) -> DeliveryResult:
        return DeliveryResult(ok=True, provider_id="null")


@dataclass
class MemoryAdapter:
    """Zbiera wysyłki w pamięci — do testów i podglądu."""
    channel: str = "memory"
    sent: list[dict] = field(default_factory=list)
    fail: bool = False

    def send(self, *, to: str, title: str, body: str, bypass_dnd: bool = False) -> DeliveryResult:
        if self.fail:
            return DeliveryResult(ok=False, error="symulowany błąd dostawy")
        record = {"to": to, "title": title, "body": body, "bypass_dnd": bypass_dnd}
        self.sent.append(record)
        return DeliveryResult(ok=True, provider_id=f"mem-{len(self.sent)}")


class SmsAdapter(MemoryAdapter):
    channel: str = "sms"


class EmailAdapter(MemoryAdapter):
    channel: str = "email"


class PushAdapter(MemoryAdapter):
    channel: str = "push"
