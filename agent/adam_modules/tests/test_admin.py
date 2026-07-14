"""ETAP 35 — backend panelu Admina: flota / modele / providerzy / logi.

Testy serwisu (na sesji) + testy API (za rolą ADMIN, RBAC F11).
"""
import pytest
from fastapi.testclient import TestClient

from adam_modules.common import db as db_mod
from adam_modules.api import create_app
from adam_modules.admin import (
    AdminService, FleetStatus, ModelKind, ModelStatus,
    ProviderState, LogLevel,
)
from adam_modules.auth import Role, create_token_pair


@pytest.fixture()
def client():
    db_mod.init_engine("sqlite:///:memory:")
    app = create_app(init_db=True)
    with TestClient(app) as c:
        yield c


# ---------------- helpers ----------------
def _admin_headers():
    pair = create_token_pair(sub="admin@silvertech.pl", role=Role.ADMIN)
    return {"Authorization": f"Bearer {pair.access_token}"}


def _family_headers():
    pair = create_token_pair(sub="rodzina@dom.pl", role=Role.FAMILY, senior_ids=["SR-1"])
    return {"Authorization": f"Bearer {pair.access_token}"}


# ================================================= SERWIS: FLOTA
def test_fleet_register_and_summary(session):
    svc = AdminService(session)
    u1 = svc.register_unit("adam-fra-01", "Frankfurt node 1", capacity=40)
    svc.register_unit("adam-fra-02", "Frankfurt node 2", capacity=60)
    svc.set_unit_status(u1.id, FleetStatus.online, active_calls=7)
    summary = svc.fleet_summary()
    assert summary["total"] == 2
    assert summary["online"] == 1
    assert summary["active_calls"] == 7
    assert summary["capacity"] == 100


def test_fleet_set_status_unknown_raises(session):
    svc = AdminService(session)
    with pytest.raises(ValueError):
        svc.set_unit_status(9999, FleetStatus.online)


# ================================================= SERWIS: MODELE
def test_model_primary_is_exclusive_per_kind(session):
    svc = AdminService(session)
    m1 = svc.register_model(ModelKind.asr, "whisper-large-v3", "openai", is_primary=True)
    m2 = svc.register_model(ModelKind.asr, "deepgram-nova-2", "deepgram", status=ModelStatus.standby)
    # ustaw drugi jako primary → pierwszy przestaje być primary
    svc.set_primary_model(m2.id)
    models = {m.name: m for m in svc.models(ModelKind.asr)}
    assert models["deepgram-nova-2"].is_primary is True
    assert models["whisper-large-v3"].is_primary is False


def test_models_filter_by_kind(session):
    svc = AdminService(session)
    svc.register_model(ModelKind.asr, "whisper", "openai")
    svc.register_model(ModelKind.llm, "gpt", "openai")
    svc.register_model(ModelKind.tts, "eleven", "elevenlabs")
    assert len(svc.models(ModelKind.llm)) == 1
    assert len(svc.models()) == 3


# ================================================= SERWIS: PROVIDERZY (fail-safe ENV)
def test_provider_state_missing_secrets(session, monkeypatch):
    for v in ("ADAM_TWILIO_SID", "ADAM_TWILIO_TOKEN", "ADAM_TWILIO_FROM"):
        monkeypatch.delenv(v, raising=False)
    assert AdminService.probe_provider_state("twilio") == ProviderState.missing_secrets


def test_provider_state_configured_with_secrets(session, monkeypatch):
    monkeypatch.setenv("ADAM_TWILIO_SID", "AC_x")
    monkeypatch.setenv("ADAM_TWILIO_TOKEN", "tok")
    monkeypatch.setenv("ADAM_TWILIO_FROM", "+48500000000")
    assert AdminService.probe_provider_state("twilio") == ProviderState.configured


