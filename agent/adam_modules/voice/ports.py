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


class TextTTS:
    """TTS dev: zwraca pseudo-audio (URI tekstowe) z parametrami profilu mowy."""
    def synthesize(self, text: str, *, rate_wpm: int = 130, volume_db: float = 0.0) -> Utterance:
        ref = "tts:" + text.replace("\n", " ")[:64]
        return Utterance(text=text, audio_ref=ref, rate_wpm=rate_wpm, volume_db=volume_db)
