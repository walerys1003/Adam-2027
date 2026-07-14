"""Testy F17 — integracja 112 (payload ratunkowy)."""
from datetime import date

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.emergency import EmergencyService
from adam_modules.medication import MedicationService, MedicationCreate, ScheduleCreate, MedForm
from adam_modules.wearables import WearableService, WearableVendor, VitalType


def _senior(session):
    return SeniorService(session).create(
        SeniorCreate(
            first_name="Jan", last_name="Kowalski", phone="+48123456789",
            birth_date=date(1945, 3, 1), address="ul. Sołacka 5, Poznań", district="Sołacz",
        )
    )


def test_build_payload_basic(session):
    s = _senior(session)
    svc = EmergencyService(session)
    p = svc.build_payload(s, reason="ból w klatce piersiowej")
    assert p.full_name == "Jan Kowalski"
    assert p.age is not None and p.age >= 80
    assert p.address == "ul. Sołacka 5, Poznań"
    assert p.reason == "ból w klatce piersiowej"


def test_payload_includes_medications(session):
    s = _senior(session)
    MedicationService(session).create(s, MedicationCreate(
        name="Ramipril", dosage="5mg", form=MedForm.tablet,
        schedules=[ScheduleCreate(at_time=__import__("datetime").time(8, 0))],
    ))
    p = EmergencyService(session).build_payload(s, reason="omdlenie")
    assert any("Ramipril" in m for m in p.medications)


def test_payload_includes_recent_vitals(session):
    s = _senior(session)
    dev = WearableService(session).register_device(s, WearableVendor.generic, "g1")
    WearableService(session).ingest_reading(dev, VitalType.heart_rate, 42.0)
    p = EmergencyService(session).build_payload(s, reason="zasłabnięcie")
    assert "heart_rate" in p.recent_vitals


def test_dispatch_summary(session):
    s = _senior(session)
    p = EmergencyService(session).build_payload(s, reason="duszność")
    summary = p.dispatch_summary()
    assert "duszność" in summary
    assert "Jan Kowalski" in summary
    assert "Sołacka" in summary


def test_payload_serializable(session):
    s = _senior(session)
    p = EmergencyService(session).build_payload(s, reason="test")
    d = p.to_dict()
    assert d["external_id"] == s.external_id
    assert "recent_vitals" in d


# ---- F15 (ETAP 26): audio + dispatch + rejestr + dialplan ----
def test_build_emergency_audio_script(session):
    from adam_modules.emergency import build_emergency_audio
    s = _senior(session)
    p = EmergencyService(session).build_payload(s, reason="ból w klatce piersiowej")
    script = build_emergency_audio(p)
    text = script.full_text()
    assert "zagrożenia życia" in text
    assert "Jan Kowalski" in text
    assert "Sołacka" in text
    # numer telefonu rozpisany słownie
    assert "jeden" in text
    # sekcja powtórzenia obecna
    assert script.repeat_notice in script.segments


def test_dispatch_creates_simulated_call_in_dev(session):
    s = _senior(session)
    call = EmergencyService(session).dispatch(s, reason="kryzys PURPLE")
    assert call.id is not None
    assert call.status.value == "simulated"   # brak originatora w dev
    assert call.audio_script and "zagrożenia życia" in call.audio_script
    assert call.payload_json


def test_dispatch_with_originator_ok(session):
    from adam_modules.emergency import OriginateResult
    s = _senior(session)

    class FakeOriginator:
        def originate(self, *, number, audio_ref):
            return OriginateResult(ok=True, channel_id="ch-112-1", detail="połączono")

    call = EmergencyService(session).dispatch(s, reason="upadek", originator=FakeOriginator())
    assert call.status.value == "dispatched"
    assert call.channel_id == "ch-112-1"


def test_emergency_history(session):
    s = _senior(session)
    svc = EmergencyService(session)
    svc.dispatch(s, reason="raz")
    svc.dispatch(s, reason="dwa")
    hist = svc.history(s.id)
    assert len(hist) == 2
    assert hist[0].reason == "dwa"   # DESC


def test_render_dialplan():
    from adam_modules.emergency import render_emergency_dialplan
    dp = render_emergency_dialplan()
    assert "[adam-emergency]" in dp
    assert "call112" in dp
    assert "Playback" in dp
