"""
Model SemaphoreEvent (F3) — dziennik zdarzeń semafora.

Każda klasyfikacja rozmowy/pomiaru zapisuje zdarzenie: poprzedni→nowy poziom,
wyzwalacz, ocena pewności i surowe sygnały. Stanowi audyt decyzji semafora
(wymóg AI Act — F13) i wejście do eskalacji (F3.2).
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from adam_modules.common.db import Base
from adam_modules.seniors.models import SemaphoreLevel


class Trigger(str, enum.Enum):
    """Wyzwalacze zmiany poziomu semafora."""
    # zielony / rutyna
    routine_ok = "routine_ok"
    # żółty — obserwacja
    mood_low = "mood_low"
    missed_medication = "missed_medication"
    poor_sleep = "poor_sleep"
    social_isolation = "social_isolation"
    minor_complaint = "minor_complaint"
    # czerwony — pilne
    no_answer_exhausted = "no_answer_exhausted"
    vitals_out_of_range = "vitals_out_of_range"
    persistent_pain = "persistent_pain"
    confusion = "confusion"
    fall_reported = "fall_reported"
    # fioletowy — kryzys (bypass DND, →112)
    chest_pain = "chest_pain"
    breathing_difficulty = "breathing_difficulty"
    stroke_symptoms = "stroke_symptoms"
    suicide_ideation = "suicide_ideation"
    unconscious = "unconscious"
    severe_bleeding = "severe_bleeding"


class SemaphoreEvent(Base):
    __tablename__ = "semaphore_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)

    previous_level: Mapped[SemaphoreLevel] = mapped_column(Enum(SemaphoreLevel))
    new_level: Mapped[SemaphoreLevel] = mapped_column(Enum(SemaphoreLevel), index=True)
    trigger: Mapped[Trigger] = mapped_column(Enum(Trigger), index=True)

    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    signals: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON surowych sygnałów
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SemaphoreEvent s{self.senior_id} {self.previous_level.value}→{self.new_level.value} {self.trigger.value}>"
