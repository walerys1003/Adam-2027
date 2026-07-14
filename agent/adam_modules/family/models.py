"""
Modele F9 — Dashboard rodzinny + notyfikacje.

FamilyMember       — opiekun/członek rodziny powiązany z seniorem (kanały kontaktu).
Notification       — powiadomienie wygenerowane przez zdarzenie semafora.
NotificationPolicy — reguła: jak dostarczać wg poziomu (digest/immediate/bypass-DND).
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adam_modules.common.db import Base
from adam_modules.seniors.models import SemaphoreLevel


class FamilyRole(str, enum.Enum):
    primary = "primary"          # główny opiekun (dostaje wszystko)
    secondary = "secondary"      # dodatkowy opiekun
    coordinator = "coordinator"  # koordynator SilverTech
    observer = "observer"        # tylko podgląd, bez alertów krytycznych


class NotifyChannel(str, enum.Enum):
    sms = "sms"
    email = "email"
    push = "push"
    call = "call"


class DeliveryMode(str, enum.Enum):
    digest = "digest"        # zbiorczo (żółty) — raz dziennie
    immediate = "immediate"  # natychmiast (czerwony)
    bypass_dnd = "bypass_dnd"  # z pominięciem trybu Nie przeszkadzać (fioletowy)


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    acknowledged = "acknowledged"  # opiekun potwierdził


class FamilyMember(Base):
    __tablename__ = "family_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)

    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[FamilyRole] = mapped_column(Enum(FamilyRole), default=FamilyRole.secondary)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    preferred_channel: Mapped[NotifyChannel] = mapped_column(Enum(NotifyChannel), default=NotifyChannel.sms)
    dnd_start: Mapped[int | None] = mapped_column(Integer, nullable=True)  # godzina 0-23
    dnd_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="recipient", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FamilyMember s{self.senior_id} {self.name!r} {self.role.value}>"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("family_members.id"), index=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)

    level: Mapped[SemaphoreLevel] = mapped_column(Enum(SemaphoreLevel), index=True)
    channel: Mapped[NotifyChannel] = mapped_column(Enum(NotifyChannel))
    mode: Mapped[DeliveryMode] = mapped_column(Enum(DeliveryMode))
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus), default=NotificationStatus.pending, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    recipient: Mapped["FamilyMember"] = relationship(back_populates="notifications")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Notification {self.level.value} -> fm{self.recipient_id} {self.status.value}>"
