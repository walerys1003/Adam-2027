"""Panel administratora Adama (ETAP 35) — backend floty, modeli, providerów, logów.

Zaplecze panelu admina (AVA-Admin-UI): przegląd i sterowanie stanem systemu:
- **fleet**     — jednostki wdrożeniowe (węzły/urządzenia obsługujące seniorów),
- **models**    — rejestr modeli AI (ASR/LLM/TTS) z aktywnym providerem i statusem,
- **providers** — stan integracji zewnętrznych (Twilio/SendGrid/FCM/OpenAI/…),
- **logs**      — systemowy dziennik zdarzeń administracyjnych/operacyjnych.

Moduł jest czysty (SQLAlchemy + serwis), bez sieci. Realny stan providerów jest
odczytywany fail-safe z konfiguracji ENV (obecność sekretów), a nie przez
połączenia — zgodnie z zasadą, że sandbox/test nie wykonuje wywołań zewnętrznych.
"""
from __future__ import annotations

from .models import (
    FleetUnit, FleetStatus,
    ModelEntry, ModelKind, ModelStatus,
    ProviderEntry, ProviderKind, ProviderState,
    AdminLog, LogLevel,
)
from .service import AdminService

__all__ = [
    "FleetUnit", "FleetStatus",
    "ModelEntry", "ModelKind", "ModelStatus",
    "ProviderEntry", "ProviderKind", "ProviderState",
    "AdminLog", "LogLevel",
    "AdminService",
]
