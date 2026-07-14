"""ConsentService (F12, ETAP 25) — rejestr zgód RODO/AI Act + bramka zgód.

Bramka (consent gate): przed startem rozmowy w trybie produkcyjnym sprawdzamy,
czy senior ma AKTYWNE (granted) zgody obowiązkowe (REQUIRED_FOR_CALL). Brak → blok.

Model zgody „ostatnia wygrywa": dla danego typu obowiązuje najświeższy wpis.
Wycofanie tworzy zdarzenie `withdrawn` (nie kasujemy historii — dowód rozliczalności).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    Consent, ConsentType, ConsentStatus, REQUIRED_FOR_CALL,
    DataProcessingLog, ProcessingAction, DataCategory,
)


@dataclass
class ConsentGateResult:
    allowed: bool
    missing: list[ConsentType] = field(default_factory=list)

    @property
    def missing_values(self) -> list[str]:
        return [c.value for c in self.missing]


class ConsentService:
    def __init__(self, session: Session):
        self.session = session

    # ---- rejestracja / wycofanie ----
    def grant(self, senior_id: int, consent_type: ConsentType, *,
              source: str | None = None, actor: str | None = None,
              note: str | None = None) -> Consent:
        entry = Consent(
            senior_id=senior_id, consent_type=consent_type,
            status=ConsentStatus.granted, source=source, actor=actor, note=note,
            granted_at=datetime.utcnow(),
        )
        self.session.add(entry)
        self.session.flush()
        return entry

    def withdraw(self, senior_id: int, consent_type: ConsentType, *,
                 actor: str | None = None, note: str | None = None) -> Consent:
        entry = Consent(
            senior_id=senior_id, consent_type=consent_type,
            status=ConsentStatus.withdrawn, actor=actor, note=note,
            withdrawn_at=datetime.utcnow(),
        )
        self.session.add(entry)
        self.session.flush()
        return entry

    # ---- odczyt stanu ----
    def current(self, senior_id: int, consent_type: ConsentType) -> Consent | None:
        """Najświeższy wpis dla danego typu zgody (ostatni wygrywa)."""
        return self.session.scalars(
            select(Consent)
            .where(Consent.senior_id == senior_id, Consent.consent_type == consent_type)
            .order_by(Consent.id.desc())
            .limit(1)
        ).first()

    def is_granted(self, senior_id: int, consent_type: ConsentType) -> bool:
        c = self.current(senior_id, consent_type)
        return bool(c and c.status == ConsentStatus.granted)

    def snapshot(self, senior_id: int) -> dict[str, str]:
        """Aktualny stan wszystkich typów zgód (typ → status/'none')."""
        out: dict[str, str] = {}
        for ct in ConsentType:
            c = self.current(senior_id, ct)
            out[ct.value] = c.status.value if c else "none"
        return out

    def history(self, senior_id: int, limit: int = 100) -> list[Consent]:
        return list(self.session.scalars(
            select(Consent).where(Consent.senior_id == senior_id)
            .order_by(Consent.id.desc()).limit(limit)
        ))

    # ---- bramka zgód (consent gate) ----
    def check_call_gate(self, senior_id: int) -> ConsentGateResult:
        """Czy można rozpocząć rozmowę? Wymaga aktywnych zgód REQUIRED_FOR_CALL."""
        missing = [ct for ct in REQUIRED_FOR_CALL if not self.is_granted(senior_id, ct)]
        return ConsentGateResult(allowed=not missing, missing=missing)

    def log_gate_check(self, senior_id: int, result: ConsentGateResult,
                       actor: str | None = None) -> None:
        """Zapisuje sprawdzenie bramki w rejestrze czynności (rozliczalność)."""
        detail = ("bramka OK" if result.allowed
                  else f"bramka ODMOWA — brak: {result.missing_values}")
        self.session.add(DataProcessingLog(
            senior_id=senior_id, action=ProcessingAction.access,
            category=DataCategory.profile, actor=actor, detail=detail,
            legal_basis="art. 6/9 RODO (consent gate)",
        ))
        self.session.flush()
