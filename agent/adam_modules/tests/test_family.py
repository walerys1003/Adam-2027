"""Testy F9 — dashboard rodzinny + notyfikacje wg poziomu semafora."""
from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.seniors.models import SemaphoreLevel
from adam_modules.family import (
    FamilyService, FamilyRole, NotifyChannel, DeliveryMode,
    NotificationStatus, SmsAdapter, EmailAdapter,
)


def _senior(session):
    return SeniorService(session).create(
        SeniorCreate(first_name="Jan", last_name="Kowalski", phone="+48123456789")
    )


def _svc(session):
    return FamilyService(session, adapters={"sms": SmsAdapter(), "email": EmailAdapter()})


def test_add_member(session):
    s = _senior(session)
    svc = _svc(session)
    fm = svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700")
    assert fm.id is not None
    assert fm.role == FamilyRole.primary
    assert len(svc.members(s.id)) == 1


def test_green_no_notifications(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700")
    out = svc.dispatch(s, SemaphoreLevel.green, title="OK", body="rutyna")
    assert out == []


def test_yellow_digest(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700")
    out = svc.dispatch(s, SemaphoreLevel.yellow, title="Uwaga", body="gorszy nastrój", hour=12)
    assert len(out) == 1
    assert out[0].mode == DeliveryMode.digest
    assert out[0].status == NotificationStatus.sent


def test_red_immediate_excludes_observer(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700")
    svc.add_member(s, "Sąsiad", FamilyRole.observer, phone="+48111222333")
    out = svc.dispatch(s, SemaphoreLevel.red, title="Pilne", body="brak odpowiedzi", hour=12)
    # obserwator wykluczony z alertów krytycznych
    assert len(out) == 1
    assert out[0].mode == DeliveryMode.immediate


def test_purple_bypass_dnd(session):
    s = _senior(session)
    svc = _svc(session)
    # opiekun w trybie DND (22-7), ale PURPLE ma bypass
    svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700",
                   dnd_start=22, dnd_end=7)
    out = svc.dispatch(s, SemaphoreLevel.purple, title="KRYZYS", body="ból w klatce", hour=3)
    assert len(out) == 1
    assert out[0].mode == DeliveryMode.bypass_dnd
    assert out[0].status == NotificationStatus.sent


def test_dnd_holds_yellow(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Anna", FamilyRole.secondary, phone="+48500600700",
                   dnd_start=22, dnd_end=7)
    out = svc.dispatch(s, SemaphoreLevel.yellow, title="Uwaga", body="x", hour=3)
    assert out[0].status == NotificationStatus.pending  # wstrzymane przez DND


def test_red_critical_role_ignores_dnd(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Koordynator", FamilyRole.coordinator, phone="+48500600700",
                   dnd_start=22, dnd_end=7)
    out = svc.dispatch(s, SemaphoreLevel.red, title="Pilne", body="x", hour=3)
    # rola krytyczna przy RED ignoruje DND
    assert out[0].status == NotificationStatus.sent


def test_dnd_window_across_midnight(session):
    s = _senior(session)
    svc = _svc(session)
    fm = svc.add_member(s, "Anna", FamilyRole.secondary, dnd_start=22, dnd_end=7)
    assert svc.in_dnd(fm, 23) is True
    assert svc.in_dnd(fm, 3) is True
    assert svc.in_dnd(fm, 12) is False


def test_acknowledge_and_feed(session):
    s = _senior(session)
    svc = _svc(session)
    svc.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700")
    out = svc.dispatch(s, SemaphoreLevel.red, title="Pilne", body="x", hour=12)
    svc.acknowledge(out[0])
    assert out[0].status == NotificationStatus.acknowledged
    feed = svc.feed(s.id)
    assert len(feed) == 1
