"""
WearableService — rejestracja urządzeń, ingest pomiarów, threshold engine (F10).

Threshold engine: domyślne progi (DEFAULT_THRESHOLDS) można nadpisać ręcznie
(manual_override) per senior. Każdy pomiar poza progiem oznaczamy breached=True
i mapujemy na VitalType — sygnał wejściowy do CrisisDetector.detect_vitals (F8).

Audyt SHA-256: dla każdego pomiaru liczymy hash z (device, typ, wartość, czas),
gwarantując integralność danych zdrowotnych (nie da się cicho zmienić wartości).
"""
from __future__ import annotations

import hashlib
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from adam_modules.seniors.models import Senior
from .models import (
    WearableDevice, VitalReading, VitalThreshold, VitalType, WearableVendor,
)
from .adapters import get_adapter, NormalizedReading

# Domyślne progi alarmowe (dorośli/seniorzy). None = brak limitu z tej strony.
DEFAULT_THRESHOLDS: dict[VitalType, tuple[float | None, float | None]] = {
    VitalType.heart_rate: (40.0, 130.0),
    VitalType.spo2: (90.0, None),
    VitalType.systolic: (90.0, 180.0),
    VitalType.diastolic: (50.0, 110.0),
    VitalType.temperature: (35.0, 38.5),
    VitalType.sleep_hours: (3.0, None),
    VitalType.steps: (None, None),
}


def compute_audit_hash(device_id: int, vital_type: VitalType, value: float, measured_at: datetime) -> str:
    raw = f"{device_id}|{vital_type.value}|{value}|{measured_at.isoformat()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class WearableService:
    def __init__(self, session: Session):
        self.session = session

    # ---- urządzenia ----
    def register_device(self, senior: Senior, vendor: WearableVendor, external_id: str,
                        model: str | None = None) -> WearableDevice:
        dev = WearableDevice(senior_id=senior.id, vendor=vendor, external_id=external_id, model=model)
        self.session.add(dev)
        self.session.flush()
        return dev

    def devices(self, senior_id: int) -> list[WearableDevice]:
        return list(self.session.scalars(
            select(WearableDevice).where(WearableDevice.senior_id == senior_id)
        ))

    # ---- progi ----
    def set_threshold(self, senior: Senior, vital_type: VitalType,
                     min_value: float | None, max_value: float | None) -> VitalThreshold:
        existing = self.session.scalar(
            select(VitalThreshold).where(
                VitalThreshold.senior_id == senior.id,
                VitalThreshold.vital_type == vital_type,
            )
        )
        if existing:
            existing.min_value = min_value
            existing.max_value = max_value
            existing.manual_override = True
            self.session.flush()
            return existing
        th = VitalThreshold(senior_id=senior.id, vital_type=vital_type,
                            min_value=min_value, max_value=max_value, manual_override=True)
        self.session.add(th)
        self.session.flush()
        return th

    def effective_threshold(self, senior_id: int, vital_type: VitalType) -> tuple[float | None, float | None]:
        override = self.session.scalar(
            select(VitalThreshold).where(
                VitalThreshold.senior_id == senior_id,
                VitalThreshold.vital_type == vital_type,
            )
        )
        if override:
            return override.min_value, override.max_value
        return DEFAULT_THRESHOLDS.get(vital_type, (None, None))

    def is_breach(self, senior_id: int, vital_type: VitalType, value: float) -> bool:
        lo, hi = self.effective_threshold(senior_id, vital_type)
        if lo is not None and value < lo:
            return True
        if hi is not None and value > hi:
            return True
        return False

    # ---- ingest ----
    def ingest_reading(self, device: WearableDevice, vital_type: VitalType, value: float,
                       measured_at: datetime | None = None) -> VitalReading:
        measured_at = measured_at or datetime.utcnow()
        breached = self.is_breach(device.senior_id, vital_type, value)
        reading = VitalReading(
            device_id=device.id, senior_id=device.senior_id, vital_type=vital_type,
            value=value, measured_at=measured_at, breached=breached,
            audit_hash=compute_audit_hash(device.id, vital_type, value, measured_at),
        )
        self.session.add(reading)
        device.last_sync_at = measured_at
        self.session.flush()
        return reading

    def ingest_payload(self, device: WearableDevice, payload: dict) -> list[VitalReading]:
        """Normalizuje payload dostawcy i zapisuje wszystkie pomiary."""
        adapter = get_adapter(device.vendor)
        if adapter is None:
            return []
        normalized: list[NormalizedReading] = adapter.normalize(payload)
        return [self.ingest_reading(device, n.vital_type, n.value, n.measured_at) for n in normalized]

    # ---- odczyty / audyt ----
    def latest(self, senior_id: int, vital_type: VitalType) -> VitalReading | None:
        return self.session.scalar(
            select(VitalReading).where(
                VitalReading.senior_id == senior_id,
                VitalReading.vital_type == vital_type,
            ).order_by(VitalReading.measured_at.desc())
        )

    def breaches(self, senior_id: int, limit: int = 50) -> list[VitalReading]:
        return list(self.session.scalars(
            select(VitalReading).where(
                VitalReading.senior_id == senior_id,
                VitalReading.breached.is_(True),
            ).order_by(VitalReading.measured_at.desc()).limit(limit)
        ))

    def verify_integrity(self, reading: VitalReading) -> bool:
        """Sprawdza, czy pomiar nie został zmodyfikowany (hash się zgadza)."""
        expected = compute_audit_hash(reading.device_id, reading.vital_type,
                                      reading.value, reading.measured_at)
        return expected == reading.audit_hash
