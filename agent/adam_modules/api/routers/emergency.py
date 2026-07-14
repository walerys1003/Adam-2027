"""Router Emergency 112 (F15, ETAP 26) — wezwanie służb, rejestr zgłoszeń, dialplan."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adam_modules.seniors import SeniorService
from adam_modules.emergency import (
    EmergencyService, build_emergency_audio, render_emergency_dialplan,
)
from ..deps import get_db

router = APIRouter(prefix="/api/seniors/{senior_id}/emergency", tags=["emergency (F15)"])


def _senior_or_404(db: Session, senior_id: int):
    senior = SeniorService(db).get(senior_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    return senior


class DispatchIn(BaseModel):
    reason: str = "kryzys — zagrożenie życia (PURPLE)"


class EmergencyCallOut(BaseModel):
    id: int
    reason: str
    status: str
    semaphore_level: str
    detail: str | None = None


@router.post("/dispatch", response_model=EmergencyCallOut)
def dispatch(senior_id: int, body: DispatchIn, db: Session = Depends(get_db)):
    """Uruchamia pełny łańcuch wezwania 112 (payload → audio → originate → rejestr).

    W dev/sandbox status = 'simulated' (fail-safe, bez realnej telefonii).
    """
    senior = _senior_or_404(db, senior_id)
    call = EmergencyService(db).dispatch(senior, body.reason)  # originator=None → dev
    db.flush()
    return EmergencyCallOut(
        id=call.id, reason=call.reason, status=call.status.value,
        semaphore_level=call.semaphore_level, detail=call.detail,
    )


@router.get("/payload")
def payload(senior_id: int, reason: str = "welfare", db: Session = Depends(get_db)):
    """Podgląd payloadu 112 + skryptu głosowego (bez wykonywania połączenia)."""
    senior = _senior_or_404(db, senior_id)
    p = EmergencyService(db).build_payload(senior, reason)
    script = build_emergency_audio(p)
    return {
        "payload": p.to_dict(),
        "dispatch_summary": p.dispatch_summary(),
        "audio_script": script.full_text(),
        "audio_segments": script.segments,
    }


@router.get("/history", response_model=list[EmergencyCallOut])
def history(senior_id: int, limit: int = 50, db: Session = Depends(get_db)):
    _senior_or_404(db, senior_id)
    rows = EmergencyService(db).history(senior_id, limit=limit)
    return [
        EmergencyCallOut(id=r.id, reason=r.reason, status=r.status.value,
                         semaphore_level=r.semaphore_level, detail=r.detail)
        for r in rows
    ]


@router.get("/dialplan")
def dialplan(senior_id: int, db: Session = Depends(get_db)):
    """Zwraca fragment dialplanu Asterisk (extensions.conf) dla wezwania 112."""
    _senior_or_404(db, senior_id)
    return {"dialplan": render_emergency_dialplan()}
