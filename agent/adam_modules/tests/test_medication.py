"""Testy F6 — medication tracker + adherence + MedGuard."""
from datetime import datetime, time, timedelta

import pytest

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.medication import (
    MedicationService,
    MedicationCreate,
    MedicationUpdate,
    ScheduleCreate,
    MedForm,
    DoseStatus,
)
from adam_modules.medication.service import (
    MISSED_AFTER_MINUTES,
    MEDGUARD_MISSED_THRESHOLD,
)


def _make_senior(session):
    return SeniorService(session).create(
        SeniorCreate(first_name="Jan", last_name="Kowalski", phone="+48123456789")
    )


def _make_med(session, senior, at=time(8, 0), days_mask=0b1111111):
    svc = MedicationService(session)
    return svc.create(
        senior,
        MedicationCreate(
            name="Ramipril",
            dosage="1 tabletka 5mg",
            form=MedForm.tablet,
            instructions="rano po posiłku",
            schedules=[ScheduleCreate(at_time=at, days_mask=days_mask)],
        ),
    )


def test_create_medication_with_schedule(session):
    senior = _make_senior(session)
    med = _make_med(session, senior)
    assert med.id is not None
    assert med.form == MedForm.tablet
    assert len(med.schedules) == 1
    assert med.schedules[0].at_time == time(8, 0)


def test_list_and_deactivate(session):
    senior = _make_senior(session)
    svc = MedicationService(session)
    _make_med(session, senior)
    m2 = _make_med(session, senior)
    assert len(svc.list_for_senior(senior.id)) == 2
    svc.deactivate(m2)
    assert len(svc.list_for_senior(senior.id)) == 1
    assert len(svc.list_for_senior(senior.id, only_active=False)) == 2


def test_update_medication(session):
    senior = _make_senior(session)
    svc = MedicationService(session)
    med = _make_med(session, senior)
    svc.update(med, MedicationUpdate(dosage="2 tabletki", prescriber="dr Nowak"))
    assert med.dosage == "2 tabletki"
    assert med.prescriber == "dr Nowak"


def test_schedule_occurs_on():
    from adam_modules.medication.models import MedicationSchedule
    # tylko poniedziałek (bit 0)
    sch = MedicationSchedule(at_time=time(8, 0), days_mask=0b0000001)
    assert sch.occurs_on(0) is True
    assert sch.occurs_on(1) is False


def test_generate_doses_for_day(session):
    senior = _make_senior(session)
    _make_med(session, senior, days_mask=0b1111111)
    svc = MedicationService(session)
    # środa
    day = datetime(2027, 1, 6, 0, 0)  # 2027-01-06 = środa
    doses = svc.generate_doses_for_day(senior.id, day)
    assert len(doses) == 1
    assert doses[0].status == DoseStatus.scheduled
    # idempotencja — drugie wywołanie nie duplikuje
    doses2 = svc.generate_doses_for_day(senior.id, day)
    assert len(doses2) == 0


def test_generate_doses_respects_days_mask(session):
    senior = _make_senior(session)
    _make_med(session, senior, days_mask=0b0000001)  # tylko poniedziałek
    svc = MedicationService(session)
    wednesday = datetime(2027, 1, 6, 0, 0)  # środa
    assert svc.generate_doses_for_day(senior.id, wednesday) == []
    monday = datetime(2027, 1, 4, 0, 0)  # poniedziałek
    assert len(svc.generate_doses_for_day(senior.id, monday)) == 1


def test_mark_taken_on_time(session):
    senior = _make_senior(session)
    _make_med(session, senior)
    svc = MedicationService(session)
    day = datetime(2027, 1, 6, 0, 0)
    dose = svc.generate_doses_for_day(senior.id, day)[0]
    svc.mark_taken(dose, when=dose.scheduled_at + timedelta(minutes=10))
    assert dose.status == DoseStatus.taken
    assert dose.taken_at is not None


def test_mark_taken_late(session):
    senior = _make_senior(session)
    _make_med(session, senior)
    svc = MedicationService(session)
    day = datetime(2027, 1, 6, 0, 0)
    dose = svc.generate_doses_for_day(senior.id, day)[0]
    svc.mark_taken(dose, when=dose.scheduled_at + timedelta(minutes=MISSED_AFTER_MINUTES + 30))
    assert dose.status == DoseStatus.late


def test_sweep_missed(session):
    senior = _make_senior(session)
    _make_med(session, senior)
    svc = MedicationService(session)
    day = datetime(2027, 1, 6, 0, 0)
    dose = svc.generate_doses_for_day(senior.id, day)[0]
    # "teraz" grubo po terminie
    now = dose.scheduled_at + timedelta(hours=5)
    missed = svc.sweep_missed(now=now)
    assert dose in missed
    assert dose.status == DoseStatus.missed


def test_adherence_report(session):
    senior = _make_senior(session)
    _make_med(session, senior)
    svc = MedicationService(session)
    base = datetime(2027, 1, 6, 0, 0)
    # 4 dawki w kolejne dni
    doses = []
    for i in range(4):
        d = svc.generate_doses_for_day(senior.id, base + timedelta(days=i))
        doses.extend(d)
    assert len(doses) == 4
    svc.mark_taken(doses[0], when=doses[0].scheduled_at)                    # taken
    svc.mark_taken(doses[1], when=doses[1].scheduled_at + timedelta(hours=3))  # late
    doses[2].status = DoseStatus.missed                                     # missed
    svc.mark_skipped(doses[3], note="lekarz odstawił")                      # skipped
    session.flush()

    rep = svc.adherence(
        senior.id,
        since=base - timedelta(days=1),
        until=base + timedelta(days=10),
    )
    assert rep.total_doses == 4
    assert rep.taken == 1 and rep.late == 1 and rep.missed == 1 and rep.skipped == 1
    # (taken+late)/(total-skipped) = 2/3
    assert rep.adherence_rate == pytest.approx(2 / 3, abs=1e-3)


def test_medguard_flag(session):
    senior = _make_senior(session)
    _make_med(session, senior)
    svc = MedicationService(session)
    now = datetime(2027, 1, 10, 12, 0)
    # poniżej progu
    for i in range(MEDGUARD_MISSED_THRESHOLD - 1):
        d = svc.generate_doses_for_day(senior.id, now - timedelta(days=i))[0]
        d.status = DoseStatus.missed
    session.flush()
    assert svc.medguard_flag(senior.id, now=now) is False
    # dobicie do progu
    d = svc.generate_doses_for_day(senior.id, now - timedelta(days=MEDGUARD_MISSED_THRESHOLD))[0]
    d.status = DoseStatus.missed
    session.flush()
    assert svc.medguard_flag(senior.id, now=now) is True
