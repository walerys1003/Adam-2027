"""Testy warstwy API (ETAP 9) — FastAPI TestClient na bazie SQLite in-memory.

Każdy test dostaje świeżą aplikację z pustą bazą (StaticPool → współdzielone
połączenie in-memory). Pokrywa wszystkie routery F1–F18.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from adam_modules.common import db as db_mod
from adam_modules.api import create_app


@pytest.fixture()
def client():
    # świeża baza in-memory na każdy test
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


# ---- system ----
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_live(client):
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_ready_ok_with_db(client):
    """Readiness zwraca 200 + database:ok gdy baza dostępna (ETAP 23)."""
    r = client.get("/health/ready")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "ready"
    assert body["checks"]["database"] == "ok"


def test_health_endpoints_no_api_key_needed(client):
    """Health musi być dostępny bez X-API-Key (dla load balancera / k8s)."""
    for path in ("/health", "/health/live", "/health/ready"):
        r = client.get(path)
        assert r.status_code in (200, 503), f"{path} → {r.status_code}"


def test_openapi_available(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "/api/seniors" in r.json()["paths"]


# ---- F1 seniors ----
def test_seniors_crud(client):
    created = _make_senior(client)
    sid = created["id"]
    assert created["external_id"].startswith("SR-")

    # get
    g = client.get(f"/api/seniors/{sid}")
    assert g.status_code == 200
    assert g.json()["first_name"] == "Jan"

    # list
    lst = client.get("/api/seniors")
    assert lst.json()["total"] == 1

    # patch
    p = client.patch(f"/api/seniors/{sid}", json={"district": "Grunwald"})
    assert p.status_code == 200 and p.json()["district"] == "Grunwald"

    # by external
    ext = client.get(f"/api/seniors/by-external/{created['external_id']}")
    assert ext.status_code == 200

    # deactivate
    d = client.delete(f"/api/seniors/{sid}")
    assert d.status_code == 204
    assert client.get(f"/api/seniors/{sid}").json()["active"] is False


def test_senior_pii_masked(client):
    r = client.post("/api/seniors", json={
        "first_name": "Anna", "last_name": "Nowak",
        "phone": "+48123456789",
    })
    assert r.status_code == 201
    body = r.json()
    # telefon zamaskowany, brak surowego numeru
    assert body["phone_masked"] and body["phone_masked"].endswith("789")
    assert "phone" not in body or body.get("phone") is None


def test_senior_404(client):
    assert client.get("/api/seniors/9999").status_code == 404


def test_senior_bad_pesel_422(client):
    r = client.post("/api/seniors", json={
        "first_name": "X", "last_name": "Y", "pesel": "0000000001",
    })
    assert r.status_code == 422


# ---- F3/F4/F8 safety ----
def test_safety_crisis_purple(client):
    s = _make_senior(client)
    r = client.post("/api/safety/analyze", json={
        "text": "boli mnie w klatce piersiowej", "apply_to_senior_id": s["id"],
    })
    assert r.status_code == 200
    body = r.json()
    assert body["level"] == "purple"
    assert body["valid"] is True
    assert body["applied"] is True
    assert len(body["escalation"]) == 3
    # 112 pierwszy krok, bypass DND
    assert body["escalation"][0]["action"] == "call_112"
    assert body["escalation"][0]["bypass_dnd"] is True


def test_safety_routine_green(client):
    r = client.post("/api/safety/analyze", json={"text": "dzień dobry, wszystko w porządku"})
    assert r.status_code == 200
    assert r.json()["level"] == "green"
    assert r.json()["escalation"] == []


def test_safety_history_and_resolve(client):
    s = _make_senior(client)
    client.post("/api/safety/analyze", json={
        "text": "nie mogę oddychać", "apply_to_senior_id": s["id"]})
    hist = client.get(f"/api/safety/seniors/{s['id']}/history")
    assert hist.status_code == 200 and len(hist.json()) >= 1

    res = client.post(f"/api/safety/seniors/{s['id']}/resolve", json={"note": "fałszywy alarm"})
    assert res.status_code == 200 and res.json()["level"] == "green"


def test_safety_vitals_breach(client):
    s = _make_senior(client)
    r = client.post("/api/safety/analyze", json={
        "vitals": {"spo2": 82}, "apply_to_senior_id": s["id"]})
    assert r.status_code == 200
    assert r.json()["level"] in ("red", "purple")


# ---- F6 medications ----
def test_medications_and_adherence(client):
    s = _make_senior(client)
    m = client.post(f"/api/seniors/{s['id']}/medications", json={
        "name": "Ramipril", "dosage": "5mg", "form": "tablet",
        "schedules": [{"at_time": "08:00:00", "days_mask": 127}],
    })
    assert m.status_code == 201, m.text
    assert m.json()["name"] == "Ramipril"

    lst = client.get(f"/api/seniors/{s['id']}/medications")
    assert len(lst.json()) == 1

    adh = client.get(f"/api/seniors/{s['id']}/medications/adherence?days=30")
    assert adh.status_code == 200
    assert "total_doses" in adh.json()


# ---- F10 wearables ----
def test_wearables_flow(client):
    s = _make_senior(client)
    dev = client.post(f"/api/seniors/{s['id']}/wearables/devices", json={
        "vendor": "apple_health", "external_id": "AH-1", "model": "Watch"})
    assert dev.status_code == 201, dev.text
    did = dev.json()["id"]

    rd = client.post(f"/api/seniors/{s['id']}/wearables/readings", json={
        "device_id": did, "vital_type": "heart_rate", "value": 72})
    assert rd.status_code == 201
    assert rd.json()["integrity_ok"] is True

    latest = client.get(f"/api/seniors/{s['id']}/wearables/latest/heart_rate")
    assert latest.status_code == 200 and latest.json()["value"] == 72

    # przekroczenie
    client.post(f"/api/seniors/{s['id']}/wearables/readings", json={
        "device_id": did, "vital_type": "spo2", "value": 80})
    br = client.get(f"/api/seniors/{s['id']}/wearables/breaches")
    assert br.status_code == 200 and len(br.json()) >= 1


# ---- F9 family ----
def test_family_members_and_dispatch(client):
    s = _make_senior(client)
    mem = client.post(f"/api/seniors/{s['id']}/family/members", json={
        "name": "Córka Ewa", "role": "primary", "phone": "+48111222333",
        "preferred_channel": "sms"})
    assert mem.status_code == 201, mem.text

    disp = client.post(f"/api/seniors/{s['id']}/family/dispatch", json={
        "level": "red", "title": "Alert", "body": "Wykryto problem", "hour": 12})
    assert disp.status_code == 200 and len(disp.json()) >= 1

    feed = client.get(f"/api/seniors/{s['id']}/family/feed")
    assert feed.status_code == 200 and len(feed.json()) >= 1


def test_family_green_no_dispatch(client):
    s = _make_senior(client)
    client.post(f"/api/seniors/{s['id']}/family/members", json={
        "name": "Syn", "role": "secondary", "phone": "+48999888777"})
    disp = client.post(f"/api/seniors/{s['id']}/family/dispatch", json={
        "level": "green", "title": "OK", "body": "rutyna"})
    assert disp.json() == []


def test_family_sse_events(client):
    s = _make_senior(client)
    r = client.get(f"/api/seniors/{s['id']}/family/events")
    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]
    assert "event: snapshot" in r.text


# ---- F11 marketplace ----
def test_marketplace_order_and_cancel(client):
    s = _make_senior(client)
    # zbuduj zweryfikowanego partnera + usługę bezpośrednio przez serwis
    from adam_modules.marketplace import MarketplaceService, ServiceCategory
    with db_mod.session_scope() as sess:
        ms = MarketplaceService(sess)
        p = ms.register_partner("MedCare", ServiceCategory.meals, nip="5260250274", insurance_oc=True)
        ms.verify_partner(p)
        svc = ms.add_service(p, "Obiady", 25.0)
        service_id = svc.id

    order = client.post("/api/marketplace/orders", json={
        "senior_id": s["id"], "service_id": service_id, "note": "bez cukru"})
    assert order.status_code == 201, order.text
    oid = order.json()["id"]
    assert order.json()["can_cancel"] is True

    lst = client.get(f"/api/marketplace/seniors/{s['id']}/orders")
    assert len(lst.json()) == 1

    cancel = client.post(f"/api/marketplace/orders/{oid}/cancel")
    assert cancel.status_code == 200 and cancel.json()["status"] == "cancelled"


def test_marketplace_services_list(client):
    r = client.get("/api/marketplace/services")
    assert r.status_code == 200 and isinstance(r.json(), list)


# ---- F12 rodo ----
def test_rodo_export_and_erase(client):
    s = _make_senior(client)
    exp = client.get(f"/api/seniors/{s['id']}/rodo/export")
    assert exp.status_code == 200 and exp.json()["senior"]["first_name"] == "Jan"

    audit = client.get(f"/api/seniors/{s['id']}/rodo/audit")
    assert audit.status_code == 200 and len(audit.json()) >= 1

    er = client.post(f"/api/seniors/{s['id']}/rodo/erase")
    assert er.status_code == 200 and "erased" in er.json()


# ---- F13 compliance ----
def test_compliance_disclosure(client):
    s = _make_senior(client)
    reg = client.get("/api/compliance/system-register")
    assert reg.json()["system_name"] == "Adam"

    d = client.post("/api/compliance/disclosures", json={
        "senior_id": s["id"], "conversation_ref": "conv-1", "channel": "voice"})
    assert d.status_code == 200 and d.json()["disclosed"] is True

    a = client.get("/api/compliance/disclosures/conv-1/asserted")
    assert a.json()["disclosed"] is True


# ---- F15 QA ----
def test_qa_evaluate(client):
    r = client.post("/api/compliance/qa/evaluate", json={
        "turns": [
            {"role": "assistant", "text": "Dzień dobry, tu Adam, asystent głosowy AI."},
            {"role": "user", "text": "Dzień dobry, czuję się dobrze dziękuję."},
        ],
        "duration_s": 60, "interruptions": 0, "completed": True,
    })
    assert r.status_code == 200
    assert 0 <= r.json()["score"] <= 100


# ---- F16 consensus ----
def test_consensus_disagreement_picks_higher(client):
    r = client.post("/api/compliance/consensus/decide", json={"votes": [
        {"source": "gpt", "level": "red", "trigger": "chest_pain", "confidence": 0.9},
        {"source": "claude", "level": "yellow", "trigger": "mood_low", "confidence": 0.8},
    ]})
    assert r.status_code == 200
    assert r.json()["level"] == "red"


# ---- F17 emergency ----
def test_emergency_payload(client):
    s = _make_senior(client)
    r = client.post(f"/api/compliance/emergency/{s['id']}/payload?reason=zawał")
    assert r.status_code == 200
    assert "payload" in r.json() and r.json()["dispatch_summary"]


# ---- F14 speech ----
def test_speech_profile(client):
    r = client.post("/api/compliance/speech/profile", json={
        "hearing": "moderate_loss", "pace": "slow", "age": 88})
    assert r.status_code == 200
    body = r.json()
    assert "speech_rate" in body and "volume_gain_db" in body


# ---- consents (F12, ETAP 25) ----
def test_consents_snapshot_empty(client):
    s = _make_senior(client)
    r = client.get(f"/api/seniors/{s['id']}/consents")
    assert r.status_code == 200
    body = r.json()
    assert body["ai_disclosure"] == "none"


def test_consents_gate_blocks_then_allows(client):
    s = _make_senior(client)
    # bramka blokuje bez zgód
    r = client.get(f"/api/seniors/{s['id']}/consents/gate")
    assert r.status_code == 200
    assert r.json()["allowed"] is False
    # udziel obowiązkowych zgód
    for ct in ("ai_disclosure", "health_processing"):
        rg = client.post(f"/api/seniors/{s['id']}/consents/grant",
                         json={"consent_type": ct, "source": "panel"})
        assert rg.status_code == 200, rg.text
    r2 = client.get(f"/api/seniors/{s['id']}/consents/gate")
    assert r2.json()["allowed"] is True


def test_call_start_blocked_without_consent(client):
    s = _make_senior(client)
    r = client.post("/api/voice/call-start",
                    json={"senior_external_id": s["external_id"], "reason": "welfare_check"})
    assert r.status_code == 200
    body = r.json()
    assert body["accepted"] is False
    assert "zgód" in body["detail"].lower() or "consent" in body["detail"].lower()


def test_consent_withdraw(client):
    s = _make_senior(client)
    client.post(f"/api/seniors/{s['id']}/consents/grant",
                json={"consent_type": "call_recording"})
    r = client.post(f"/api/seniors/{s['id']}/consents/withdraw",
                    json={"consent_type": "call_recording"})
    assert r.status_code == 200
    assert r.json()["status"] == "withdrawn"
