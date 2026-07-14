"""Serwis panelu admina (ETAP 35) — flota, modele, providerzy, logi.

Czysty serwis na sesji SQLAlchemy. Stan providerów jest wyznaczany fail-safe z
konfiguracji ENV (obecność kompletu sekretów), bez wykonywania połączeń — spójnie
z fabryką `family.build_adapters()` (brak sekretów → degradacja do NullAdapter).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from .models import (
    FleetUnit, FleetStatus,
    ModelEntry, ModelKind, ModelStatus,
    ProviderEntry, ProviderKind, ProviderState,
    AdminLog, LogLevel,
)


# Mapowanie provider → wymagane zmienne ENV (komplet = configured).
_PROVIDER_ENV: dict[str, tuple[ProviderKind, str, tuple[str, ...]]] = {
    "twilio":   (ProviderKind.sms, "Twilio SMS",
                 ("ADAM_TWILIO_SID", "ADAM_TWILIO_TOKEN", "ADAM_TWILIO_FROM")),
    "sendgrid": (ProviderKind.email, "SendGrid Email",
                 ("ADAM_SENDGRID_KEY", "ADAM_SENDGRID_FROM")),
    "fcm":      (ProviderKind.push, "Firebase Cloud Messaging",
                 ("ADAM_FCM_KEY",)),
    "openai":   (ProviderKind.llm, "OpenAI (LLM/ASR/TTS)",
                 ("ADAM_OPENAI_KEY",)),
    "elevenlabs": (ProviderKind.tts, "ElevenLabs TTS",
                   ("ADAM_ELEVENLABS_KEY",)),
    "deepgram": (ProviderKind.asr, "Deepgram (dual-STT)",
                 ("ADAM_DEEPGRAM_KEY",)),
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AdminService:
    def __init__(self, session: Session):
        self.session = session

    # ---------------------------------------------------------- FLOTA
    def register_unit(
        self, code: str, name: str, *,
        region: str = "eu-central", capacity: int = 50,
        status: FleetStatus = FleetStatus.offline,
    ) -> FleetUnit:
        unit = FleetUnit(code=code, name=name, region=region,
                         capacity=capacity, status=status)
        self.session.add(unit)
        self.session.flush()
        return unit

    def set_unit_status(self, unit_id: int, status: FleetStatus,
                        *, active_calls: int | None = None) -> FleetUnit:
        unit = self.session.get(FleetUnit, unit_id)
        if unit is None:
            raise ValueError(f"Brak jednostki floty id={unit_id}")
        unit.status = status
        unit.last_seen = _now()
        if active_calls is not None:
            unit.active_calls = active_calls
        self.session.flush()
        return unit

    def fleet(self) -> list[FleetUnit]:
        return list(self.session.execute(
            select(FleetUnit).order_by(FleetUnit.code)
        ).scalars())

    def fleet_summary(self) -> dict:
        units = self.fleet()
        by_status: dict[str, int] = {}
        for u in units:
            by_status[u.status.value] = by_status.get(u.status.value, 0) + 1
        return {
            "total": len(units),
            "by_status": by_status,
            "online": by_status.get("online", 0),
            "active_calls": sum(u.active_calls for u in units),
            "capacity": sum(u.capacity for u in units),
        }

    # ---------------------------------------------------------- MODELE AI
    def register_model(
        self, kind: ModelKind, name: str, provider: str, *,
        status: ModelStatus = ModelStatus.standby,
        is_primary: bool = False, params: dict | None = None,
    ) -> ModelEntry:
        entry = ModelEntry(
            kind=kind, name=name, provider=provider, status=status,
            is_primary=is_primary,
            params_json=json.dumps(params) if params else None,
        )
        self.session.add(entry)
        self.session.flush()
        if is_primary:
            self._demote_other_primaries(kind, entry.id)
        return entry

    def _demote_other_primaries(self, kind: ModelKind, keep_id: int) -> None:
        others = self.session.execute(
            select(ModelEntry).where(ModelEntry.kind == kind,
                                     ModelEntry.id != keep_id,
                                     ModelEntry.is_primary.is_(True))
        ).scalars()
        for m in others:
            m.is_primary = False
        self.session.flush()

    def set_primary_model(self, model_id: int) -> ModelEntry:
        entry = self.session.get(ModelEntry, model_id)
        if entry is None:
            raise ValueError(f"Brak modelu id={model_id}")
        entry.is_primary = True
        entry.status = ModelStatus.active
        self.session.flush()
        self._demote_other_primaries(entry.kind, entry.id)
        return entry

    def models(self, kind: ModelKind | None = None) -> list[ModelEntry]:
        stmt = select(ModelEntry)
        if kind is not None:
            stmt = stmt.where(ModelEntry.kind == kind)
        return list(self.session.execute(stmt.order_by(ModelEntry.kind)).scalars())

    # ---------------------------------------------------------- PROVIDERZY
    @staticmethod
    def probe_provider_state(key: str) -> ProviderState:
        """Fail-safe: stan providera z obecności kompletu sekretów w ENV (bez sieci)."""
        spec = _PROVIDER_ENV.get(key)
        if spec is None:
            return ProviderState.disabled
        _, _, required = spec
        if all(os.getenv(v, "").strip() for v in required):
            return ProviderState.configured
        return ProviderState.missing_secrets

    def sync_providers(self) -> list[ProviderEntry]:
        """Tworzy/odświeża wpisy providerów wg katalogu + aktualnego stanu ENV."""
        out: list[ProviderEntry] = []
        for key, (kind, display, required) in _PROVIDER_ENV.items():
            entry = self.session.execute(
                select(ProviderEntry).where(ProviderEntry.key == key)
            ).scalar_one_or_none()
            state = self.probe_provider_state(key)
            if entry is None:
                entry = ProviderEntry(
                    key=key, kind=kind, display_name=display,
                    state=state, required_env=",".join(required),
                )
                self.session.add(entry)
            else:
                entry.state = state
                entry.required_env = ",".join(required)
            out.append(entry)
        self.session.flush()
        return out

    def providers(self) -> list[ProviderEntry]:
        return list(self.session.execute(
            select(ProviderEntry).order_by(ProviderEntry.key)
        ).scalars())

    # ---------------------------------------------------------- LOGI
    def log(
        self, level: LogLevel, source: str, message: str, *,
        actor: str | None = None, meta: dict | None = None,
    ) -> AdminLog:
        entry = AdminLog(
            level=level, source=source, message=message, actor=actor,
            meta_json=json.dumps(meta) if meta else None,
        )
        self.session.add(entry)
        self.session.flush()
        return entry

    def logs(
        self, *, level: LogLevel | None = None, source: str | None = None,
        limit: int = 100,
    ) -> list[AdminLog]:
        stmt = select(AdminLog)
        if level is not None:
            stmt = stmt.where(AdminLog.level == level)
        if source is not None:
            stmt = stmt.where(AdminLog.source == source)
        stmt = stmt.order_by(desc(AdminLog.id)).limit(limit)
        return list(self.session.execute(stmt).scalars())
