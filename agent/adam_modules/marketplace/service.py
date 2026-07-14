"""
MarketplaceService — partnerzy, usługi, zamówienia + anty-fraud (F11).

Weryfikacja partnera (F11.2): NIP (10 cyfr + suma kontrolna) oraz polisa OC.
Dopiero status `verified` pozwala publikować usługi i przyjmować zamówienia.

Anty-fraud: wykluczenia kategorii wysokiego ryzyka bez OC, licznik fraud_flags
(3+ → automatyczne zawieszenie), okno anulowania zamówienia 30 minut.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from adam_modules.seniors.models import Senior
from .models import (
    Partner, Service, Order, ServiceCategory, PartnerStatus, OrderStatus,
)

CANCELLATION_WINDOW_MINUTES = 30
FRAUD_SUSPEND_THRESHOLD = 3

# Kategorie wymagające obowiązkowej polisy OC (wykluczenie bez OC — anty-fraud).
OC_REQUIRED_CATEGORIES = {
    ServiceCategory.medical_care,
    ServiceCategory.physiotherapy,
    ServiceCategory.transport,
    ServiceCategory.legal_admin,
}


def validate_nip(nip: str | None) -> bool:
    """Walidacja polskiego NIP (10 cyfr + suma kontrolna)."""
    if not nip or not nip.isdigit() or len(nip) != 10:
        return False
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    checksum = sum(int(d) * w for d, w in zip(nip[:9], weights)) % 11
    if checksum == 10:
        return False
    return checksum == int(nip[9])


class MarketplaceService:
    def __init__(self, session: Session):
        self.session = session

    # ---- partnerzy ----
    def register_partner(self, name: str, category: ServiceCategory,
                         nip: str | None = None, insurance_oc: bool = False) -> Partner:
        p = Partner(name=name, category=category, nip=nip, insurance_oc=insurance_oc)
        self.session.add(p)
        self.session.flush()
        return p

    def verify_partner(self, partner: Partner) -> Partner:
        """Weryfikacja: poprawny NIP + (OC gdy kategoria wymaga)."""
        if not validate_nip(partner.nip):
            partner.status = PartnerStatus.rejected
            self.session.flush()
            return partner
        if partner.category in OC_REQUIRED_CATEGORIES and not partner.insurance_oc:
            partner.status = PartnerStatus.rejected
            self.session.flush()
            return partner
        partner.status = PartnerStatus.verified
        self.session.flush()
        return partner

    def flag_fraud(self, partner: Partner) -> Partner:
        partner.fraud_flags += 1
        if partner.fraud_flags >= FRAUD_SUSPEND_THRESHOLD:
            partner.status = PartnerStatus.suspended
        self.session.flush()
        return partner

    # ---- usługi ----
    def add_service(self, partner: Partner, title: str, price_pln: float,
                    description: str | None = None) -> Service:
        if partner.status != PartnerStatus.verified:
            raise ValueError("Tylko zweryfikowany partner może publikować usługi")
        svc = Service(partner_id=partner.id, title=title, price_pln=price_pln, description=description)
        self.session.add(svc)
        self.session.flush()
        return svc

    def list_services(self, category: ServiceCategory | None = None) -> list[Service]:
        stmt = select(Service).where(Service.active.is_(True))
        if category:
            stmt = stmt.join(Partner).where(Partner.category == category,
                                            Partner.status == PartnerStatus.verified)
        return list(self.session.scalars(stmt))

    # ---- zamówienia ----
    def create_order(self, senior: Senior, service: Service, note: str | None = None,
                     now: datetime | None = None) -> Order:
        now = now or datetime.utcnow()
        partner = self.session.get(Partner, service.partner_id)
        if partner is None or partner.status != PartnerStatus.verified:
            raise ValueError("Usługa niedostępna — partner niezweryfikowany")
        order = Order(
            service_id=service.id, senior_id=senior.id, status=OrderStatus.created,
            amount_pln=service.price_pln, note=note,
            cancellable_until=now + timedelta(minutes=CANCELLATION_WINDOW_MINUTES),
        )
        self.session.add(order)
        self.session.flush()
        return order

    def can_cancel(self, order: Order, now: datetime | None = None) -> bool:
        now = now or datetime.utcnow()
        if order.status not in (OrderStatus.created, OrderStatus.confirmed):
            return False
        return order.cancellable_until is not None and now <= order.cancellable_until

    def cancel_order(self, order: Order, now: datetime | None = None) -> Order:
        if not self.can_cancel(order, now):
            raise ValueError("Poza oknem anulowania (30 min) lub zły status")
        order.status = OrderStatus.cancelled
        self.session.flush()
        return order

    def confirm_order(self, order: Order) -> Order:
        order.status = OrderStatus.confirmed
        self.session.flush()
        return order

    def complete_order(self, order: Order, now: datetime | None = None) -> Order:
        order.status = OrderStatus.completed
        order.completed_at = now or datetime.utcnow()
        self.session.flush()
        return order

    def orders_for_senior(self, senior_id: int) -> list[Order]:
        return list(self.session.scalars(
            select(Order).where(Order.senior_id == senior_id).order_by(Order.id.desc())
        ))
