"""
F15 — Integracja 112 (wezwanie służb ratunkowych).

EmergencyService buduje kompletny payload dla służb ratunkowych przy eskalacji
PURPLE (dane lokalizacyjne, wiek, aktywne leki, ostatnie pomiary, powód), generuje
komunikat głosowy dla dyspozytora (audio.py), próbuje realnego wywołania przez
dialplan/ARI (dialplan.py, fail-safe) i zapisuje ślad w rejestrze EmergencyCall.
"""
from .payload import EmergencyPayload, EmergencyService
from .audio import EmergencyAudioScript, build_emergency_audio
from .dialplan import (
    render_emergency_dialplan, originate_emergency,
    EmergencyOriginator, NullEmergencyOriginator, OriginateResult,
    EMERGENCY_NUMBER,
)
from .models import EmergencyCall, EmergencyStatus

__all__ = [
    "EmergencyPayload", "EmergencyService",
    "EmergencyAudioScript", "build_emergency_audio",
    "render_emergency_dialplan", "originate_emergency",
    "EmergencyOriginator", "NullEmergencyOriginator", "OriginateResult",
    "EMERGENCY_NUMBER",
    "EmergencyCall", "EmergencyStatus",
]
