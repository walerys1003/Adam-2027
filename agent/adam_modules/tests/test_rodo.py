"""Testy F12 — RODO (retencja + soft-delete + eksport + prawo do zapomnienia)."""
from datetime import datetime, timedelta

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.rodo import RodoService, ProcessingAction, DataCategory, RETENTION_DAYS
from adam_modules.memory import MemoryService, MemoryKind
from adam_modules.family import FamilyService, FamilyRole
from adam_modules.wearables import WearableService, WearableVendor, VitalType


def _senior(session):
    return SeniorService(session).create(
        SeniorCreate(first_name="Jan", last_name="Kowalski",
                     pesel=None, phone="+48123456789")
    )


def test_retention_expiry():
    svc = RodoService
    now = datetime(2027, 6, 1)
    # nagranie sprzed 40 dni (limit 30) — wygasło
    old = now - timedelta(days=40)
    assert RodoService.is_expired(DataCategory.recordings, old, now) is True
    # transkrypt sprzed 40 dni (limit 365) — nie wygasł
    assert RodoService.is_expired(DataCategory.transcripts, old, now) is False


def test_retention_days_config():
    assert RETENTION_DAYS[DataCategory.recordings] == 30
    assert RETENTION_DAYS[DataCategory.transcripts] == 365
    assert RETENTION_DAYS[DataCategory.reports] == 730


def test_log_and_audit_trail(session):
    s = _senior(session)
    rodo = RodoService(session)
    rodo.log(s.id, ProcessingAction.access, actor="operator1")
    rodo.log(s.id, ProcessingAction.export, actor="operator1")
    trail = rodo.audit_trail(s.id)
    assert len(trail) == 2
    assert trail[0].action == ProcessingAction.export  # najnowszy pierwszy


def test_export_data(session):
    s = _senior(session)
    MemoryService(session).remember(s, "lubi kawę", MemoryKind.preference)
    rodo = RodoService(session)
    data = rodo.export_data(s, actor="operator1")
    assert data["senior"]["first_name"] == "Jan"
    assert data["senior"]["phone"] == "+48123456789"
    assert len(data["memory"]) == 1
    # eksport logowany
    trail = rodo.audit_trail(s.id)
    assert any(t.action == ProcessingAction.export for t in trail)


def test_export_json_serializable(session):
    s = _senior(session)
    rodo = RodoService(session)
    js = rodo.export_json(s)
    assert '"first_name": "Jan"' in js


def test_soft_delete(session):
    s = _senior(session)
    rodo = RodoService(session)
    rodo.soft_delete(s, actor="operator1")
    assert s.active is False
    assert any(t.action == ProcessingAction.soft_delete for t in rodo.audit_trail(s.id))


def test_erase_senior_right_to_be_forgotten(session):
    s = _senior(session)
    # zasil dane w kilku modułach
    MemoryService(session).remember(s, "fakt 1", MemoryKind.fact)
    MemoryService(session).remember(s, "fakt 2", MemoryKind.fact)
    FamilyService(session).add_member(s, "Anna", FamilyRole.primary, phone="+48500600700")
    dev = WearableService(session).register_device(s, WearableVendor.generic, "g1")
    WearableService(session).ingest_reading(dev, VitalType.heart_rate, 72.0)

    rodo = RodoService(session)
    counts = rodo.erase_senior(s, actor="dpo")

    assert counts["memory"] == 2
    assert counts["family_members"] == 1
    assert counts["vitals"] == 1
    assert counts["devices"] == 1
    # profil zanonimizowany
    assert s.first_name == "ANONIM"
    assert s.pesel is None
    assert s.phone is None
    assert s.active is False
    # operacja zalogowana (dowód wykonania art. 17)
    assert any(t.action == ProcessingAction.erase for t in rodo.audit_trail(s.id))


def test_erase_leaves_audit_log(session):
    s = _senior(session)
    rodo = RodoService(session)
    rodo.erase_senior(s, actor="dpo")
    # log przetwarzania pozostaje jako dowód
    assert len(rodo.audit_trail(s.id)) >= 1
