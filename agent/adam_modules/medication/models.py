"""
Modele F6 — Medication tracker.

Medication         — lek przypisany seniorowi (nazwa, dawka, forma, uwagi).
MedicationSchedule — harmonogram: o której i w jakie dni brać dany lek.
DoseLog            — log pojedynczej dawki (zaplanowana / wzięta / pominięta).
"""
from __future__ import annotations

import enum
from datetime import datetime, time

from sqlalchemy import String, Integer, Boolean, DateTime, Time, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adam_modules.common.db import Base


class MedForm(str, enum.Enum):
    tablet = "tablet"          # tabletka
    capsule = "capsule"        # kapsułka
    liquid = "liquid"          # płyn / syrop
    injection = "injection"    # zastrzyk
    drops = "drops"            # krople
    inhaler = "inhaler"        # inhalator
    patch = "patch"            # plaster
    other = "other"


class DoseStatus(str, enum.Enum):
    scheduled = "scheduled"    # zaplanowana, jeszcze nie minęła
    taken = "taken"            # potwierdzone przyjęcie
    missed = "missed"          # pominięta (→ trigger missed_medication)
    skipped = "skipped"        # świadomie pominięta (za wiedzą opiekuna)
    late = "late"             # wzięta po czasie


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)

    name: Mapped[str] = mapped_column(String(160))
    dosage: Mapped[str | None] = mapped_column(String(80), nullable=True)  # np. "1 tabletka 10mg"
    form: Mapped[MedForm] = mapped_column(Enum(MedForm), default=MedForm.tablet)
    instructions: Mapped[str | None] = mapped_column(String(500), nullable=True)  # np. "po posiłku"
    prescriber: Mapped[str | None] = mapped_column(String(120), nullable=True)     # lekarz zlecający

    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    schedules: Mapped[list["MedicationSchedule"]] = relationship(
        back_populates="medication", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Medication s{self.senior_id} {self.name!r}>"


class MedicationSchedule(Base):
    __tablename__ = "medication_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medication_id: Mapped[int] = mapped_column(ForeignKey("medications.id"), index=True)

    at_time: Mapped[time] = mapped_column(Time)
    # bitmaska dni tygodnia: 0b1111111 = codziennie (poniedziałek..niedziela)
    days_mask: Mapped[int] = mapped_column(Integer, default=0b1111111)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    medication: Mapped["Medication"] = relationship(back_populates="schedules")

    def occurs_on(self, weekday: int) -> bool:
        """weekday: 0=poniedziałek .. 6=niedziela (jak datetime.weekday())."""
        return bool(self.days_mask & (1 << weekday))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Schedule med{self.medication_id} {self.at_time}>"


class DoseLog(Base):
    __tablename__ = "dose_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medication_id: Mapped[int] = mapped_column(ForeignKey("medications.id"), index=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)

    scheduled_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    status: Mapped[DoseStatus] = mapped_column(Enum(DoseStatus), default=DoseStatus.scheduled, index=True)
    taken_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DoseLog med{self.medication_id} {self.status.value} @{self.scheduled_at}>"
