"""Modele panelu admina (ETAP 35): flota, modele AI, providerzy, logi."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Enum, Text, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from adam_modules.common.db import Base


# ------------------------------------------------------------------ FLOTA

class FleetStatus(str, enum.Enum):
    online = "online"          # jednostka pracuje normalnie
    degraded = "degraded"      # działa, ale z ograniczeniami (np. jeden STT padł)
    offline = "offline"        # niedostępna
    maintenance = "maintenance"  # celowo wyłączona do serwisu


class FleetUnit(Base):
    """Jednostka wdrożeniowa obsługująca połączenia z seniorami (węzeł/urządzenie)."""
    __tablename__ = "fleet_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    region: Mapped[str] = mapped_column(String(64), default="eu-central")
    status: Mapped[FleetStatus] = mapped_column(
        Enum(FleetStatus), default=FleetStatus.offline, index=True
    )
    active_calls: Mapped[int] = mapped_column(Integer, default=0)
    capacity: Mapped[int] = mapped_column(Integer, default=50)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# ------------------------------------------------------------------ MODELE AI

class ModelKind(str, enum.Enum):
    asr = "asr"    # rozpoznawanie mowy
    llm = "llm"    # model językowy
    tts = "tts"    # synteza mowy


class ModelStatus(str, enum.Enum):
    active = "active"          # obecnie używany
    standby = "standby"        # skonfigurowany, w rezerwie (np. drugi STT)
    disabled = "disabled"      # wyłączony


class ModelEntry(Base):
    """Wpis rejestru modeli AI — który silnik/provider obsługuje dany rodzaj."""
    __tablename__ = "admin_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[ModelKind] = mapped_column(Enum(ModelKind), index=True)
    name: Mapped[str] = mapped_column(String(120))              # np. "whisper-large-v3"
    provider: Mapped[str] = mapped_column(String(64))           # np. "openai", "deepgram"
    status: Mapped[ModelStatus] = mapped_column(
        Enum(ModelStatus), default=ModelStatus.standby, index=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    params_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# ------------------------------------------------------------------ PROVIDERZY

class ProviderKind(str, enum.Enum):
    sms = "sms"
    email = "email"
    push = "push"
    asr = "asr"
    llm = "llm"
    tts = "tts"
    telephony = "telephony"


class ProviderState(str, enum.Enum):
    configured = "configured"      # komplet sekretów obecny (gotowy do pracy)
    missing_secrets = "missing_secrets"  # brak/niekomplet sekretów (fail-safe → null)
    disabled = "disabled"          # celowo wyłączony


class ProviderEntry(Base):
    """Stan integracji zewnętrznej (Twilio/SendGrid/FCM/OpenAI/…)."""
    __tablename__ = "admin_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # "twilio"
    kind: Mapped[ProviderKind] = mapped_column(Enum(ProviderKind), index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    state: Mapped[ProviderState] = mapped_column(
        Enum(ProviderState), default=ProviderState.missing_secrets, index=True
    )
    # lista zmiennych ENV wymaganych do działania (przecinkami) — bez wartości!
    required_env: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# ------------------------------------------------------------------ LOGI

class LogLevel(str, enum.Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class AdminLog(Base):
    """Systemowy dziennik zdarzeń administracyjnych/operacyjnych."""
    __tablename__ = "admin_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[LogLevel] = mapped_column(Enum(LogLevel), default=LogLevel.info, index=True)
    source: Mapped[str] = mapped_column(String(64), index=True)   # np. "fleet", "voice"
    message: Mapped[str] = mapped_column(Text)
    actor: Mapped[str | None] = mapped_column(String(120), nullable=True)  # e-mail admina
    meta_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
