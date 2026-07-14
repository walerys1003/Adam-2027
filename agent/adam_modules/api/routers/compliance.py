"""Router compliance (F13/F15/F16/F17) — AI Act, QA, consensus, payload 112.

Łączy funkcje bezstanowe (QA/consensus/emergency wyliczają wynik ad-hoc) oraz
compliance F13 zapisujący log ujawnień AI.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from adam_modules.seniors import SeniorService
from adam_modules.compliance import ComplianceService, DisclosureChannel
from adam_modules.qa import QAEvaluator, Turn
from adam_modules.consensus import ConsensusEngine, ModelVote
from adam_modules.emergency import EmergencyService
from adam_modules.speech import build_speech_profile, HearingLevel, CognitivePace
from ..deps import get_db

router = APIRouter(prefix="/api/compliance", tags=["compliance (F13/F15/F16/F17)"])


# ---- F13 AI Act ----
@router.get("/system-register")
def system_register():
    return ComplianceService.system_register()


class DisclosureIn(BaseModel):
    senior_id: int
    conversation_ref: str
    channel: DisclosureChannel = DisclosureChannel.voice
    disclosed: bool = True
    disclosure_text: str | None = None


@router.post("/disclosures")
def record_disclosure(data: DisclosureIn, db: Session = Depends(get_db)):
    senior = SeniorService(db).get(data.senior_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    log = ComplianceService(db).record_disclosure(
        senior, data.conversation_ref, channel=data.channel,
        disclosed=data.disclosed, disclosure_text=data.disclosure_text,
    )
    db.flush()
    return {"id": log.id, "conversation_ref": log.conversation_ref,
            "disclosed": log.disclosed, "channel": log.channel.value}


@router.get("/disclosures/{conversation_ref}/asserted")
def assert_disclosed(conversation_ref: str, db: Session = Depends(get_db)):
    return {"conversation_ref": conversation_ref,
            "disclosed": ComplianceService(db).assert_disclosed(conversation_ref)}


# ---- F15 QA ----
class TurnIn(BaseModel):
    role: str
    text: str
    asr_confidence: float = 1.0


class QAIn(BaseModel):
    turns: list[TurnIn]
    duration_s: float = 60.0
    interruptions: int = 0
    completed: bool = True


@router.post("/qa/evaluate")
def qa_evaluate(data: QAIn):
    turns = [Turn(role=t.role, text=t.text, asr_confidence=t.asr_confidence) for t in data.turns]
    evaluator = QAEvaluator()
    result = evaluator.evaluate(
        turns, duration_s=data.duration_s,
        interruptions=data.interruptions, completed=data.completed,
    )
    return {
        "score": result.score,
        "flags": result.flags,
        "metrics": result.metrics,
        "needs_human_review": evaluator.needs_human_review(result),
    }


# ---- F16 consensus ----
class VoteIn(BaseModel):
    source: str
    level: str
    trigger: str
    confidence: float = 1.0


class ConsensusIn(BaseModel):
    votes: list[VoteIn]


@router.post("/consensus/decide")
def consensus_decide(data: ConsensusIn):
    from adam_modules.seniors.models import SemaphoreLevel
    from adam_modules.semaphore.models import Trigger
    votes = [
        ModelVote(source=v.source, level=SemaphoreLevel(v.level),
                  trigger=Trigger(v.trigger), confidence=v.confidence)
        for v in data.votes
    ]
    result = ConsensusEngine().decide(votes)
    return {
        "level": result.level.value,
        "trigger": result.trigger.value,
        "confidence": result.confidence,
        "agreement": result.agreement,
        "needs_review": result.needs_review,
        "notes": result.notes,
    }


# ---- F17 emergency 112 ----
@router.post("/emergency/{senior_id}/payload")
def emergency_payload(senior_id: int, reason: str, db: Session = Depends(get_db)):
    senior = SeniorService(db).get(senior_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    payload = EmergencyService(db).build_payload(senior, reason=reason)
    return {"payload": payload.to_dict(), "dispatch_summary": payload.dispatch_summary()}


# ---- F14 speech profile ----
class SpeechIn(BaseModel):
    hearing: HearingLevel = HearingLevel.normal
    pace: CognitivePace = CognitivePace.normal
    age: int = Field(default=75, ge=0, le=130)


@router.post("/speech/profile")
def speech_profile(data: SpeechIn):
    profile = build_speech_profile(data.hearing, data.pace, data.age)
    return profile.to_dict()
