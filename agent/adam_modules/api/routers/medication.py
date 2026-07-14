"""Router leków (F6) — lista/dodawanie leków + raport adherence."""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from adam_modules.seniors import SeniorService
from adam_modules.medication import (
    MedicationService, MedicationCreate, MedicationOut, AdherenceReport,
)
from ..deps import get_db

router = APIRouter(prefix="/api/seniors/{senior_id}/medications", tags=["medications (F6)"])


def _senior_or_404(db: Session, senior_id: int):
    senior = SeniorService(db).get(senior_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    return senior


@router.get("", response_model=list[MedicationOut])
def list_medications(
    senior_id: int,
    only_active: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    _senior_or_404(db, senior_id)
    meds = MedicationService(db).list_for_senior(senior_id, only_active=only_active)
    return [MedicationOut.model_validate(m, from_attributes=True) for m in meds]


@router.post("", response_model=MedicationOut, status_code=201)
def create_medication(senior_id: int, data: MedicationCreate, db: Session = Depends(get_db)):
    senior = _senior_or_404(db, senior_id)
    med = MedicationService(db).create(senior, data)
    db.flush()
    return MedicationOut.model_validate(med, from_attributes=True)


@router.get("/adherence", response_model=AdherenceReport)
def adherence(
    senior_id: int,
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    _senior_or_404(db, senior_id)
    since = datetime.utcnow() - timedelta(days=days)
    until = datetime.utcnow() + timedelta(days=1)
    return MedicationService(db).adherence(senior_id, since=since, until=until)
