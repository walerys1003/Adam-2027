"""Testy F11 — marketplace (partnerzy + weryfikacja + zamówienia + anty-fraud)."""
from datetime import datetime, timedelta

import pytest

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.marketplace import (
    MarketplaceService, ServiceCategory, PartnerStatus, OrderStatus,
    validate_nip, CANCELLATION_WINDOW_MINUTES, FRAUD_SUSPEND_THRESHOLD,
)


def _senior(session):
    return SeniorService(session).create(
        SeniorCreate(first_name="Jan", last_name="Kowalski", phone="+48123456789")
    )


# ---- NIP ----
def test_validate_nip():
    assert validate_nip("5260250274") is True   # poprawny przykładowy NIP
    assert validate_nip("0000000001") is False   # błędna suma kontrolna
    assert validate_nip("1234567890") is False
    assert validate_nip("123") is False
    assert validate_nip(None) is False


def test_ten_categories_exist():
    assert len(list(ServiceCategory)) == 10


# ---- weryfikacja partnera ----
def test_verify_partner_ok(session):
    svc = MarketplaceService(session)
    p = svc.register_partner("SprzątamPL", ServiceCategory.home_help, nip="5260250274")
    svc.verify_partner(p)
    assert p.status == PartnerStatus.verified


def test_verify_rejects_bad_nip(session):
    svc = MarketplaceService(session)
    p = svc.register_partner("Fejk", ServiceCategory.home_help, nip="0000000001")
    svc.verify_partner(p)
    assert p.status == PartnerStatus.rejected


def test_oc_required_category(session):
    svc = MarketplaceService(session)
    # transport wymaga OC
    p = svc.register_partner("Transporter", ServiceCategory.transport, nip="5260250274", insurance_oc=False)
    svc.verify_partner(p)
    assert p.status == PartnerStatus.rejected
    p2 = svc.register_partner("TransporterOC", ServiceCategory.transport, nip="5260250274", insurance_oc=True)
    svc.verify_partner(p2)
    assert p2.status == PartnerStatus.verified


def test_fraud_suspend(session):
    svc = MarketplaceService(session)
    p = svc.register_partner("Podejrzany", ServiceCategory.shopping, nip="5260250274")
    svc.verify_partner(p)
    for _ in range(FRAUD_SUSPEND_THRESHOLD):
        svc.flag_fraud(p)
    assert p.status == PartnerStatus.suspended


# ---- usługi ----
def test_add_service_requires_verified(session):
    svc = MarketplaceService(session)
    p = svc.register_partner("Nowy", ServiceCategory.meals, nip="5260250274")
    with pytest.raises(ValueError):
        svc.add_service(p, "Obiady", 25.0)
    svc.verify_partner(p)
    s = svc.add_service(p, "Obiady", 25.0)
    assert s.id is not None


# ---- zamówienia ----
def _verified_service(session):
    svc = MarketplaceService(session)
    p = svc.register_partner("Catering", ServiceCategory.meals, nip="5260250274")
    svc.verify_partner(p)
    return svc, svc.add_service(p, "Obiad dnia", 22.0)


def test_create_order(session):
    s = _senior(session)
    svc, service = _verified_service(session)
    now = datetime(2027, 1, 6, 12, 0)
    order = svc.create_order(s, service, now=now)
    assert order.status == OrderStatus.created
    assert order.amount_pln == 22.0
    assert order.cancellable_until == now + timedelta(minutes=CANCELLATION_WINDOW_MINUTES)


def test_cancel_within_window(session):
    s = _senior(session)
    svc, service = _verified_service(session)
    now = datetime(2027, 1, 6, 12, 0)
    order = svc.create_order(s, service, now=now)
    svc.cancel_order(order, now=now + timedelta(minutes=10))
    assert order.status == OrderStatus.cancelled


def test_cancel_after_window_fails(session):
    s = _senior(session)
    svc, service = _verified_service(session)
    now = datetime(2027, 1, 6, 12, 0)
    order = svc.create_order(s, service, now=now)
    with pytest.raises(ValueError):
        svc.cancel_order(order, now=now + timedelta(minutes=40))


def test_complete_order(session):
    s = _senior(session)
    svc, service = _verified_service(session)
    order = svc.create_order(s, service)
    svc.confirm_order(order)
    svc.complete_order(order)
    assert order.status == OrderStatus.completed
    assert order.completed_at is not None


def test_order_from_unverified_partner_fails(session):
    s = _senior(session)
    svc = MarketplaceService(session)
    p = svc.register_partner("Catering", ServiceCategory.meals, nip="5260250274")
    svc.verify_partner(p)
    service = svc.add_service(p, "Obiad", 22.0)
    # zawieś partnera po utworzeniu usługi
    p.status = PartnerStatus.suspended
    session.flush()
    with pytest.raises(ValueError):
        svc.create_order(s, service)
