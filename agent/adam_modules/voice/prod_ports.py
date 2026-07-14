"""Produkcyjne adaptery portów głosowych (ETAP 18).

Podmiany deweloperskich portów (`EchoASR`/`RuleLLM`/`TextTTS`) na realnych
dostawców, z zachowaniem tych samych sygnatur (`ASRPort`/`LLMPort`/`TTSPort`):

- `WhisperASR`      — STT przez OpenAI Whisper (`/v1/audio/transcriptions`),
- `OpenAITTS`       — synteza mowy przez OpenAI (`/v1/audio/speech`),
- `ElevenLabsTTS`   — synteza mowy przez ElevenLabs (`/v1/text-to-speech/{voice}`),
- `OpenAILLM`       — „mózg" Adama (chat) + głos klasyfikacyjny do konsensusu.

Zasady (spójne z `asterisk.py`):
- **Sieć tylko na brzegach** — klient HTTP (`httpx`) jest wstrzykiwany; logika
  rozmowy pozostaje testowalna offline.
- **Fail-safe** — każdy błąd sieci/dostawcy jest łapany; adapter zwraca wartość
  bezpieczną (pusta transkrypcja, degradacja TTS do referencji tekstowej,
  neutralna odpowiedź LLM, `classify()=None`). Rozmowa nigdy nie „wywala się".
- **No-op bez klucza** — bez klucza API adapter loguje ostrzeżenie i degraduje
  do zachowania zastępczego; nigdy nie rzuca przy konstrukcji.

Realny LLM zachowuje konsensus kryzysowy: `classify()` daje niezależny głos,
który `CrisisConsensus` (ETAP 17) łączy z detektorem F3 (fail-safe: wyższy
poziom + needs_review).
"""
from __future__ import annotations

import json
import logging
import os

from adam_modules.semaphore.models import SemaphoreLevel, Trigger
from .ports import Transcript, LLMReply, LLMClassification, Utterance

logger = logging.getLogger("adam.voice.prod")


# ==================================================================== ASR

class WhisperASR:
    """STT przez OpenAI Whisper. Implementuje `ASRPort`.

    `audio_ref` w produkcji to `record:<name>` (z Asteriska) lub ścieżka pliku.
    Sieć odbywa się przez wstrzyknięty `http_client` (httpx-zgodny). Bez klucza
    lub bez klienta → transkrypcja pusta (fail-safe; sesja domyka rozmowę).
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "whisper-1",
        http_client=None,
        audio_loader=None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model
        self._client = http_client
        # audio_loader(audio_ref) -> bytes | None ; wstrzykiwany (Asterisk/plik)
        self._load = audio_loader
        if not self.api_key:
            logger.warning("WhisperASR bez OPENAI_API_KEY — tryb no-op (pusta transkrypcja)")

    def _ready(self) -> bool:
        return bool(self.api_key and self._client is not None)

    def transcribe(self, audio_ref: str) -> Transcript:
        if not self._ready():
            logger.info("[no-op] whisper transcribe ref=%s", audio_ref)
            return Transcript(text="", confidence=0.0, is_final=True)
        try:
            audio = self._load(audio_ref) if self._load else None
            if not audio:
                logger.warning("WhisperASR: brak danych audio dla ref=%s", audio_ref)
                return Transcript(text="", confidence=0.0, is_final=True)
            resp = self._client.post(
                f"{self.base_url}/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                data={"model": self.model, "language": "pl"},
                files={"file": ("utterance.wav", audio, "audio/wav")},
            )
            data = _json(resp)
            text = (data.get("text") or "").strip()
            return Transcript(text=text, confidence=0.9 if text else 0.0, is_final=True)
        except Exception as exc:  # fail-safe
            logger.warning("WhisperASR error ref=%s err=%s", audio_ref, exc)
            return Transcript(text="", confidence=0.0, is_final=True)


# ==================================================================== TTS

class OpenAITTS:
    """Synteza mowy przez OpenAI (`/v1/audio/speech`). Implementuje `TTSPort`.

    Zwraca `Utterance` z `audio_ref='sound:<...>'`, gdy synteza się powiedzie i
    zostanie zapisana przez wstrzyknięty `audio_sink`. Bez klucza/klienta → dev
    degradacja do referencji tekstowej `tts:<...>` (spójne z Asterisk `_to_media_uri`).
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4o-mini-tts",
        voice: str = "alloy",
        http_client=None,
        audio_sink=None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model
        self.voice = voice
        self._client = http_client
        # audio_sink(name, bytes) -> str (media uri, np. 'sound:<name>'); wstrzykiwany
        self._sink = audio_sink
        self._seq = 0
        if not self.api_key:
            logger.warning("OpenAITTS bez OPENAI_API_KEY — degradacja do referencji tekstowej")

    def _ready(self) -> bool:
        return bool(self.api_key and self._client is not None and self._sink is not None)

    def synthesize(self, text: str, *, rate_wpm: int = 130, volume_db: float = 0.0) -> Utterance:
        fallback_ref = "tts:" + text.replace("\n", " ")[:64]
        if not self._ready():
            return Utterance(text=text, audio_ref=fallback_ref, rate_wpm=rate_wpm, volume_db=volume_db)
        try:
            self._seq += 1
            resp = self._client.post(
                f"{self.base_url}/audio/speech",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "voice": self.voice, "input": text, "format": "wav"},
            )
            audio = _content(resp)
            name = f"adam-tts-{self._seq}"
            media = self._sink(name, audio) or fallback_ref
            return Utterance(text=text, audio_ref=media, rate_wpm=rate_wpm, volume_db=volume_db)
        except Exception as exc:  # fail-safe
            logger.warning("OpenAITTS error err=%s", exc)
            return Utterance(text=text, audio_ref=fallback_ref, rate_wpm=rate_wpm, volume_db=volume_db)


