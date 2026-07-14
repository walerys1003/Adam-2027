"""Testy Consent Manager (F12, ETAP 25) — rejestr zgód + bramka zgód."""
from __future__ import annotations

from adam_modules.rodo import ConsentService, ConsentType, ConsentStatus
from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate


def _new_senior(db):
    return SeniorService(db).create(
        SeniorCreate(first_name="Anna", last_name="Nowak")
    )


def test_grant_and_current(session):
    s = _new_senior(session)
    svc = ConsentService(session)
    c = svc.grant(s.id, ConsentType.ai_disclosure, source="panel", actor="op1")
    assert c.status == ConsentStatus.granted
    assert svc.is_granted(s.id, ConsentType.ai_disclosure)


def test_withdraw_last_wins(session):
    s = _new_senior(session)
    svc = ConsentService(session)
    svc.grant(s.id, ConsentType.health_processing)
    assert svc.is_granted(s.id, ConsentType.health_processing)
    svc.withdraw(s.id, ConsentType.health_processing, actor="senior")
    assert not svc.is_granted(s.id, ConsentType.health_processing)
    # ponowne udzielenie znów aktywuje
    svc.grant(s.id, ConsentType.health_processing)
    assert svc.is_granted(s.id, ConsentType.health_processing)


def test_snapshot_contains_all_types(session):
    s = _new_senior(session)
    svc = ConsentService(session)
    snap = svc.snapshot(s.id)
    assert set(snap.keys()) == {ct.value for ct in ConsentType}
    assert all(v == "none" for v in snap.values())


def test_gate_blocks_without_mandatory(session):
    s = _new_senior(session)
    svc = ConsentService(session)
    gate = svc.check_call_gate(s.id)
    assert gate.allowed is False
    assert "ai_disclosure" in gate.missing_values
    assert "health_processing" in gate.missing_values


def test_gate_allows_with_mandatory(session):
    s = _new_senior(session)
    svc = ConsentService(session)
    svc.grant(s.id, ConsentType.ai_disclosure)
    svc.grant(s.id, ConsentType.health_processing)
    gate = svc.check_call_gate(s.id)
    assert gate.allowed is True
    assert gate.missing == []


def test_history_records_events(session):
    s = _new_senior(session)
    svc = ConsentService(session)
    svc.grant(s.id, ConsentType.ai_disclosure)
    svc.withdraw(s.id, ConsentType.ai_disclosure)
    hist = svc.history(s.id)
    assert len(hist) == 2
