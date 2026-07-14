"""
Modele F10 — Wearables.

WearableDevice — urządzenie noszone przypisane seniorowi (dostawca, id zewn.).
VitalReading   — pojedynczy pomiar (HR/SpO2/BP/kroki/sen) z audytem SHA-256.
VitalThreshold — próg alarmowy (auto domyślny lub ręczne nadpisanie opiekuna).
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Integer, Float, Boolean, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adam_modules.common.db import Base


class WearableVendor(str, enum.Enum):
    xiaomi_zepp = "xiaomi_zepp"       # Xiaomi / Zepp Life
    apple_health = "apple_health"     # Apple HealthKit
    garmin = "garmin"                 # Garmin Connect
    fitbit = "fitbit"                 # Fitbit Web API
    generic = "generic"


class VitalType(str, enum.Enum):
    heart_rate = "heart_rate"     # bpm
    spo2 = "spo2"                 # %
    systolic = "systolic"         # mmHg
    diastolic = "diastolic"       # mmHg
    steps = "steps"               # liczba
    sleep_hours = "sleep_hours"   # godziny
    temperature = "temperature"   # °C


class WearableDevice(Base):
    __tablename__ = "wearable_devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)

    vendor: Mapped[WearableVendor] = mapped_column(Enum(WearableVendor), default=WearableVendor.generic)
    external_id: Mapped[str] = mapped_column(String(120))
    model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    readings: Mapped[list["VitalReading"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<WearableDevice s{self.senior_id} {self.vendor.value}>"


class VitalReading(Base):
    __tablename__ = "vital_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("wearable_devices.id"), index=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)

    vital_type: Mapped[VitalType] = mapped_column(Enum(VitalType), index=True)
    value: Mapped[float] = mapped_column(Float)
    measured_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    breached: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    # audyt niezmienności pomiaru (integralność danych zdrowotnych)
    audit_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    device: Mapped["WearableDevice"] = relationship(back_populates="readings")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<VitalReading {self.vital_type.value}={self.value} breach={self.breached}>"


class VitalThreshold(Base):
    __tablename__ = "vital_thresholds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)

    vital_type: Mapped[VitalType] = mapped_column(Enum(VitalType))
    min_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    manual_override: Mapped[bool] = mapped_column(Boolean, default=False)  # ustawione ręcznie przez opiekuna
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:  # pragma: no cover
        return f"<VitalThreshold {self.vital_type.value} [{self.min_value},{self.max_value}]>"
