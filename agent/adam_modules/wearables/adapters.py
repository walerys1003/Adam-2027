"""
Adaptery wearables (F10.1) — normalizacja danych z różnych dostawców.

Każdy dostawca zwraca inny format; adapter mapuje surowy payload na wspólną
listę (VitalType, value, measured_at). Interfejsy REST realizuje się w
produkcji (OAuth do Fitbit/Garmin, HealthKit export, Zepp API). Tu — protokół
i deterministyczne implementacje na słownikach (test/dev).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from .models import VitalType, WearableVendor


@dataclass
class NormalizedReading:
    vital_type: VitalType
    value: float
    measured_at: datetime


class WearableAdapter(Protocol):
    vendor: WearableVendor

    def normalize(self, payload: dict) -> list[NormalizedReading]:
        ...  # pragma: no cover


def _parse_ts(value, default: datetime | None = None) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            pass
    return default or datetime.utcnow()


class XiaomiZeppAdapter:
    vendor = WearableVendor.xiaomi_zepp

    def normalize(self, payload: dict) -> list[NormalizedReading]:
        out: list[NormalizedReading] = []
        ts = _parse_ts(payload.get("time"))
        m = {
            "hr": VitalType.heart_rate,
            "spo2": VitalType.spo2,
            "steps": VitalType.steps,
            "sleep": VitalType.sleep_hours,
        }
        for key, vt in m.items():
            if key in payload and payload[key] is not None:
                out.append(NormalizedReading(vt, float(payload[key]), ts))
        return out


class AppleHealthAdapter:
    vendor = WearableVendor.apple_health

    def normalize(self, payload: dict) -> list[NormalizedReading]:
        # HealthKit: lista samples {type, value, endDate}
        out: list[NormalizedReading] = []
        type_map = {
            "HKQuantityTypeIdentifierHeartRate": VitalType.heart_rate,
            "HKQuantityTypeIdentifierOxygenSaturation": VitalType.spo2,
            "HKQuantityTypeIdentifierStepCount": VitalType.steps,
            "HKQuantityTypeIdentifierBodyTemperature": VitalType.temperature,
        }
        for s in payload.get("samples", []):
            vt = type_map.get(s.get("type"))
            if vt is not None:
                out.append(NormalizedReading(vt, float(s["value"]), _parse_ts(s.get("endDate"))))
        return out


class GarminAdapter:
    vendor = WearableVendor.garmin

    def normalize(self, payload: dict) -> list[NormalizedReading]:
        out: list[NormalizedReading] = []
        ts = _parse_ts(payload.get("calendarDate"))
        if "restingHeartRate" in payload:
            out.append(NormalizedReading(VitalType.heart_rate, float(payload["restingHeartRate"]), ts))
        if "averageSpo2" in payload:
            out.append(NormalizedReading(VitalType.spo2, float(payload["averageSpo2"]), ts))
        if "totalSteps" in payload:
            out.append(NormalizedReading(VitalType.steps, float(payload["totalSteps"]), ts))
        return out


class FitbitAdapter:
    vendor = WearableVendor.fitbit

    def normalize(self, payload: dict) -> list[NormalizedReading]:
        out: list[NormalizedReading] = []
        ts = _parse_ts(payload.get("dateTime"))
        if "restingHeartRate" in payload:
            out.append(NormalizedReading(VitalType.heart_rate, float(payload["restingHeartRate"]), ts))
        if "spo2" in payload:
            out.append(NormalizedReading(VitalType.spo2, float(payload["spo2"]), ts))
        if "steps" in payload:
            out.append(NormalizedReading(VitalType.steps, float(payload["steps"]), ts))
        return out


ADAPTERS: dict[WearableVendor, WearableAdapter] = {
    WearableVendor.xiaomi_zepp: XiaomiZeppAdapter(),
    WearableVendor.apple_health: AppleHealthAdapter(),
    WearableVendor.garmin: GarminAdapter(),
    WearableVendor.fitbit: FitbitAdapter(),
}


def get_adapter(vendor: WearableVendor) -> WearableAdapter | None:
    return ADAPTERS.get(vendor)
