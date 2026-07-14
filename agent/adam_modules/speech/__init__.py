"""
F14 — Optymalizacja mowy senioralnej.

build_speech_profile() dobiera parametry TTS (tempo, głośność, pauzy, ton) oraz
strategię (powtórzenia, prostota) na podstawie niedosłuchu, tempa poznawczego
i wieku. Wynik trafia do System Promptu (F5) i konfiguracji TTS.
"""
from .profile import (
    SpeechProfile, HearingLevel, CognitivePace, build_speech_profile,
)
from .preprocessor import (
    SeniorAudioPreprocessor, PreprocessorConfig, FrameStats,
    AdaptiveVAD, VADConfig, VADResult, VADState,
    frame_rms, rms_to_dbfs,
)
from .wielkopolska import (
    normalize_regional, NormalizationResult, dictionary_size,
    CRISIS_REGIONALISMS,
)

__all__ = [
    "SpeechProfile", "HearingLevel", "CognitivePace", "build_speech_profile",
    "SeniorAudioPreprocessor", "PreprocessorConfig", "FrameStats",
    "AdaptiveVAD", "VADConfig", "VADResult", "VADState",
    "frame_rms", "rms_to_dbfs",
    "normalize_regional", "NormalizationResult", "dictionary_size",
    "CRISIS_REGIONALISMS",
]
