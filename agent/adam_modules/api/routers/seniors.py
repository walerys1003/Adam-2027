"""Router seniorów (F1) — CRUD profili + lista/paginacja.

Wszystkie odpowiedzi maskują PII (PESEL/telefon) przez SeniorOut.from_model.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate, SeniorUpdate, SeniorOut
from ..deps import get_db

router = APIRouter(prefix="/api/seniors", tags=["seniors (F1)"])


class SeniorListOut(BaseModel):
    items: list[SeniorOut]
    total: int
    limit: int
    offset: int


@router.get("", response_model=SeniorListOut)
def list_seniors(
    active: bool | None = Query(default=None),
    district: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    svc = SeniorService(db)
    rows = svc.list(active=active, district=district, limit=limit, offset=offset)
    return SeniorListOut(
        items=[SeniorOut.from_model(s) for s in rows],
        total=svc.count(active=active),
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=SeniorOut, status_code=status.HTTP_201_CREATED)
def create_senior(data: SeniorCreate, db: Session = Depends(get_db)):
    svc = SeniorService(db)
    senior = svc.create(data)
    db.flush()
    return SeniorOut.from_model(senior)


@router.get("/{senior_id}", response_model=SeniorOut)
def get_senior(senior_id: int, db: Session = Depends(get_db)):
    senior = SeniorService(db).get(senior_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    return SeniorOut.from_model(senior)


@router.get("/by-external/{external_id}", response_model=SeniorOut)
def get_senior_by_external(external_id: str, db: Session = Depends(get_db)):
    senior = SeniorService(db).get_by_external(external_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    return SeniorOut.from_model(senior)


@router.patch("/{senior_id}", response_model=SeniorOut)
def update_senior(senior_id: int, data: SeniorUpdate, db: Session = Depends(get_db)):
    senior = SeniorService(db).update(senior_id, data)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    return SeniorOut.from_model(senior)


@router.delete("/{senior_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_senior(senior_id: int, db: Session = Depends(get_db)):
    ok = SeniorService(db).deactivate(senior_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    return None
