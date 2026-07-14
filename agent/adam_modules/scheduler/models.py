"""
Modele F2 — Scheduler welfare-check.

Campaign     — cykliczna kampania telefoniczna (np. „poranny welfare-check").
CallAttempt  — pojedyncza próba połączenia w ramach kampanii, z logiką retry.
"""
from __future__ import annotations

import enum
from datetime import datetime, time

from sqlalchemy import String, Integer, Boolean, DateTime, Time, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adam_modules.common.db import Base


class CampaignKind(str, enum.Enum):
    morning = "morning"          # poranny welfare-check
    evening = "evening"          # wieczorny welfare-check
    medication = "medication"    # przypomnienie o lekach
    custom = "custom"


class CallStatus(str, enum.Enum):
    pending = "pending"          # zaplanowana
    dialing = "dialing"          # w trakcie originate
    answered = "answered"        # odebrano
    no_answer = "no_answer"      # brak odpowiedzi (→ retry)
    failed = "failed"            # błąd techniczny (→ retry)
    exhausted = "exhausted"      # wyczerpano retry (→ eskalacja semafora)
    completed = "completed"      # rozmowa zakończona sukcesem


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[CampaignKind] = mapped_column(Enum(CampaignKind), default=CampaignKind.morning)
    scheduled_time: Mapped[time] = mapped_column(Time)  # pora dnia (HH:MM)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    retry_interval_s: Mapped[int] = mapped_column(Integer, default=20)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    attempts: Mapped[list["CallAttempt"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Campaign {self.name} {self.kind.value} @{self.scheduled_time}>"


class CallAttempt(Base):
    __tablename__ = "call_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)

    attempt_no: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[CallStatus] = mapped_column(
        Enum(CallStatus), default=CallStatus.pending, index=True
    )
    channel_id: Mapped[str | None] = mapped_column(String(64), nullable=True)  # ARI channel

    scheduled_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    campaign: Mapped["Campaign"] = relationship(back_populates="attempts")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CallAttempt s{self.senior_id} #{self.attempt_no} {self.status.value}>"
