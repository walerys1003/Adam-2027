"""Pydantic v2 schematy dla API seniorów (F1.3)."""
from __future__ import annotations

import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import Package, SemaphoreLevel

_PESEL_RE = re.compile(r"^\d{11}$")
_PHONE_RE = re.compile(r"^\+?\d{9,15}$")


def _validate_pesel_checksum(pesel: str) -> bool:
    """Walidacja sumy kontrolnej polskiego numeru PESEL."""
    if not _PESEL_RE.match(pesel):
        return False
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    s = sum(int(d) * w for d, w in zip(pesel[:10], weights))
    control = (10 - (s % 10)) % 10
    return control == int(pesel[10])


class SeniorBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    birth_date: date | None = None
    address: str | None = Field(default=None, max_length=256)
    district: str | None = Field(default=None, max_length=80)
    package: Package = Package.basic


class SeniorCreate(SeniorBase):
    pesel: str | None = None
    phone: str | None = None

    @field_validator("pesel")
    @classmethod
    def _check_pesel(cls, v: str | None) -> str | None:
        if v is not None and not _validate_pesel_checksum(v):
            raise ValueError("Nieprawidłowy PESEL (format lub suma kontrolna)")
        return v

    @field_validator("phone")
    @classmethod
    def _check_phone(cls, v: str | None) -> str | None:
        if v is not None and not _PHONE_RE.match(v):
            raise ValueError("Nieprawidłowy numer telefonu")
        return v


class SeniorUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    birth_date: date | None = None
    address: str | None = None
    district: str | None = None
    package: Package | None = None
    phone: str | None = None
    semaphore: SemaphoreLevel | None = None
    active: bool | None = None


class SeniorOut(SeniorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    semaphore: SemaphoreLevel
    active: bool
    age: int | None = None
    # PII maskowane w odpowiedzi
    pesel_masked: str | None = None
    phone_masked: str | None = None
    created_at: datetime | None = None

    @classmethod
    def from_model(cls, s) -> "SeniorOut":
        pesel = s.pesel
        phone = s.phone
        return cls(
            id=s.id,
            external_id=s.external_id,
            first_name=s.first_name,
            last_name=s.last_name,
            birth_date=s.birth_date,
            address=s.address,
            district=s.district,
            package=s.package,
            semaphore=s.semaphore,
            active=s.active,
            age=s.age,
            pesel_masked=(f"•••••••{pesel[-4:]}" if pesel else None),
            phone_masked=(f"•••{phone[-3:]}" if phone else None),
            created_at=s.created_at,
        )
