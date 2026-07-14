"""Router marketplace (F11) — katalog usług + zamówienia z oknem anulowania."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adam_modules.seniors import SeniorService
from adam_modules.marketplace import (
    MarketplaceService, ServiceCategory,
)
from ..deps import get_db

router = APIRouter(prefix="/api/marketplace", tags=["marketplace (F11)"])


class ServiceOut(BaseModel):
    id: int
    partner_id: int
    title: str
    price_pln: float
    description: str | None = None


class OrderOut(BaseModel):
    id: int
    service_id: int
    senior_id: int
    status: str
    amount_pln: float
    note: str | None = None
    cancellable_until: datetime | None = None
    can_cancel: bool


class OrderIn(BaseModel):
    senior_id: int
    service_id: int
    note: str | None = None


def _order_out(svc: MarketplaceService, o) -> OrderOut:
    return OrderOut(
        id=o.id, service_id=o.service_id, senior_id=o.senior_id, status=o.status.value,
        amount_pln=o.amount_pln, note=o.note, cancellable_until=o.cancellable_until,
        can_cancel=svc.can_cancel(o),
    )


@router.get("/services", response_model=list[ServiceOut])
def list_services(
    category: ServiceCategory | None = Query(default=None),
    db: Session = Depends(get_db),
):
    rows = MarketplaceService(db).list_services(category=category)
    return [ServiceOut(id=s.id, partner_id=s.partner_id, title=s.title,
                       price_pln=s.price_pln, description=s.description) for s in rows]


@router.post("/orders", response_model=OrderOut, status_code=201)
def create_order(data: OrderIn, db: Session = Depends(get_db)):
    senior = SeniorService(db).get(data.senior_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    svc = MarketplaceService(db)
    from adam_modules.marketplace.models import Service
    service = db.get(Service, data.service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Usługa nie znaleziona")
    order = svc.create_order(senior, service, note=data.note)  # ValueError → 422
    db.flush()
    return _order_out(svc, order)


@router.get("/seniors/{senior_id}/orders", response_model=list[OrderOut])
def orders_for_senior(senior_id: int, db: Session = Depends(get_db)):
    if SeniorService(db).get(senior_id) is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    svc = MarketplaceService(db)
    return [_order_out(svc, o) for o in svc.orders_for_senior(senior_id)]


@router.post("/orders/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    svc = MarketplaceService(db)
    from adam_modules.marketplace.models import Order
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Zamówienie nie znalezione")
    svc.cancel_order(order)  # ValueError (poza oknem) → 422
    db.flush()
    return _order_out(svc, order)
