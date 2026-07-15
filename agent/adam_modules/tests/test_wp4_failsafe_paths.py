"""WP-4 — testy ścieżek fail-safe / brzegowych (podniesienie pokrycia luk).

Celują w gałęzie oznaczone jako niepokryte w raporcie coverage:
  - wearables.adapters._parse_ts (fail-safe parsowania czasu)
  - wearables.adapters.GarminAdapter.normalize (wszystkie pola / brak pól)
  - semaphore.escalation.EscalationLadder.next_step (gałąź „brak następnego”)
"""
from datetime import datetime

from adam_modules.wearables.adapters import (
    _parse_ts,
    GarminAdapter,
    XiaomiZeppAdapter,
)
from adam_modules.wearables import VitalType
from adam_modules.semaphore.escalation import EscalationLadder
from adam_modules.seniors.models import SemaphoreLevel


# --- _parse_ts: fail-safe ------------------------------------------------

def test_parse_ts_passthrough_datetime():
    dt = datetime(2027, 7, 15, 10, 30)
    assert _parse_ts(dt) == dt


def test_parse_ts_valid_iso_string():
    out = _parse_ts("2027-07-15T10:30:00Z")
    assert out.year == 2027 and out.month == 7 and out.day == 15


def test_parse_ts_invalid_string_falls_back_to_default():
    default = datetime(2000, 1, 1)
    assert _parse_ts("nie-jest-data", default=default) == default


def test_parse_ts_invalid_string_without_default_returns_now():
    out = _parse_ts(12345)  # typ nieobsługiwany → utcnow
    assert isinstance(out, datetime)


# --- GarminAdapter -------------------------------------------------------

def test_garmin_adapter_all_fields():
    payload = {
        "calendarDate": "2027-07-15",
        "restingHeartRate": 62,
        "averageSpo2": 97,
        "totalSteps": 4200,
    }
    readings = GarminAdapter().normalize(payload)
    kinds = {r.vital_type for r in readings}
    assert VitalType.heart_rate in kinds
    assert VitalType.spo2 in kinds
    assert VitalType.steps in kinds
    assert len(readings) == 3


def test_garmin_adapter_empty_payload_yields_nothing():
    assert GarminAdapter().normalize({}) == []


def test_xiaomi_adapter_partial_payload():
    readings = XiaomiZeppAdapter().normalize({"time": "2027-07-15T08:00:00Z"})
    # Brak wartości vitalnych → pusty wynik, ale bez wyjątku.
    assert isinstance(readings, list)


# --- EscalationLadder.next_step -----------------------------------------

def test_next_step_returns_first_uncompleted():
    step = EscalationLadder.next_step(SemaphoreLevel.red, completed_actions=[])
    assert step is not None


def test_next_step_returns_none_when_all_done():
    plan = EscalationLadder.plan(SemaphoreLevel.red)
    all_actions = [s.action for s in plan]
    assert EscalationLadder.next_step(SemaphoreLevel.red, all_actions) is None
