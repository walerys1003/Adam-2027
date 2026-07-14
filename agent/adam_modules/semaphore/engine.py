"""
SemaphoreEngine (F3.1) — klasyfikacja poziomu semafora.

Mapuje wyzwalacze (Trigger) na poziom (SemaphoreLevel), stosuje state machine
(poziom nigdy nie „spada" automatycznie z RED/PURPLE bez rozwiązania) i zapisuje
SemaphoreEvent. Poziom wynikowy = maksimum z bieżących sygnałów, z uwzględnieniem
niezamkniętego stanu krytycznego.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from adam_modules.seniors.models import Senior, SemaphoreLevel
from .models import SemaphoreEvent, Trigger

# Mapowanie: trigger → poziom semafora
TRIGGER_LEVEL: dict[Trigger, SemaphoreLevel] = {
    Trigger.routine_ok: SemaphoreLevel.green,
    # żółty
    Trigger.mood_low: SemaphoreLevel.yellow,
    Trigger.missed_medication: SemaphoreLevel.yellow,
    Trigger.poor_sleep: SemaphoreLevel.yellow,
    Trigger.social_isolation: SemaphoreLevel.yellow,
    Trigger.minor_complaint: SemaphoreLevel.yellow,
    # czerwony
    Trigger.no_answer_exhausted: SemaphoreLevel.red,
    Trigger.vitals_out_of_range: SemaphoreLevel.red,
    Trigger.persistent_pain: SemaphoreLevel.red,
    Trigger.confusion: SemaphoreLevel.red,
    Trigger.fall_reported: SemaphoreLevel.red,
    # fioletowy — kryzys
    Trigger.chest_pain: SemaphoreLevel.purple,
    Trigger.breathing_difficulty: SemaphoreLevel.purple,
    Trigger.stroke_symptoms: SemaphoreLevel.purple,
    Trigger.suicide_ideation: SemaphoreLevel.purple,
    Trigger.unconscious: SemaphoreLevel.purple,
    Trigger.severe_bleeding: SemaphoreLevel.purple,
}

_ORDER = {
    SemaphoreLevel.green: 0,
    SemaphoreLevel.yellow: 1,
    SemaphoreLevel.red: 2,
    SemaphoreLevel.purple: 3,
}


def level_rank(level: SemaphoreLevel) -> int:
    return _ORDER[level]


def max_level(a: SemaphoreLevel, b: SemaphoreLevel) -> SemaphoreLevel:
    return a if _ORDER[a] >= _ORDER[b] else b


@dataclass
class Classification:
    level: SemaphoreLevel
    trigger: Trigger
    confidence: float = 1.0
    signals: dict = field(default_factory=dict)
    note: str | None = None


class SemaphoreEngine:
    def __init__(self, session: Session):
        self.session = session

    def classify(self, triggers: list[Trigger]) -> Classification:
        """Zwraca klasyfikację o najwyższym poziomie z listy wyzwalaczy."""
        if not triggers:
            return Classification(level=SemaphoreLevel.green, trigger=Trigger.routine_ok)
        # wybierz trigger o najwyższym poziomie
        top = max(triggers, key=lambda t: _ORDER[TRIGGER_LEVEL[t]])
        return Classification(level=TRIGGER_LEVEL[top], trigger=top)

    def current_level(self, senior: Senior) -> SemaphoreLevel:
        return senior.semaphore

    def apply(self, senior: Senior, classification: Classification,
              *, allow_downgrade: bool = False) -> SemaphoreEvent:
        """
        Stosuje klasyfikację: aktualizuje poziom seniora i zapisuje zdarzenie.
        State machine: bez allow_downgrade poziom może tylko rosnąć lub trwać
        (RED/PURPLE nie „gasną" samoczynnie — wymaga jawnego rozwiązania).
        """
        previous = senior.semaphore
        if allow_downgrade:
            new = classification.level
        else:
            new = max_level(previous, classification.level)

        event = SemaphoreEvent(
            senior_id=senior.id,
            previous_level=previous,
            new_level=new,
            trigger=classification.trigger,
            confidence=classification.confidence,
            signals=json.dumps(classification.signals, ensure_ascii=False) if classification.signals else None,
            note=classification.note,
        )
        senior.semaphore = new
        self.session.add(event)
        self.session.flush()
        return event

    def resolve(self, senior: Senior, note: str | None = None) -> SemaphoreEvent:
        """Jawne rozwiązanie stanu — sprowadza semafor do zielonego (allow_downgrade)."""
        return self.apply(
            senior,
            Classification(level=SemaphoreLevel.green, trigger=Trigger.routine_ok, note=note),
            allow_downgrade=True,
        )

    def history(self, senior_id: int, limit: int = 50) -> list[SemaphoreEvent]:
        return list(self.session.scalars(
            select(SemaphoreEvent).where(SemaphoreEvent.senior_id == senior_id)
            .order_by(SemaphoreEvent.id.desc()).limit(limit)
        ))
