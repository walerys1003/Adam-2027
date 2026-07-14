"""Testy F9 — dashboard rodzinny + notyfikacje wg poziomu semafora."""
from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.seniors.models import SemaphoreLevel
from adam_modules.family import (
    FamilyService, FamilyRole, NotifyChannel, DeliveryMode,
    NotificationStatus, SmsAdapter, EmailAdapter,
)


def _senior(session):
    return SeniorService(session).create(
        SeniorCreate(first_name="Jan", last_name="Kowalski", phone="+48123456789")
    )


def _svc(session):
    return FamilyService(session, adapters={"sms": SmsAdapter(), "email": EmailAdapter()})


def test_add_member(session):
    s = _senior(session)
    svc = _svc(session)
    fm = svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700")
    assert fm.id is not None
    assert fm.role == FamilyRole.primary
    assert len(svc.members(s.id)) == 1


def test_green_no_notifications(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700")
    out = svc.dispatch(s, SemaphoreLevel.green, title="OK", body="rutyna")
    assert out == []


def test_yellow_digest(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700")
    out = svc.dispatch(s, SemaphoreLevel.yellow, title="Uwaga", body="gorszy nastrój", hour=12)
    assert len(out) == 1
    assert out[0].mode == DeliveryMode.digest
    assert out[0].status == NotificationStatus.sent


def test_red_immediate_excludes_observer(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700")
    svc.add_member(s, "Sąsiad", FamilyRole.observer, phone="+48111222333")
    out = svc.dispatch(s, SemaphoreLevel.red, title="Pilne", body="brak odpowiedzi", hour=12)
    # obserwator wykluczony z alertów krytycznych
    assert len(out) == 1
    assert out[0].mode == DeliveryMode.immediate


def test_purple_bypass_dnd(session):
    s = _senior(session)
    svc = _svc(session)
    # opiekun w trybie DND (22-7), ale PURPLE ma bypass
    svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700",
                   dnd_start=22, dnd_end=7)
    out = svc.dispatch(s, SemaphoreLevel.purple, title="KRYZYS", body="ból w klatce", hour=3)
    assert len(out) == 1
    assert out[0].mode == DeliveryMode.bypass_dnd
    assert out[0].status == NotificationStatus.sent


def test_dnd_holds_yellow(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Anna", FamilyRole.secondary, phone="+48500600700",
                   dnd_start=22, dnd_end=7)
    out = svc.dispatch(s, SemaphoreLevel.yellow, title="Uwaga", body="x", hour=3)
    assert out[0].status == NotificationStatus.pending  # wstrzymane przez DND


def test_red_critical_role_ignores_dnd(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Koordynator", FamilyRole.coordinator, phone="+48500600700",
                   dnd_start=22, dnd_end=7)
    out = svc.dispatch(s, SemaphoreLevel.red, title="Pilne", body="x", hour=3)
    # rola krytyczna przy RED ignoruje DND
    assert out[0].status == NotificationStatus.sent


def test_dnd_window_across_midnight(session):
    s = _senior(session)
    svc = _svc(session)
    fm = svc.add_member(s, "Anna", FamilyRole.secondary, dnd_start=22, dnd_end=7)
    assert svc.in_dnd(fm, 23) is True
    assert svc.in_dnd(fm, 3) is True
    assert svc.in_dnd(fm, 12) is False


def test_acknowledge_and_feed(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700")
    out = svc.dispatch(s, SemaphoreLevel.red, title="Pilne", body="x", hour=12)
    svc.acknowledge(out[0])
    assert out[0].status == NotificationStatus.acknowledged
    feed = svc.feed(s.id)
    assert len(feed) == 1


# ==================================================================
# ETAP 32 — Realne integracje: fabryka build_adapters (fail-safe)
# Twilio/SendGrid/FCM już istnieją (ETAP 13). Tu weryfikujemy, że
# fabryka degraduje PER KANAŁ do NullAdapter przy braku sekretów,
# i buduje realne adaptery gdy komplet sekretów jest obecny.
# ==================================================================
import pytest
from adam_modules.family import (
    build_adapters, NullAdapter, MemoryAdapter,
    TwilioSmsAdapter, SendGridEmailAdapter, FcmPushAdapter,
)

_LIVE_SECRETS = (
    "ADAM_TWILIO_SID", "ADAM_TWILIO_TOKEN", "ADAM_TWILIO_FROM",
    "ADAM_SENDGRID_KEY", "ADAM_SENDGRID_FROM", "ADAM_FCM_KEY",
)


def _clear_live_secrets(monkeypatch):
    for k in _LIVE_SECRETS:
        monkeypatch.delenv(k, raising=False)


def test_build_adapters_default_is_memory(monkeypatch):
    monkeypatch.delenv("ADAM_NOTIFY_PROVIDER", raising=False)
    adapters = build_adapters()
    assert set(adapters) == {"sms", "email", "push", "call"}
    assert all(isinstance(a, MemoryAdapter) for a in adapters.values())


def test_build_adapters_null_provider(monkeypatch):
    monkeypatch.setenv("ADAM_NOTIFY_PROVIDER", "null")
    adapters = build_adapters()
    assert all(isinstance(a, NullAdapter) for a in adapters.values())


def test_build_adapters_live_without_secrets_degrades_to_null(monkeypatch):
    """Fail-safe: provider=live bez sekretów → NullAdapter na każdym kanale."""
    monkeypatch.setenv("ADAM_NOTIFY_PROVIDER", "live")
    _clear_live_secrets(monkeypatch)
    adapters = build_adapters()
    assert isinstance(adapters["sms"], NullAdapter)
    assert isinstance(adapters["email"], NullAdapter)
    assert isinstance(adapters["push"], NullAdapter)
    assert isinstance(adapters["call"], NullAdapter)


def test_build_adapters_live_partial_secrets_degrades_per_channel(monkeypatch):
    """Tylko SMS ma komplet sekretów → SMS realny, reszta NullAdapter."""
    monkeypatch.setenv("ADAM_NOTIFY_PROVIDER", "live")
    _clear_live_secrets(monkeypatch)
    monkeypatch.setenv("ADAM_TWILIO_SID", "AC_test")
    monkeypatch.setenv("ADAM_TWILIO_TOKEN", "tok_test")
    monkeypatch.setenv("ADAM_TWILIO_FROM", "+48500000000")
    adapters = build_adapters()
    assert isinstance(adapters["sms"], TwilioSmsAdapter)
    assert isinstance(adapters["email"], NullAdapter)  # brak SendGrid
    assert isinstance(adapters["push"], NullAdapter)   # brak FCM


def test_build_adapters_live_full_secrets_builds_real_adapters(monkeypatch):
    monkeypatch.setenv("ADAM_NOTIFY_PROVIDER", "live")
    monkeypatch.setenv("ADAM_TWILIO_SID", "AC_test")
    monkeypatch.setenv("ADAM_TWILIO_TOKEN", "tok_test")
    monkeypatch.setenv("ADAM_TWILIO_FROM", "+48500000000")
    monkeypatch.setenv("ADAM_SENDGRID_KEY", "SG.test")
    monkeypatch.setenv("ADAM_SENDGRID_FROM", "adam@example.org")
    monkeypatch.setenv("ADAM_FCM_KEY", "fcm_test")
    adapters = build_adapters()
    assert isinstance(adapters["sms"], TwilioSmsAdapter)
    assert isinstance(adapters["email"], SendGridEmailAdapter)
    assert isinstance(adapters["push"], FcmPushAdapter)
    # kanał call zawsze poza tym pakietem (warstwa ARI)
    assert isinstance(adapters["call"], NullAdapter)


def test_null_adapter_send_is_safe_noop():
    res = NullAdapter().send(to="+48500000000", title="x", body="y")
    assert res.ok is True
    assert res.provider_id == "null"
