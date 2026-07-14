"""Modele F15 (ETAP 26) — rejestr zgłoszeń ratunkowych 112.

EmergencyCall — trwały ślad każdej próby wezwania służb: kiedy, dlaczego,
z jakim payloadem, jaki był wynik (dodzwoniono/nie/symulacja dev). Rejestr jest
dowodem rozliczalności (RODO art. 6 ust.1 lit. d — ochrona żywotnych interesów)
i materiałem do audytu jakości (F16).
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from adam_modules.common.db import Base


class EmergencyStatus(str, enum.Enum):
    initiated = "initiated"       # zgłoszenie utworzone
    dispatched = "dispatched"     # przekazane do kanału (originate wysłany)
    connected = "connected"       # dyspozytor odebrał
    failed = "failed"             # nie udało się połączyć
    simulated = "simulated"       # tryb dev — brak realnej telefonii


class EmergencyCall(Base):
    __tablename__ = "emergency_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)
    reason: Mapped[str] = mapped_column(String(200))
    semaphore_level: Mapped[str] = mapped_column(String(16))
    status: Mapped[EmergencyStatus] = mapped_column(
        Enum(EmergencyStatus), default=EmergencyStatus.initiated, index=True
    )
    channel_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_script: Mapped[str | None] = mapped_column(Text, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<EmergencyCall s{self.senior_id} {self.status.value}>"