def test_sync_providers_creates_catalog(session, monkeypatch):
    for v in ("ADAM_TWILIO_SID", "ADAM_TWILIO_TOKEN", "ADAM_TWILIO_FROM",
              "ADAM_SENDGRID_KEY", "ADAM_SENDGRID_FROM", "ADAM_FCM_KEY",
              "ADAM_OPENAI_KEY", "ADAM_ELEVENLABS_KEY", "ADAM_DEEPGRAM_KEY"):
        monkeypatch.delenv(v, raising=False)
    svc = AdminService(session)
    providers = svc.sync_providers()
    keys = {p.key for p in providers}
    assert {"twilio", "sendgrid", "fcm", "openai"}.issubset(keys)
    assert all(p.state == ProviderState.missing_secrets for p in providers)
    # idempotencja — drugi sync nie duplikuje
    again = svc.sync_providers()
    assert len(again) == len(providers)


# ================================================= SERWIS: LOGI
def test_logs_record_and_filter(session):
    svc = AdminService(session)
    svc.log(LogLevel.info, "fleet", "node online")
    svc.log(LogLevel.error, "voice", "ASR timeout", actor="admin@x.pl")
    svc.log(LogLevel.warning, "voice", "high latency")
    assert len(svc.logs()) == 3
    assert len(svc.logs(level=LogLevel.error)) == 1
    assert len(svc.logs(source="voice")) == 2
    # najnowszy pierwszy
    assert svc.logs()[0].message == "high latency"


# ================================================= API (RBAC ADMIN)
def test_api_admin_requires_auth(client):
    r = client.get("/api/admin/fleet")
    assert r.status_code == 401


def test_api_admin_forbidden_for_family(client):
    r = client.get("/api/admin/fleet", headers=_family_headers())
    assert r.status_code == 403


def test_api_fleet_crud(client):
    h = _admin_headers()
    r = client.post("/api/admin/fleet", headers=h,
                    json={"code": "adam-01", "name": "Node 1", "capacity": 30})
    assert r.status_code == 200
    uid = r.json()["id"]
    r = client.patch(f"/api/admin/fleet/{uid}", headers=h,
                     json={"status": "online", "active_calls": 5})
    assert r.status_code == 200
    assert r.json()["status"] == "online"
    r = client.get("/api/admin/fleet/summary", headers=h)
    assert r.json()["online"] == 1
    assert r.json()["active_calls"] == 5


def test_api_fleet_patch_unknown_404(client):
    r = client.patch("/api/admin/fleet/9999", headers=_admin_headers(),
                     json={"status": "offline"})
    assert r.status_code == 404


def test_api_models_and_primary(client):
    h = _admin_headers()
    r = client.post("/api/admin/models", headers=h,
                    json={"kind": "asr", "name": "whisper", "provider": "openai", "is_primary": True})
    assert r.status_code == 200
    m1 = r.json()["id"]
    r = client.post("/api/admin/models", headers=h,
                    json={"kind": "asr", "name": "deepgram", "provider": "deepgram"})
    m2 = r.json()["id"]
    r = client.patch(f"/api/admin/models/{m2}/primary", headers=h)
    assert r.status_code == 200
    assert r.json()["is_primary"] is True
    r = client.get("/api/admin/models?kind=asr", headers=h)
    primaries = [m for m in r.json() if m["is_primary"]]
    assert len(primaries) == 1
    assert primaries[0]["id"] == m2


def test_api_providers_list_autoinit(client):
    r = client.get("/api/admin/providers", headers=_admin_headers())
    assert r.status_code == 200
    keys = {p["key"] for p in r.json()}
    assert "twilio" in keys and "openai" in keys


def test_api_logs_create_and_list(client):
    h = _admin_headers()
    client.post("/api/admin/logs", headers=h,
                json={"level": "warning", "source": "fleet", "message": "test log"})
    r = client.get("/api/admin/logs?source=fleet", headers=h)
    assert r.status_code == 200
    assert any(e["message"] == "test log" for e in r.json())
