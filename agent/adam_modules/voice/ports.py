"""Porty warstwy głosowej (ETAP 12.1): ASR / LLM / TTS.

Definicje `Protocol` + implementacje deweloperskie bez sieci:
- EchoASR  — „rozpoznaje" tekst podany wprost (symulacja mowy seniora w testach),
- RuleLLM  — regułowy generator odpowiedzi Adama (empatyczny, deterministyczny),
- TextTTS  — „synteza" zwracająca ten sam tekst + metadane profilu mowy.

Produkcyjnie podmieniane na Whisper/GPT/ElevenLabs (te same sygnatury).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from adam_modules.semaphore.models import SemaphoreLevel, Trigger


# ------------------------------------------------------------------ typy danych

@dataclass
class Transcript:
    text: str
    confidence: float = 1.0
    is_final: bool = True


@dataclass
class LLMReply:
    text: str
    finished: bool = False          # czy Adam uznaje rozmowę za zakończoną
    meta: dict = field(default_factory=dict)


@dataclass
class LLMClassification:
    """Głos klasyfikacyjny LLM dla konsensusu kryzysowego (ETAP 17)."""
    level: SemaphoreLevel
    trigger: Trigger
    confidence: float = 0.7


@dataclass
class Utterance:
    """Wynik TTS gotowy do odtworzenia na kanale."""
    text: str
    audio_ref: str                  # w dev: pseudo-URI; prod: ścieżka pliku audio
    rate_wpm: int = 130
    volume_db: float = 0.0


# ------------------------------------------------------------------ porty

class ASRPort(Protocol):
    def transcribe(self, audio_ref: str) -> Transcript: ...  # pragma: no cover


class LLMPort(Protocol):
    def reply(self, *, system_prompt: str, history: list[dict], user_text: str) -> LLMReply: ...  # pragma: no cover
    # opcjonalny głos klasyfikacyjny do konsensusu kryzysowego (ETAP 17);
    # implementacje bez tej metody degradują konsensus do samego detektora.
    def classify(self, *, text: str) -> LLMClassification | None: ...  # pragma: no cover


class TTSPort(Protocol):
    def synthesize(self, text: str, *, rate_wpm: int = 130, volume_db: float = 0.0) -> Utterance: ...  # pragma: no cover


# ------------------------------------------------------------------ implementacje dev

class EchoASR:
    """ASR dev: `audio_ref` traktuje jako literalny tekst wypowiedzi seniora.

    Konwencja: audio_ref w formie 'say:<tekst>' → transkrypcja '<tekst>'.
    Pozwala testować pełen tor bez plików audio.
    """
    def transcribe(self, audio_ref: str) -> Transcript:
        text = audio_ref
        if audio_ref.startswith("say:"):
            text = audio_ref[4:]
        return Transcript(text=text.strip(), confidence=0.99, is_final=True)


class RuleLLM:
    """Regułowy „mózg" Adama (dev/test) — bez sieci, deterministyczny.

    Rozpoznaje intencje z tekstu seniora i buduje empatyczną odpowiedź.
    Sygnalizuje `finished=True`, gdy senior się żegna.
    """
    _BYE = ("do widzenia", "żegnam", "pa pa", "koniec", "dziękuję, to wszystko")
    _GOOD = ("dobrze", "w porządku", "świetnie", "czuję się dobrze", "wszystko ok")
    _MEDS = ("lek", "tabletk", "leki", "lekarstw")

    # Heurystyki klasyfikacyjne LLM — CELOWO niezależne od słownika detektora F3,
    # by konsensus miał realną wartość (dwa różne spojrzenia). LLM potrafi
    # „podnieść" czujność na niuanse opisowe, których reguła nie łapie dosłownie.
    _LLM_PURPLE = ("nie chcę żyć", "chcę umrzeć", "tracę przytomność", "zasłabł",
                   "krew leci", "krwawię", "nie oddycha", "zawał")
    _LLM_RED = ("okropnie boli", "przewróciłam", "przewróciłem", "upadłam", "upadłem",
                "gorączka", "zawroty głowy", "nie mam siły wstać")
    _LLM_YELLOW = ("smutno", "samotn", "nie spałam", "nie spałem", "zapomniałam wziąć",
                   "zapomniałem wziąć", "gorszy dzień", "martwię się")

    def reply(self, *, system_prompt: str, history: list[dict], user_text: str) -> LLMReply:
        t = (user_text or "").lower()
        if any(b in t for b in self._BYE):
            return LLMReply(text="Dziękuję za rozmowę. Życzę spokojnego dnia. Do usłyszenia!",
                            finished=True, meta={"intent": "farewell"})
        if any(g in t for g in self._GOOD):
            return LLMReply(text="Bardzo się cieszę, że czuje się Pan/Pani dobrze. "
                                 "Czy pamiętał/a Pan/Pani o dzisiejszych lekach?",
                            meta={"intent": "wellbeing_ok"})
        if any(m in t for m in self._MEDS):
            return LLMReply(text="To ważne, żeby przyjmować leki regularnie. "
                                 "Zapiszę, że o tym rozmawialiśmy. Czy coś jeszcze Pana/Panią martwi?",
                            meta={"intent": "medication"})
        if not t:
            return LLMReply(text="Nie usłyszałem odpowiedzi. Czy mnie Pan/Pani słyszy?",
                            meta={"intent": "reprompt"})
        # domyślna, empatyczna kontynuacja
        return LLMReply(text="Rozumiem. Proszę mi powiedzieć, jak Pan/Pani się dziś czuje?",
                        meta={"intent": "followup"})

    def classify(self, *, text: str) -> LLMClassification | None:
        """Niezależny głos klasyfikacyjny do konsensusu (ETAP 17).

        Zwraca poziom + trigger na podstawie własnych heurystyk. Zielony
        oznacza „brak sygnału" — konsensus i tak zabezpiecza fail-safe.
        """
        t = (text or "").lower()
        if any(p in t for p in self._LLM_PURPLE):
            return LLMClassification(SemaphoreLevel.purple, Trigger.suicide_ideation
                                     if ("żyć" in t or "umrzeć" in t) else Trigger.unconscious,
                                     confidence=0.6)
        if any(p in t for p in self._LLM_RED):
            return LLMClassification(SemaphoreLevel.red, Trigger.persistent_pain, confidence=0.6)
        if any(p in t for p in self._LLM_YELLOW):
            return LLMClassification(SemaphoreLevel.yellow, Trigger.mood_low, confidence=0.6)
        return LLMClassification(SemaphoreLevel.green, Trigger.routine_ok, confidence=0.8)


class TextTTS:
    """TTS dev: zwraca pseudo-audio (URI tekstowe) z parametrami profilu mowy."""
    def synthesize(self, text: str, *, rate_wpm: int = 130, volume_db: float = 0.0) -> Utterance:
        ref = "tts:" + text.replace("\n", " ")[:64]
        return Utterance(text=text, audio_ref=ref, rate_wpm=rate_wpm, volume_db=volume_db)
