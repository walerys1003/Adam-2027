"""
Modele F13 — AI Act compliance.

DisclosureLog — dowód, że w danej rozmowie Adam ujawnił swoją naturę AI
(art. 50 AI Act — obowiązek transparentności). Każda rozmowa musi mieć wpis.
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from adam_modules.common.db import Base


class DisclosureChannel(str, enum.Enum):
    voice = "voice"      # wypowiedziane w rozmowie telefonicznej
    sms = "sms"
    app = "app"


class DisclosureLog(Base):
    __tablename__ = "disclosure_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)
    conversation_ref: Mapped[str] = mapped_column(String(120), index=True)

    channel: Mapped[DisclosureChannel] = mapped_column(Enum(DisclosureChannel), default=DisclosureChannel.voice)
    disclosed: Mapped[bool] = mapped_column(Boolean, default=False)
    disclosure_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DisclosureLog s{self.senior_id} {self.conversation_ref} disclosed={self.disclosed}>"
