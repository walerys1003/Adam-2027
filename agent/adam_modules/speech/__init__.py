"""
F14 — Optymalizacja mowy senioralnej.

build_speech_profile() dobiera parametry TTS (tempo, głośność, pauzy, ton) oraz
strategię (powtórzenia, prostota) na podstawie niedosłuchu, tempa poznawczego
i wieku. Wynik trafia do System Promptu (F5) i konfiguracji TTS.
"""
from .profile import (
    SpeechProfile, HearingLevel, CognitivePace, build_speech_profile,
)

__all__ = [
    "SpeechProfile", "HearingLevel", "CognitivePace", "build_speech_profile",
]
