"""Router warstwy głosowej `/api/voice` (ETAP 12.4).

Endpoint deweloperski/integracyjny: symuluje pełne połączenie tura-po-turze
(FakeChannel + RuleLLM), zwracając transkrypcję i wynik (poziom semafora,
eskalacja). Pozwala panelowi/testom przejść tor rozmowy bez telefonii.

Produkcyjnie (Frankfurt DC) start realnego połączenia inicjuje Asterisk (Stasis
ARI) — ten sam DialogEngine/CallSession, tylko z `AriChannel` zamiast Fake.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from adam_modules.seniors.service import SeniorService
from adam_modules.speech.profile import HearingLevel, CognitivePace
from adam_modules.voice import (
    DialogEngine, RuleLLM, FakeChannel, CallSession,
)
from adam_modules.voice.stasis import CallStartRequest, originate_call
from ..deps import get_db

router = APIRouter(prefix="/api/voice", tags=["voice"])


class SimulateIn(BaseModel):
    senior_external_id: str = Field(min_length=1)
    # kolejne wypowiedzi seniora (ASR w dev = tekst wprost)
    utterances: list[str] = Field(default_factory=list)
    hearing: HearingLevel = HearingLevel.mild_loss
    pace: CognitivePace = CognitivePace.normal


class TurnOut(BaseModel):
    speaker: str
    text: str
    level: str
    trigger: str | None = None


class SimulateOut(BaseModel):
    senior_external_id: str
    disclosure_said: bool
    escalated: bool
    max_level: str
    top_trigger: str | None
    rate_wpm: int
    volume_db: float
    turns: list[TurnOut]


@router.post("/simulate-call", response_model=SimulateOut)
def simulate_call(body: SimulateIn, db: Session = Depends(get_db)):
    svc = SeniorService(db)
    senior = svc.get_by_external(body.senior_external_id)
    if not senior:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony.")

    engine = DialogEngine(
        RuleLLM(),
        senior_name=senior.first_name,
        senior_age=senior.age,
        senior_external_id=senior.external_id,
        hearing=body.hearing,
        pace=body.pace,
    )
    channel = FakeChannel(script=list(body.utterances))
    outcome = CallSession(channel, engine).run()

    return SimulateOut(
        senior_external_id=body.senior_external_id,
        disclosure_said=outcome.disclosure_said,
        escalated=outcome.escalated,
        max_level=outcome.max_level.value,
        top_trigger=outcome.top_trigger,
        rate_wpm=engine.rate_wpm,
        volume_db=engine.volume_db,
        turns=[
            TurnOut(speaker=t.speaker.value, text=t.text,
                    level=t.level.value, trigger=t.trigger)
            for t in outcome.turns
        ],
    )


# ---- webhook startu połączenia (ETAP 19) ----

class CallStartIn(BaseModel):
    senior_external_id: str = Field(min_length=1)
    reason: str = "welfare_check"


class CallStartOut(BaseModel):
    accepted: bool
    channel_id: str | None = None
    detail: str = ""
    senior_external_id: str


@router.post("/call-start", response_model=CallStartOut)
def call_start(body: CallStartIn, db: Session = Depends(get_db)):
    """Inicjuje realne połączenie wychodzące do seniora (originate przez Asterisk).

    Bez skonfigurowanego originatora ARI (środowisko sandbox/dev) zwraca
    `accepted=false` z detalem — fail-safe, bez wyjątku. W produkcji originator
    (POST /channels do Asteriska) jest wstrzykiwany na poziomie procesu Stasis.
    """
    svc = SeniorService(db)
    senior = svc.get_by_external(body.senior_external_id)
    if not senior:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony.")

    req = CallStartRequest(
        senior_external_id=senior.external_id,
        senior_name=senior.first_name,
        senior_age=senior.age,
        reason=body.reason,
    )
    result = originate_call(req)  # originator=None w dev → accepted=False
    return CallStartOut(
        accepted=result.accepted,
        channel_id=result.channel_id,
        detail=result.detail,
        senior_external_id=senior.external_id,
    )
