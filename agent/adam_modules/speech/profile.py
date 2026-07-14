"""
F14 — Optymalizacja mowy senioralnej (audio profile).

Dobór parametrów TTS i strategii rozmowy pod ograniczenia percepcyjne seniorów
(niedosłuch, wolniejsze przetwarzanie, potrzeba powtórzeń). Wynik zasila
System Prompt (F5, parametr speech_profile) oraz konfigurację TTS w runtime.

Parametry są deterministyczne i wyjaśnialne (audytowalne — wymóg AI Act):
wynikają z jawnych reguł na podstawie profilu słuchu/tempa.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, asdict


class HearingLevel(str, enum.Enum):
    normal = "normal"
    mild_loss = "mild_loss"        # lekki niedosłuch
    moderate_loss = "moderate_loss"  # umiarkowany
    severe_loss = "severe_loss"    # znaczny


class CognitivePace(str, enum.Enum):
    normal = "normal"
    slow = "slow"                  # wolniejsze przetwarzanie
    very_slow = "very_slow"


@dataclass
class SpeechProfile:
    speech_rate: float        # mnożnik tempa (1.0 = normalne; <1 wolniej)
    volume_gain_db: float     # wzmocnienie głośności [dB]
    pause_ms: int             # pauza między zdaniami [ms]
    pitch_shift: float        # przesunięcie tonu (niższy = lepiej słyszalny dla seniorów)
    repeat_key_points: bool   # czy powtarzać kluczowe informacje
    simple_language: bool     # czy upraszczać język

    def to_dict(self) -> dict:
        return asdict(self)

    def describe(self) -> str:
        """Opis do wstrzyknięcia do promptu (F5.speech_profile)."""
        parts = [f"tempo {self.speech_rate:.2f}x", f"pauzy {self.pause_ms}ms"]
        if self.volume_gain_db > 0:
            parts.append(f"głośniej +{self.volume_gain_db:.0f}dB")
        if self.repeat_key_points:
            parts.append("powtarzaj kluczowe informacje")
        if self.simple_language:
            parts.append("bardzo prosty język")
        return ", ".join(parts)


def build_speech_profile(
    hearing: HearingLevel = HearingLevel.normal,
    pace: CognitivePace = CognitivePace.normal,
    age: int | None = None,
) -> SpeechProfile:
    """Buduje profil mowy z jawnych reguł (niedosłuch + tempo + wiek)."""
    # bazowe
    rate = 1.0
    gain = 0.0
    pause = 400
    pitch = 0.0
    repeat = False
    simple = False

    # niedosłuch → głośniej, niższy ton, wolniej
    hearing_gain = {
        HearingLevel.normal: 0.0,
        HearingLevel.mild_loss: 3.0,
        HearingLevel.moderate_loss: 6.0,
        HearingLevel.severe_loss: 9.0,
    }
    gain += hearing_gain[hearing]
    if hearing in (HearingLevel.moderate_loss, HearingLevel.severe_loss):
        rate -= 0.1
        pitch -= 0.1
        repeat = True
    if hearing == HearingLevel.severe_loss:
        rate -= 0.05
        simple = True

    # tempo poznawcze → wolniej, dłuższe pauzy
    if pace == CognitivePace.slow:
        rate -= 0.1
        pause += 200
        repeat = True
    elif pace == CognitivePace.very_slow:
        rate -= 0.2
        pause += 400
        repeat = True
        simple = True

    # wiek 85+ → dodatkowe uproszczenie
    if age is not None and age >= 85:
        simple = True
        pause += 100

    # ograniczenia zakresów (bezpieczeństwo TTS)
    rate = max(0.6, min(1.0, round(rate, 2)))
    gain = max(0.0, min(12.0, gain))
    pause = max(300, min(1500, pause))
    pitch = max(-0.3, min(0.0, round(pitch, 2)))

    return SpeechProfile(
        speech_rate=rate, volume_gain_db=gain, pause_ms=pause,
        pitch_shift=pitch, repeat_key_points=repeat, simple_language=simple,
    )
