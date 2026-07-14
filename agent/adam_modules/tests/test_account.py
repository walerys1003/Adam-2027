"""Testy routera konta/wiadomości `/api/account` (ETAP 22).

Weryfikuje domknięcie integracji panelu (Wiadomości + Konto):
- threads: puste bez powiadomień, pojawiają się po dispatch/wiadomości,
- add_message: trwały zapis (wątek zawiera dopisaną wiadomość) + 404,
- invoices: pochodne z pakietów (kwota rośnie z liczbą seniorów),
- sessions: bieżąca sesja z JWT (401 bez tokenu).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from adam_modules.api import create_app
from adam_modules.common import db as db_mod


@pytest.fixture()
def client():
    db_mod.init_engine("sqlite:///:memory:")
    app = create_app(init_db=True)
    with TestClient(app) as c:
        yield c


def _make_senior(client, first="Jan", last="Kowalski"):
    r = client.post("/api/seniors", json={
        "first_name": first, "last_name": last,
        "birth_date": "1945-03-01", "address": "ul. Sołacka 5, Poznań",
        "district": "Jeżyce",
    })
    assert r.status_code == 201, r.text
    return r.json()


def _token(client, email="admin@silvertech.pl", password="admin123"):
    return client.post("/api/auth/login", json={"email": email, "password": password}).json()["access_token"]


# ---------------------------------------------------------------- threads

def test_threads_empty_without_notifications(client):
    _make_senior(client)
    r = client.get("/api/account/threads")
    assert r.status_code == 200, r.text
    assert r.json() == []


def test_add_message_creates_thread_and_persists(client):
    s = _make_senior(client, first="Halina")
    ext = s["external_id"]

    # dopisz wiadomość → tworzy wątek (Notification)
    r = client.post(f"/api/account/threads/{ext}/messages",
                    json={"body": "Dzień dobry, dzwoniłam do pani Haliny."})
    assert r.status_code == 200, r.text
    thread = r.json()
    assert thread["id"] == ext
    assert thread["senior_name"].startswith("Halina")
    assert any("Dzień dobry" in m["body"] for m in thread["messages"])

    # wątek widoczny na liście
    threads = client.get("/api/account/threads").json()
    assert len(threads) == 1
    assert threads[0]["id"] == ext
    # 'from' koordynatora
    assert threads[0]["messages"][-1]["from"] == "coordinator"


def test_add_message_404_when_senior_missing(client):
    r = client.post("/api/account/threads/SR-NOPE/messages", json={"body": "hej"})
    assert r.status_code == 404


def test_add_message_validation_empty_body(client):
    s = _make_senior(client)
    r = client.post(f"/api/account/threads/{s['external_id']}/messages", json={"body": ""})
    assert r.status_code == 422


# ---------------------------------------------------------------- invoices

def test_invoices_derived_from_packages(client):
    # bez seniorów → 0 zł, ale 4 okresy
    r0 = client.get("/api/account/invoices")
    assert r0.status_code == 200
    inv0 = r0.json()
    assert len(inv0) == 4
    assert inv0[0]["status"] == "pending"
    assert all(i["status"] == "paid" for i in inv0[1:])

    # dodaj seniora (pakiet basic domyślnie) → kwota rośnie
    _make_senior(client)
    inv1 = client.get("/api/account/invoices").json()
    amount0 = int(inv0[0]["amount"].split()[0])
    amount1 = int(inv1[0]["amount"].split()[0])
    assert amount1 > amount0


# ---------------------------------------------------------------- sessions

def test_sessions_requires_auth(client):
    r = client.get("/api/account/sessions")
    assert r.status_code == 401


def test_sessions_returns_current(client):
    tok = _token(client)
    r = client.get("/api/account/sessions", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200, r.text
    sessions = r.json()
    assert len(sessions) == 1
    assert sessions[0]["current"] is True
    assert "admin" in sessions[0]["device"]
