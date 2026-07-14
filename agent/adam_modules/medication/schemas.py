"""Pydantic v2 schematy dla API leków (F6)."""
from __future__ import annotations

from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field

from .models import MedForm, DoseStatus


class ScheduleCreate(BaseModel):
    at_time: time
    days_mask: int = Field(default=0b1111111, ge=0, le=0b1111111)


class MedicationBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    dosage: str | None = Field(default=None, max_length=80)
    form: MedForm = MedForm.tablet
    instructions: str | None = Field(default=None, max_length=500)
    prescriber: str | None = Field(default=None, max_length=120)


class MedicationCreate(MedicationBase):
    schedules: list[ScheduleCreate] = Field(default_factory=list)


class MedicationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    dosage: str | None = None
    form: MedForm | None = None
    instructions: str | None = None
    prescriber: str | None = None
    active: bool | None = None


class ScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    at_time: time
    days_mask: int
    active: bool


class MedicationOut(MedicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    senior_id: int
    active: bool
    created_at: datetime | None = None
    schedules: list[ScheduleOut] = Field(default_factory=list)


class DoseLogCreate(BaseModel):
    medication_id: int
    scheduled_at: datetime
    status: DoseStatus = DoseStatus.scheduled


class AdherenceReport(BaseModel):
    """Raport przyjmowania leków w oknie czasowym (F6.2)."""
    senior_id: int
    total_doses: int
    taken: int
    missed: int
    late: int
    skipped: int
    adherence_rate: float  # 0.0..1.0 (taken+late) / (total - skipped)
