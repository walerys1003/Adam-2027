"""Testy F10 — wearables (adaptery + threshold engine + audyt SHA-256)."""
from datetime import datetime

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.wearables import (
    WearableService, WearableVendor, VitalType,
)


def _senior(session):
    return SeniorService(session).create(
        SeniorCreate(first_name="Jan", last_name="Kowalski", phone="+48123456789")
    )


def test_register_device(session):
    s = _senior(session)
    svc = WearableService(session)
    dev = svc.register_device(s, WearableVendor.fitbit, "fitbit-123", model="Charge 6")
    assert dev.id is not None
    assert len(svc.devices(s.id)) == 1


def test_ingest_reading_normal(session):
    s = _senior(session)
    svc = WearableService(session)
    dev = svc.register_device(s, WearableVendor.generic, "gen-1")
    r = svc.ingest_reading(dev, VitalType.heart_rate, 72.0)
    assert r.breached is False
    assert dev.last_sync_at is not None


def test_ingest_reading_breach(session):
    s = _senior(session)
    svc = WearableService(session)
    dev = svc.register_device(s, WearableVendor.generic, "gen-1")
    r = svc.ingest_reading(dev, VitalType.spo2, 85.0)  # < 90 default
    assert r.breached is True


def test_manual_threshold_override(session):
    s = _senior(session)
    svc = WearableService(session)
    dev = svc.register_device(s, WearableVendor.generic, "gen-1")
    # zawęź próg HR ręcznie
    svc.set_threshold(s, VitalType.heart_rate, min_value=60, max_value=100)
    assert svc.is_breach(s.id, VitalType.heart_rate, 110) is True
    assert svc.is_breach(s.id, VitalType.heart_rate, 80) is False
    lo, hi = svc.effective_threshold(s.id, VitalType.heart_rate)
    assert (lo, hi) == (60, 100)


def test_audit_hash_integrity(session):
    s = _senior(session)
    svc = WearableService(session)
    dev = svc.register_device(s, WearableVendor.generic, "gen-1")
    r = svc.ingest_reading(dev, VitalType.heart_rate, 72.0)
    assert svc.verify_integrity(r) is True
    # symulacja manipulacji
    r.value = 999.0
    assert svc.verify_integrity(r) is False


def test_ingest_payload_fitbit(session):
    s = _senior(session)
    svc = WearableService(session)
    dev = svc.register_device(s, WearableVendor.fitbit, "fitbit-123")
    readings = svc.ingest_payload(dev, {
        "dateTime": "2027-01-06T08:00:00",
        "restingHeartRate": 68,
        "spo2": 97,
        "steps": 3200,
    })
    assert len(readings) == 3
    types = {r.vital_type for r in readings}
    assert VitalType.heart_rate in types and VitalType.spo2 in types


def test_ingest_payload_xiaomi(session):
    s = _senior(session)
    svc = WearableService(session)
    dev = svc.register_device(s, WearableVendor.xiaomi_zepp, "zepp-1")
    readings = svc.ingest_payload(dev, {"time": "2027-01-06T09:00:00", "hr": 75, "spo2": 96})
    assert len(readings) == 2


def test_ingest_payload_apple(session):
    s = _senior(session)
    svc = WearableService(session)
    dev = svc.register_device(s, WearableVendor.apple_health, "apple-1")
    readings = svc.ingest_payload(dev, {"samples": [
        {"type": "HKQuantityTypeIdentifierHeartRate", "value": 70, "endDate": "2027-01-06T10:00:00"},
        {"type": "HKQuantityTypeIdentifierStepCount", "value": 5000, "endDate": "2027-01-06T10:00:00"},
    ]})
    assert len(readings) == 2


def test_latest_and_breaches(session):
    s = _senior(session)
    svc = WearableService(session)
    dev = svc.register_device(s, WearableVendor.generic, "gen-1")
    svc.ingest_reading(dev, VitalType.spo2, 95.0, measured_at=datetime(2027, 1, 6, 8, 0))
    svc.ingest_reading(dev, VitalType.spo2, 84.0, measured_at=datetime(2027, 1, 6, 9, 0))
    latest = svc.latest(s.id, VitalType.spo2)
    assert latest.value == 84.0
    assert len(svc.breaches(s.id)) == 1
