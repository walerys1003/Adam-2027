"""
F17 — Integracja 112.

EmergencyService buduje kompletny payload dla służb ratunkowych przy eskalacji
PURPLE: dane lokalizacyjne, wiek, aktywne leki, ostatnie pomiary, powód wezwania.
"""
from .payload import EmergencyPayload, EmergencyService

__all__ = ["EmergencyPayload", "EmergencyService"]
