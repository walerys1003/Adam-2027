"""
F10 — Wearables.

Adaptery Xiaomi Zepp / Apple HealthKit / Garmin / Fitbit normalizują pomiary
do wspólnego formatu. Threshold engine (auto + ręczne nadpisanie) oznacza
przekroczenia (breached) — zasila CrisisDetector (F8). Audyt SHA-256 gwarantuje
integralność danych zdrowotnych.
"""
from .models import (
    WearableDevice, VitalReading, VitalThreshold, WearableVendor, VitalType,
)
from .adapters import (
    WearableAdapter, NormalizedReading, get_adapter,
    XiaomiZeppAdapter, AppleHealthAdapter, GarminAdapter, FitbitAdapter,
)
from .service import WearableService, DEFAULT_THRESHOLDS, compute_audit_hash

__all__ = [
    "WearableDevice", "VitalReading", "VitalThreshold", "WearableVendor", "VitalType",
    "WearableAdapter", "NormalizedReading", "get_adapter",
    "XiaomiZeppAdapter", "AppleHealthAdapter", "GarminAdapter", "FitbitAdapter",
    "WearableService", "DEFAULT_THRESHOLDS", "compute_audit_hash",
]
