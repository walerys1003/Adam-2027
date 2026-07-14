"""Router RODO (F12) — eksport danych (art.15/20), soft-delete, erase (art.17), audyt."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adam_modules.seniors import SeniorService
from adam_modules.rodo import RodoService
from ..deps import get_db

router = APIRouter(prefix="/api/seniors/{senior_id}/rodo", tags=["rodo (F12)"])


def _senior_or_404(db: Session, senior_id: int):
    senior = SeniorService(db).get(senior_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    return senior


class AuditItemOut(BaseModel):
    id: int
    action: str
    detail: str | None = None
    legal_basis: str | None = None


@router.get("/export")
def export_data(senior_id: int, actor: str | None = Query(default=None), db: Session = Depends(get_db)):
    """Zwraca komplet danych seniora (prawo dostępu/przenoszalności)."""
    senior = _senior_or_404(db, senior_id)
    data = RodoService(db).export_data(senior, actor=actor)
    db.flush()
    return data


@router.post("/soft-delete")
def soft_delete(senior_id: int, actor: str | None = Query(default=None), db: Session = Depends(get_db)):
    senior = _senior_or_404(db, senior_id)
    RodoService(db).soft_delete(senior, actor=actor)
    db.flush()
    return {"senior_id": senior_id, "active": senior.active}


@router.post("/erase")
def erase(senior_id: int, actor: str | None = Query(default=None), db: Session = Depends(get_db)):
    """Prawo do zapomnienia (art.17): usuwa dane powiązane + anonimizuje profil."""
    senior = _senior_or_404(db, senior_id)
    counts = RodoService(db).erase_senior(senior, actor=actor)
    db.flush()
    return {"senior_id": senior_id, "erased": counts}


@router.get("/audit", response_model=list[AuditItemOut])
def audit(senior_id: int, limit: int = 100, db: Session = Depends(get_db)):
    _senior_or_404(db, senior_id)
    rows = RodoService(db).audit_trail(senior_id, limit=limit)
    return [
        AuditItemOut(
            id=r.id, action=r.action.value,
            detail=getattr(r, "detail", None),
            legal_basis=getattr(r, "legal_basis", None),
        )
        for r in rows
    ]
