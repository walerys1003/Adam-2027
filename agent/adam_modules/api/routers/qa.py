"""Router QA Loop (F16, ETAP 30) — oceny, audyt, improvement loop, nastrój, telemetria decyzji."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adam_modules.seniors import SeniorService
from adam_modules.qa import (
    QAService, Turn, AuditVerdict, ImprovementStatus, DecisionKind,
)
from ..deps import get_db

router = APIRouter(prefix="/api/qa", tags=["qa (F16)"])


# ---------- schematy ----------
class TurnIn(BaseModel):
    role: str
    text: str
    asr_confidence: float = 1.0


class EvaluateIn(BaseModel):
    turns: list[TurnIn]
    senior_id: int | None = None
    conversation_ref: str | None = None
    duration_s: float | None = None
    interruptions: int = 0
    completed: bool = True


class AuditIn(BaseModel):
    auditor: str
    verdict: AuditVerdict
    note: str | None = None
    evaluation_id: int | None = None
    senior_id: int | None = None
    conversation_ref: str | None = None
    auto_improvements: bool = True


class ImprovementIn(BaseModel):
    category: str
    title: str
    detail: str | None = None
    priority: int = 3


class SentimentIn(BaseModel):
    senior_id: int
    text: str
    semaphore_level: str | None = None
    prosody_valence: float | None = None
    conversation_ref: str | None = None


class DecisionIn(BaseModel):
    decision: DecisionKind
    senior_id: int | None = None
    conversation_ref: str | None = None
    level: str | None = None
    trigger: str | None = None
    confidence: float | None = None
    voters: list[str] | None = None
    escalated_112: bool = False
    emergency_call_id: int | None = None
    note: str | None = None


# ---------- oceny ----------
@router.post("/evaluate")
def evaluate(body: EvaluateIn, db: Session = Depends(get_db)):
    turns = [Turn(role=t.role, text=t.text, asr_confidence=t.asr_confidence) for t in body.turns]
    ev = QAService(db).evaluate_and_store(
        turns, senior_id=body.senior_id, conversation_ref=body.conversation_ref,
        duration_s=body.duration_s, interruptions=body.interruptions, completed=body.completed,
    )
    return {"id": ev.id, "score": ev.score, "needs_review": ev.needs_review,
            "flags": ev.flags, "metrics": ev.metrics}


@router.get("/pending-review")
def pending_review(limit: int = 50, db: Session = Depends(get_db)):
    rows = QAService(db).pending_review(limit=limit)
    return [{"id": r.id, "score": r.score, "conversation_ref": r.conversation_ref,
             "flags": r.flags} for r in rows]


# ---------- audyt + improvement loop ----------
@router.post("/audits")
def create_audit(body: AuditIn, db: Session = Depends(get_db)):
    svc = QAService(db)
    audit = svc.record_audit(
        auditor=body.auditor, verdict=body.verdict, note=body.note,
        evaluation_id=body.evaluation_id, senior_id=body.senior_id,
        conversation_ref=body.conversation_ref,
    )
    created = svc.improvements_from_audit(audit) if body.auto_improvements else []
    return {"id": audit.id, "verdict": audit.verdict.value,
            "improvements_created": [i.id for i in created]}


@router.post("/improvements")
def create_improvement(body: ImprovementIn, db: Session = Depends(get_db)):
    item = QAService(db).open_improvement(
        category=body.category, title=body.title, detail=body.detail, priority=body.priority,
    )
    return {"id": item.id, "status": item.status.value, "priority": item.priority}


@router.get("/improvements")
def backlog(only_open: bool = True, limit: int = 100, db: Session = Depends(get_db)):
    rows = QAService(db).improvement_backlog(only_open=only_open, limit=limit)
    return [{"id": r.id, "category": r.category, "title": r.title,
             "status": r.status.value, "priority": r.priority} for r in rows]


@router.patch("/improvements/{item_id}")
def resolve_improvement(item_id: int, status: ImprovementStatus, db: Session = Depends(get_db)):
    item = QAService(db).resolve_improvement(item_id, status=status)
    if item is None:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
    return {"id": item.id, "status": item.status.value}


# ---------- nastrój ----------
@router.post("/sentiment")
def record_sentiment(body: SentimentIn, db: Session = Depends(get_db)):
    if SeniorService(db).get(body.senior_id) is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    row = QAService(db).record_sentiment(
        senior_id=body.senior_id, text=body.text, semaphore_level=body.semaphore_level,
        prosody_valence=body.prosody_valence, conversation_ref=body.conversation_ref,
    )
    return {"id": row.id, "label": row.label.value, "score": row.score, "source": row.source}


@router.get("/sentiment/{senior_id}")
def mood_timeline(senior_id: int, limit: int = 20, db: Session = Depends(get_db)):
    svc = QAService(db)
    rows = svc.mood_timeline(senior_id, limit=limit)
    return {"average": svc.average_mood(senior_id, limit=limit),
            "readings": [{"label": r.label.value, "score": r.score,
                          "created_at": str(r.created_at)} for r in rows]}


# ---------- telemetria decyzji ----------
@router.post("/decisions")
def record_decision(body: DecisionIn, db: Session = Depends(get_db)):
    row = QAService(db).record_decision(
        decision=body.decision, senior_id=body.senior_id, conversation_ref=body.conversation_ref,
        level=body.level, trigger=body.trigger, confidence=body.confidence, voters=body.voters,
        escalated_112=body.escalated_112, emergency_call_id=body.emergency_call_id, note=body.note,
    )
    return {"id": row.id, "decision": row.decision.value, "escalated_112": row.escalated_112}


@router.get("/decisions")
def decisions(senior_id: int | None = None, limit: int = 100, db: Session = Depends(get_db)):
    rows = QAService(db).decisions(senior_id=senior_id, limit=limit)
    return [{"id": r.id, "decision": r.decision.value, "level": r.level,
             "trigger": r.trigger, "escalated_112": r.escalated_112,
             "created_at": str(r.created_at)} for r in rows]


@router.get("/stats/escalations")
def escalation_stats(db: Session = Depends(get_db)):
    return QAService(db).escalation_stats()
