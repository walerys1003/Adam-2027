"""
Adaptery dostarczania powiadomień (F9.1) — interfejsy + implementacje null/test.

Produkcyjnie (Frankfurt DC) rejestruje się realne adaptery (np. Twilio SMS,
SMTP/SendGrid email, FCM/APNs push). Tu definiujemy protokół i bezpieczne
implementacje null (nic nie wysyłają) oraz in-memory (zbierają — do testów).
"""
from __future__ import annotations

import base64
import os
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


# ==================================================================
# Realne adaptery HTTP (ETAP 13) — httpx (już w requirements).
# Sekrety wyłącznie z ENV; brak sekretu => degradacja do NullAdapter.
# Uwaga: sieć realnie działa dopiero we Frankfurt DC — w sandboxie
# adaptery są konstruowane, ale nie wykonują połączeń w testach.
# ==================================================================

_HTTP_TIMEOUT = float(os.getenv("ADAM_NOTIFY_TIMEOUT", "8.0"))


def _post(url: str, *, data=None, json=None, headers=None) -> DeliveryResult:
    """Wykonuje POST przez httpx; mapuje wynik na DeliveryResult."""
    try:
        import httpx  # lokalny import — nie obciąża środowisk bez sieci
    except Exception as exc:  # pragma: no cover
        return DeliveryResult(ok=False, error=f"httpx niedostępny: {exc}")
    try:
        with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
            resp = client.post(url, data=data, json=json, headers=headers)
        if 200 <= resp.status_code < 300:
            pid = None
            try:
                body = resp.json()
                pid = body.get("sid") or body.get("id") or body.get("name")
            except Exception:
                pid = None
            return DeliveryResult(ok=True, provider_id=pid)
        return DeliveryResult(ok=False, error=f"HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as exc:
        return DeliveryResult(ok=False, error=f"{type(exc).__name__}: {exc}")


@dataclass
class TwilioSmsAdapter:
    """SMS przez Twilio Messages API. Wymaga ADAM_TWILIO_SID/TOKEN/FROM."""
    channel: str = "sms"
    account_sid: str = ""
    auth_token: str = ""
    from_number: str = ""

    def send(self, *, to: str, title: str, body: str, bypass_dnd: bool = False) -> DeliveryResult:
        if not (self.account_sid and self.auth_token and self.from_number):
            return DeliveryResult(ok=False, error="Twilio niekonfigurowany (SID/TOKEN/FROM).")
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        auth = base64.b64encode(f"{self.account_sid}:{self.auth_token}".encode()).decode()
        text = f"{title}\n{body}" if title else body
        return _post(
            url,
            data={"To": to, "From": self.from_number, "Body": text},
            headers={"Authorization": f"Basic {auth}"},
        )


@dataclass
class SendGridEmailAdapter:
    """E-mail przez SendGrid v3 Mail Send. Wymaga ADAM_SENDGRID_KEY/FROM."""
    channel: str = "email"
    api_key: str = ""
    from_email: str = ""

    def send(self, *, to: str, title: str, body: str, bypass_dnd: bool = False) -> DeliveryResult:
        if not (self.api_key and self.from_email):
            return DeliveryResult(ok=False, error="SendGrid niekonfigurowany (KEY/FROM).")
        return _post(
            "https://api.sendgrid.com/v3/mail/send",
            json={
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": self.from_email},
                "subject": title or "Powiadomienie Adam",
                "content": [{"type": "text/plain", "value": body}],
            },
            headers={"Authorization": f"Bearer {self.api_key}",
                     "Content-Type": "application/json"},
        )


@dataclass
class FcmPushAdapter:
    """Push przez FCM legacy HTTP API. Wymaga ADAM_FCM_KEY (server key)."""
    channel: str = "push"
    server_key: str = ""

    def send(self, *, to: str, title: str, body: str, bypass_dnd: bool = False) -> DeliveryResult:
        if not self.server_key:
            return DeliveryResult(ok=False, error="FCM niekonfigurowany (server key).")
        return _post(
            "https://fcm.googleapis.com/fcm/send",
            json={
                "to": to,
                "priority": "high" if bypass_dnd else "normal",
                "notification": {"title": title, "body": body},
            },
            headers={"Authorization": f"key={self.server_key}",
                     "Content-Type": "application/json"},
        )


# ------------------------------------------------------------------ fabryka

def _provider() -> str:
    return os.getenv("ADAM_NOTIFY_PROVIDER", "memory").strip().lower()


def build_adapters() -> dict[str, "NotificationAdapter"]:
    """Buduje mapę kanał→adapter na podstawie ENV.

    ADAM_NOTIFY_PROVIDER:
    - `memory` (domyślnie) → MemoryAdapter na wszystkich kanałach (dev/test),
    - `null`              → NullAdapter (nic nie wysyła),
    - `live`              → realne adaptery (Twilio/SendGrid/FCM); kanał bez
                            sekretu degraduje się do NullAdapter (fail-safe).
    Kanał `call` zawsze Memory/Null (telefonia = warstwa ARI, poza tym pakietem).
    """
    provider = _provider()
    if provider == "null":
        return {c: NullAdapter() for c in ("sms", "email", "push", "call")}
    if provider == "live":
        sms = TwilioSmsAdapter(
            account_sid=os.getenv("ADAM_TWILIO_SID", ""),
            auth_token=os.getenv("ADAM_TWILIO_TOKEN", ""),
            from_number=os.getenv("ADAM_TWILIO_FROM", ""),
        )
        email = SendGridEmailAdapter(
            api_key=os.getenv("ADAM_SENDGRID_KEY", ""),
            from_email=os.getenv("ADAM_SENDGRID_FROM", ""),
        )
        push = FcmPushAdapter(server_key=os.getenv("ADAM_FCM_KEY", ""))
        return {"sms": sms, "email": email, "push": push, "call": NullAdapter()}
    # domyślnie: memory (spójne z dotychczasowymi testami)
    return {c: MemoryAdapter(channel=c) for c in ("sms", "email", "push", "call")}
