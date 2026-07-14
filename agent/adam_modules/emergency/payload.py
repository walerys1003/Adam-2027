"""
F17 — Integracja 112 (payload dla służb ratunkowych).

Buduje ustrukturyzowany, zwięzły payload przekazywany operatorowi 112 przy
eskalacji PURPLE: dane lokalizacyjne, wiek, aktywne leki, ostatnie pomiary
życiowe i powód wezwania. Payload musi być deterministyczny i kompletny —
od niego zależy szybkość reakcji.

Uwaga RODO: przekazanie danych do 112 ma podstawę w art. 6 ust. 1 lit. d
(ochrona żywotnych interesów). Operacja powinna być logowana (RodoService).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

from adam_modules.seniors.models import Senior


@dataclass
class EmergencyPayload:
    external_id: str
    full_name: str
    age: int | None
    address: str | None
    district: str | None
    phone: str | None
    reason: str
    semaphore_level: str
    medications: list[str] = field(default_factory=list)
    recent_vitals: dict = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def dispatch_summary(self) -> str:
        """Zwięzły komunikat głosowy/tekstowy dla operatora 112."""
        who = f"{self.full_name}, {self.age} lat" if self.age else self.full_name
        where = self.address or "adres nieznany"
        meds = f" Leki: {', '.join(self.medications)}." if self.medications else ""
        vitals = ""
        if self.recent_vitals:
            vitals = " Pomiary: " + ", ".join(f"{k}={v}" for k, v in self.recent_vitals.items()) + "."
        return f"Zgłoszenie: {self.reason}. Pacjent: {who}. Adres: {where}.{meds}{vitals}"


class EmergencyService:
    def __init__(self, session: Session):
        self.session = session

    def build_payload(self, senior: Senior, reason: str) -> EmergencyPayload:
        return EmergencyPayload(
            external_id=senior.external_id,
            full_name=senior.full_name,
            age=senior.age,
            address=senior.address,
            district=senior.district,
            phone=senior.phone,
            reason=reason,
            semaphore_level=senior.semaphore.value,
            medications=self._active_medications(senior.id),
            recent_vitals=self._recent_vitals(senior.id),
            created_at=datetime.utcnow().isoformat(),
        )

    def _active_medications(self, senior_id: int) -> list[str]:
        try:
            from adam_modules.medication.models import Medication
        except ImportError:  # pragma: no cover
            return []
        rows = self.session.scalars(
            select(Medication).where(
                Medication.senior_id == senior_id, Medication.active.is_(True)
            )
        )
        out = []
        for m in rows:
            out.append(f"{m.name}{(' ' + m.dosage) if m.dosage else ''}")
        return out

    def _recent_vitals(self, senior_id: int) -> dict:
        try:
            from adam_modules.wearables.models import VitalReading, VitalType
        except ImportError:  # pragma: no cover
            return {}
        out: dict = {}
        for vt in (VitalType.heart_rate, VitalType.spo2, VitalType.systolic):
            r = self.session.scalar(
                select(VitalReading).where(
                    VitalReading.senior_id == senior_id,
                    VitalReading.vital_type == vt,
                ).order_by(VitalReading.measured_at.desc())
            )
            if r is not None:
                out[vt.value] = r.value
        return out

    # ---- F15 (ETAP 26): pełny łańcuch wezwania 112 ----
    def dispatch(self, senior: Senior, reason: str, *, originator=None):
        """Buduje payload + skrypt głosowy, próbuje wywołać 112, zapisuje EmergencyCall.

        Bez originatora (dev/sandbox) → status `simulated` (fail-safe, bez wyjątku).
        Zwraca utworzony rekord EmergencyCall.
        """
        from .audio import build_emergency_audio
        from .dialplan import originate_emergency
        from .models import EmergencyCall, EmergencyStatus

        payload = self.build_payload(senior, reason)
        script = build_emergency_audio(payload)
        result = originate_emergency(script, originator)

        if result.simulated:
            status = EmergencyStatus.simulated
        elif result.ok:
            status = EmergencyStatus.dispatched
        else:
            status = EmergencyStatus.failed

        call = EmergencyCall(
            senior_id=senior.id,
            reason=reason,
            semaphore_level=payload.semaphore_level,
            status=status,
            channel_id=result.channel_id,
            payload_json=json.dumps(payload.to_dict(), ensure_ascii=False),
            audio_script=script.full_text(),
            detail=result.detail,
        )
        self.session.add(call)
        self.session.flush()

        # rejestr RODO (art. 6 ust. 1 lit. d — ochrona żywotnych interesów)
        try:
            from adam_modules.rodo import RodoService, ProcessingAction, DataCategory
            RodoService(self.session).log(
                senior.id, ProcessingAction.access, category=DataCategory.reports,
                actor="emergency", detail=f"wezwanie 112: {reason} [{status.value}]",
                legal_basis="art. 6 ust. 1 lit. d RODO",
            )
        except Exception:  # pragma: no cover — log nie może blokować wezwania
            pass

        return call

    def history(self, senior_id: int, limit: int = 50):
        from .models import EmergencyCall
        return list(self.session.scalars(
            select(EmergencyCall).where(EmergencyCall.senior_id == senior_id)
            .order_by(EmergencyCall.id.desc()).limit(limit)
        ))