class ElevenLabsTTS:
    """Synteza mowy przez ElevenLabs (`/v1/text-to-speech/{voice_id}`)."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        voice_id: str | None = None,
        model_id: str = "eleven_multilingual_v2",
        http_client=None,
        audio_sink=None,
    ):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.base_url = (base_url or os.getenv("ELEVENLABS_BASE_URL", "https://api.elevenlabs.io/v1")).rstrip("/")
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "")
        self.model_id = model_id
        self._client = http_client
        self._sink = audio_sink
        self._seq = 0
        if not self.api_key or not self.voice_id:
            logger.warning("ElevenLabsTTS bez klucza/voice_id — degradacja do referencji tekstowej")

    def _ready(self) -> bool:
        return bool(self.api_key and self.voice_id and self._client is not None and self._sink is not None)

    def synthesize(self, text: str, *, rate_wpm: int = 130, volume_db: float = 0.0) -> Utterance:
        fallback_ref = "tts:" + text.replace("\n", " ")[:64]
        if not self._ready():
            return Utterance(text=text, audio_ref=fallback_ref, rate_wpm=rate_wpm, volume_db=volume_db)
        try:
            self._seq += 1
            resp = self._client.post(
                f"{self.base_url}/text-to-speech/{self.voice_id}",
                headers={"xi-api-key": self.api_key, "Accept": "audio/wav"},
                json={"text": text, "model_id": self.model_id},
            )
            audio = _content(resp)
            name = f"adam-11l-{self._seq}"
            media = self._sink(name, audio) or fallback_ref
            return Utterance(text=text, audio_ref=media, rate_wpm=rate_wpm, volume_db=volume_db)
        except Exception as exc:  # fail-safe
            logger.warning("ElevenLabsTTS error err=%s", exc)
            return Utterance(text=text, audio_ref=fallback_ref, rate_wpm=rate_wpm, volume_db=volume_db)


# ==================================================================== LLM

class OpenAILLM:
    """Produkcyjny „mózg" Adama przez OpenAI Chat Completions. Implementuje `LLMPort`.

    - `reply()` buduje empatyczną odpowiedź Adama z system_prompt + historii.
    - `classify()` daje NIEZALEŻNY głos klasyfikacyjny do konsensusu kryzysowego
      (ETAP 17), poprzez wymuszenie odpowiedzi JSON o poziomie semafora.

    Fail-safe: błąd/brak klucza → `reply()` zwraca neutralną, bezpieczną kontynuację;
    `classify()` zwraca None (konsensus degraduje do samego detektora F3).
    """

    _NEUTRAL = "Rozumiem. Proszę mi powiedzieć, jak Pan/Pani się dziś czuje?"

    _LEVELS = {
        "green": SemaphoreLevel.green, "yellow": SemaphoreLevel.yellow,
        "red": SemaphoreLevel.red, "purple": SemaphoreLevel.purple,
    }
    _TRIGGERS = {
        "suicide_ideation": Trigger.suicide_ideation, "unconscious": Trigger.unconscious,
        "persistent_pain": Trigger.persistent_pain, "mood_low": Trigger.mood_low,
        "routine_ok": Trigger.routine_ok,
    }

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4o-mini",
        http_client=None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model
        self._client = http_client
        if not self.api_key:
            logger.warning("OpenAILLM bez OPENAI_API_KEY — odpowiedzi neutralne, classify=None")

    def _ready(self) -> bool:
        return bool(self.api_key and self._client is not None)

    def _chat(self, messages: list[dict], *, temperature: float = 0.6, json_mode: bool = False) -> str:
        payload = {"model": self.model, "messages": messages, "temperature": temperature}
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        resp = self._client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
        )
        data = _json(resp)
        return (data["choices"][0]["message"]["content"] or "").strip()

    def reply(self, *, system_prompt: str, history: list[dict], user_text: str) -> LLMReply:
        if not self._ready():
            return LLMReply(text=self._NEUTRAL, meta={"intent": "neutral_fallback", "source": "no-op"})
        try:
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history or [])
            messages.append({"role": "user", "content": user_text or ""})
            text = self._chat(messages) or self._NEUTRAL
            finished = any(b in text.lower() for b in ("do usłyszenia", "do widzenia", "spokojnego dnia"))
            return LLMReply(text=text, finished=finished, meta={"intent": "llm", "source": "openai"})
        except Exception as exc:  # fail-safe
            logger.warning("OpenAILLM reply error err=%s", exc)
            return LLMReply(text=self._NEUTRAL, meta={"intent": "neutral_fallback", "source": "error"})

    def classify(self, *, text: str) -> LLMClassification | None:
        if not self._ready():
            return None
        try:
            sys = (
                "Jesteś klasyfikatorem bezpieczeństwa dla asystenta seniorów. "
                "Oceń wypowiedź i zwróć WYŁĄCZNIE JSON: "
                '{"level":"green|yellow|red|purple","trigger":'
                '"routine_ok|mood_low|persistent_pain|unconscious|suicide_ideation",'
                '"confidence":0.0-1.0}. '
                "purple = zagrożenie życia (myśli samobójcze, utrata przytomności, krwotok). "
                "red = poważny ból/upadek/gorączka. yellow = obniżony nastrój/samotność. "
                "green = wszystko w porządku."
            )
            raw = self._chat(
                [{"role": "system", "content": sys}, {"role": "user", "content": text or ""}],
                temperature=0.0, json_mode=True,
            )
            data = json.loads(raw)
            level = self._LEVELS.get(str(data.get("level", "green")).lower(), SemaphoreLevel.green)
            trigger = self._TRIGGERS.get(str(data.get("trigger", "routine_ok")).lower(), Trigger.routine_ok)
            conf = float(data.get("confidence", 0.6))
            conf = min(1.0, max(0.0, conf))
            return LLMClassification(level, trigger, confidence=conf)
        except Exception as exc:  # fail-safe → detektor F3 sam decyduje
            logger.warning("OpenAILLM classify error err=%s", exc)
            return None


# ==================================================================== helpery

def _json(resp):
    """Odczyt JSON z odpowiedzi httpx-zgodnej (obsługa .json() lub .text)."""
    if hasattr(resp, "json"):
        return resp.json()
    return json.loads(getattr(resp, "text", "{}"))


def _content(resp) -> bytes:
    """Odczyt bajtów z odpowiedzi (audio)."""
    if hasattr(resp, "content"):
        c = resp.content
        return c if isinstance(c, (bytes, bytearray)) else bytes(c)
    return b""
