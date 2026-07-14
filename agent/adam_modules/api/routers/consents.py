"""Router Consents (F12, ETAP 25) — zgody RODO/AI Act + bramka zgód (consent gate)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adam_modules.seniors import SeniorService
from adam_modules.rodo import ConsentService, ConsentType
from ..deps import get_db

router = APIRouter(prefix="/api/seniors/{senior_id}/consents", tags=["consents (F12)"])


def _senior_or_404(db: Session, senior_id: int):
    senior = SeniorService(db).get(senior_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    return senior


class ConsentIn(BaseModel):
    consent_type: ConsentType
    source: str | None = None
    actor: str | None = None
    note: str | None = None


class ConsentOut(BaseModel):
    id: int
    consent_type: str
    status: str
    source: str | None = None
    actor: str | None = None


class GateOut(BaseModel):
    allowed: bool
    missing: list[str]


@router.get("")
def snapshot(senior_id: int, db: Session = Depends(get_db)):
    """Aktualny stan wszystkich typów zgód (typ → status/'none')."""
    _senior_or_404(db, senior_id)
    return ConsentService(db).snapshot(senior_id)


@router.get("/history", response_model=list[ConsentOut])
def history(senior_id: int, limit: int = 100, db: Session = Depends(get_db)):
    _senior_or_404(db, senior_id)
    rows = ConsentService(db).history(senior_id, limit=limit)
    return [
        ConsentOut(id=r.id, consent_type=r.consent_type.value, status=r.status.value,
                   source=r.source, actor=r.actor)
        for r in rows
    ]


@router.post("/grant", response_model=ConsentOut)
def grant(senior_id: int, body: ConsentIn, db: Session = Depends(get_db)):
    _senior_or_404(db, senior_id)
    c = ConsentService(db).grant(senior_id, body.consent_type,
                                 source=body.source, actor=body.actor, note=body.note)
    db.flush()
    return ConsentOut(id=c.id, consent_type=c.consent_type.value, status=c.status.value,
                      source=c.source, actor=c.actor)


@router.post("/withdraw", response_model=ConsentOut)
def withdraw(senior_id: int, body: ConsentIn, db: Session = Depends(get_db)):
    _senior_or_404(db, senior_id)
    c = ConsentService(db).withdraw(senior_id, body.consent_type,
                                    actor=body.actor, note=body.note)
    db.flush()
    return ConsentOut(id=c.id, consent_type=c.consent_type.value, status=c.status.value,
                      source=c.source, actor=c.actor)


@router.get("/gate", response_model=GateOut)
def gate(senior_id: int, db: Session = Depends(get_db)):
    """Bramka zgód: czy można rozpocząć rozmowę (aktywne zgody obowiązkowe)?"""
    _senior_or_404(db, senior_id)
    svc = ConsentService(db)
    result = svc.check_call_gate(senior_id)
    svc.log_gate_check(senior_id, result)
    db.flush()
    return GateOut(allowed=result.allowed, missing=result.missing_values)
