"""Testy adapterów powiadomień (ETAP 13) — fabryka + realne adaptery.

Nie wykonuje realnych połączeń sieciowych: sprawdza selekcję z ENV,
fail-safe (brak sekretu → błąd/degradacja) oraz zbudowanie mapy kanałów.
"""
from __future__ import annotations

import pytest

from adam_modules.family.adapters import (
    build_adapters, MemoryAdapter, NullAdapter,
    TwilioSmsAdapter, SendGridEmailAdapter, FcmPushAdapter,
)


def test_build_default_memory(monkeypatch):
    monkeypatch.delenv("ADAM_NOTIFY_PROVIDER", raising=False)
    adapters = build_adapters()
    assert set(adapters) == {"sms", "email", "push", "call"}
    assert all(isinstance(a, MemoryAdapter) for a in adapters.values())
    assert adapters["sms"].channel == "sms"


def test_build_null(monkeypatch):
    monkeypatch.setenv("ADAM_NOTIFY_PROVIDER", "null")
    adapters = build_adapters()
    assert all(isinstance(a, NullAdapter) for a in adapters.values())


def test_build_live_types(monkeypatch):
    monkeypatch.setenv("ADAM_NOTIFY_PROVIDER", "live")
    adapters = build_adapters()
    assert isinstance(adapters["sms"], TwilioSmsAdapter)
    assert isinstance(adapters["email"], SendGridEmailAdapter)
    assert isinstance(adapters["push"], FcmPushAdapter)
    assert isinstance(adapters["call"], NullAdapter)


def test_live_adapters_failsafe_without_secrets():
    # bez sekretów realne adaptery zwracają DeliveryResult(ok=False), nie rzucają
    sms = TwilioSmsAdapter()
    email = SendGridEmailAdapter()
    push = FcmPushAdapter()
    for a in (sms, email, push):
        res = a.send(to="x", title="t", body="b")
        assert res.ok is False
        assert res.error


def test_memory_adapter_collects():
    a = MemoryAdapter(channel="sms")
    res = a.send(to="+48500", title="Alarm", body="tresc", bypass_dnd=True)
    assert res.ok
    assert a.sent[0]["to"] == "+48500"
    assert a.sent[0]["bypass_dnd"] is True


def test_null_adapter_ok_but_silent():
    a = NullAdapter()
    res = a.send(to="x", title="t", body="b")
    assert res.ok and res.provider_id == "null"


def test_dispatch_uses_provider_env(monkeypatch):
    # dispatch przez API korzysta z build_adapters — provider=null => brak wysyłek realnych
    monkeypatch.setenv("ADAM_NOTIFY_PROVIDER", "null")
    from fastapi.testclient import TestClient
    from adam_modules.common import db as db_mod
    from adam_modules.api import create_app

    db_mod.init_engine("sqlite:///:memory:")
    with TestClient(create_app(init_db=True)) as c:
        s = c.post("/api/seniors", json={
            "first_name": "A", "last_name": "B", "birth_date": "1940-01-01",
            "address": "ul. X 1", "district": "Wilda"}).json()
        sid = s["id"]
        c.post(f"/api/seniors/{sid}/family/members", json={
            "name": "Córka", "relationship": "child", "phone": "+48500",
            "preferred_channel": "sms"})
        r = c.post(f"/api/seniors/{sid}/family/dispatch", json={
            "level": "red", "title": "Alarm", "body": "tresc"})
        assert r.status_code == 200, r.text
