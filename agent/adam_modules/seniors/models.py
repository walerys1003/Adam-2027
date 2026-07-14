"""
Model Senior (F1) — profil podopiecznego.

PII (PESEL, telefon) przechowywane WYŁĄCZNIE zaszyfrowane (kolumny *_enc) +
blind index (*_bidx) do wyszukiwania. Właściwości pesel/phone szyfrują/odszyfrowują
w locie przez FieldCipher.
"""
from __future__ import annotations

import enum
from datetime import datetime, date

from sqlalchemy import String, Integer, Date, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from adam_modules.common.db import Base
from adam_modules.common.crypto import get_cipher


class Package(str, enum.Enum):
    basic = "basic"
    family = "family"
    premium = "premium"


class SemaphoreLevel(str, enum.Enum):
    green = "green"
    yellow = "yellow"
    red = "red"
    purple = "purple"


class Senior(Base):
    __tablename__ = "seniors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # --- PII zaszyfrowane ---
    _pesel_enc: Mapped[str | None] = mapped_column("pesel_enc", String(256), nullable=True)
    pesel_bidx: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    _phone_enc: Mapped[str | None] = mapped_column("phone_enc", String(256), nullable=True)
    phone_bidx: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)

    # --- Adres (do payloadu 112, F17) ---
    address: Mapped[str | None] = mapped_column(String(256), nullable=True)
    district: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)

    package: Mapped[Package] = mapped_column(Enum(Package), default=Package.basic)
    semaphore: Mapped[SemaphoreLevel] = mapped_column(
        Enum(SemaphoreLevel), default=SemaphoreLevel.green, index=True
    )
    active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # ---- właściwości PII (szyfrowanie w locie) ----
    @property
    def pesel(self) -> str | None:
        return get_cipher().decrypt(self._pesel_enc)

    @pesel.setter
    def pesel(self, value: str | None) -> None:
        cipher = get_cipher()
        self._pesel_enc = cipher.encrypt(value)
        self.pesel_bidx = cipher.blind_index(value) if value else None

    @property
    def phone(self) -> str | None:
        return get_cipher().decrypt(self._phone_enc)

    @phone.setter
    def phone(self, value: str | None) -> None:
        cipher = get_cipher()
        self._phone_enc = cipher.encrypt(value)
        self.phone_bidx = cipher.blind_index(value) if value else None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def age(self) -> int | None:
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Senior {self.external_id} {self.full_name} {self.semaphore.value}>"
