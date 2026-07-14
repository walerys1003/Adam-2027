"""Router bezpieczeństwa (F3/F4/F8) — detekcja kryzysu, semafor, eskalacja.

Przepływ: /analyze wykrywa sygnały (tekst+vitals) → klasyfikacja przez
Guardrails → opcjonalnie zastosowanie na seniorze (zmiana poziomu semafora)
→ plan eskalacji.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from adam_modules.seniors import SeniorService
from adam_modules.seniors.models import SemaphoreLevel
from adam_modules.semaphore import (
    CrisisDetector, SemaphoreEngine, Guardrails, EscalationLadder,
)
from ..deps import get_db

router = APIRouter(prefix="/api/safety", tags=["safety (F3/F4/F8)"])

_detector = CrisisDetector()


# ---- schematy ----
class AnalyzeIn(BaseModel):
    text: str = ""
    vitals: dict[str, float] = Field(default_factory=dict)
    apply_to_senior_id: int | None = None


class DetectionOut(BaseModel):
    trigger: str
    level: str
    confidence: float
    evidence: list[str]


class EscalationStepOut(BaseModel):
    order: int
    action: str
    at_offset_s: int
    bypass_dnd: bool
    description: str = ""


class AnalyzeOut(BaseModel):
    level: str
    trigger: str
    confidence: float
    valid: bool
    needs_confirmation: bool = False
    guardrail_errors: list[str] = Field(default_factory=list)
    detections: list[DetectionOut]
    escalation: list[EscalationStepOut]
    applied: bool = False
    previous_level: str | None = None


def _escalation_out(level: SemaphoreLevel) -> list[EscalationStepOut]:
    return [
        EscalationStepOut(
            order=s.order,
            action=s.action,
            at_offset_s=s.at_offset_s,
            bypass_dnd=s.bypass_dnd,
            description=s.description,
        )
        for s in EscalationLadder.plan(level)
    ]


@router.post("/analyze", response_model=AnalyzeOut)
def analyze(data: AnalyzeIn, db: Session = Depends(get_db)):
    detections = _detector.detect(text=data.text, vitals=data.vitals or None)
    classification = _detector.to_classification(detections)
    guard = Guardrails.validate(classification)

    applied = False
    previous_level: str | None = None
    if data.apply_to_senior_id is not None:
        senior = SeniorService(db).get(data.apply_to_senior_id)
        if senior is None:
            raise HTTPException(status_code=404, detail="Senior nie znaleziony")
        previous_level = senior.semaphore.value
        SemaphoreEngine(db).apply(senior, classification)
        db.flush()
        applied = True

    return AnalyzeOut(
        level=classification.level.value,
        trigger=classification.trigger.value,
        confidence=classification.confidence,
        valid=guard.ok,
        needs_confirmation=guard.needs_confirmation,
        guardrail_errors=guard.errors,
        detections=[
            DetectionOut(
                trigger=d.trigger.value, level=d.level.value,
                confidence=d.confidence, evidence=d.evidence,
            ) for d in detections
        ],
        escalation=_escalation_out(classification.level),
        applied=applied,
        previous_level=previous_level,
    )


class ResolveIn(BaseModel):
    note: str | None = None


@router.post("/seniors/{senior_id}/resolve", response_model=AnalyzeOut)
def resolve(senior_id: int, data: ResolveIn, db: Session = Depends(get_db)):
    senior = SeniorService(db).get(senior_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    previous = senior.semaphore.value
    SemaphoreEngine(db).resolve(senior, note=data.note)
    db.flush()
    return AnalyzeOut(
        level=senior.semaphore.value,
        trigger="routine_ok",
        confidence=1.0,
        valid=True,
        needs_confirmation=False,
        guardrail_errors=[],
        detections=[],
        escalation=[],
        applied=True,
        previous_level=previous,
    )


class HistoryItemOut(BaseModel):
    id: int
    previous_level: str
    new_level: str
    trigger: str
    confidence: float
    note: str | None = None


@router.get("/seniors/{senior_id}/history", response_model=list[HistoryItemOut])
def history(senior_id: int, limit: int = 50, db: Session = Depends(get_db)):
    events = SemaphoreEngine(db).history(senior_id, limit=limit)
    return [
        HistoryItemOut(
            id=e.id,
            previous_level=e.previous_level.value,
            new_level=e.new_level.value,
            trigger=e.trigger.value,
            confidence=e.confidence,
            note=e.note,
        ) for e in events
    ]
