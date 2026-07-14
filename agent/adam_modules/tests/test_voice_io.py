"""Testy produkcyjnych adapterów I/O głosu (ETAP 18).

Wszystko offline — httpx jest fałszywy (wstrzykiwany). Weryfikujemy:
- WhisperASR: happy-path, brak audio, fail-safe, no-op bez klucza,
- OpenAITTS / ElevenLabsTTS: sink→sound URI, degradacja bez klucza, fail-safe,
- OpenAILLM: reply happy-path + fail-safe, classify JSON + fail-safe + no-op,
- zgodność z konsensusem (classify daje głos LLMClassification).
"""
from __future__ import annotations

import json

import pytest

from adam_modules.voice.prod_ports import (
    WhisperASR, OpenAITTS, ElevenLabsTTS, OpenAILLM,
)
from adam_modules.voice.ports import Transcript, LLMClassification
from adam_modules.semaphore.models import SemaphoreLevel


# ------------------------------------------------------------------ fake httpx

class FakeResp:
    def __init__(self, *, json_data=None, content=b""):
        self._json = json_data
        self.content = content

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json


class FakeClient:
    """Zapamiętuje wywołania i zwraca zaplanowaną odpowiedź (lub rzuca)."""
    def __init__(self, resp=None, raise_exc=None):
        self.resp = resp
        self.raise_exc = raise_exc
        self.calls = []

    def post(self, url, **kw):
        self.calls.append((url, kw))
        if self.raise_exc:
            raise self.raise_exc
        return self.resp


# ================================================================== WhisperASR

def test_whisper_happy_path():
    client = FakeClient(resp=FakeResp(json_data={"text": "  Dzień dobry Adam  "}))
    asr = WhisperASR(api_key="k", http_client=client, audio_loader=lambda ref: b"AUDIO")
    t = asr.transcribe("record:x")
    assert isinstance(t, Transcript)
    assert t.text == "Dzień dobry Adam"
    assert t.confidence > 0
    # trafił do endpointu transkrypcji
    assert client.calls[0][0].endswith("/audio/transcriptions")


def test_whisper_no_audio_returns_empty():
    client = FakeClient(resp=FakeResp(json_data={"text": "x"}))
    asr = WhisperASR(api_key="k", http_client=client, audio_loader=lambda ref: None)
    t = asr.transcribe("record:x")
    assert t.text == "" and t.confidence == 0.0


def test_whisper_fail_safe_on_error():
    client = FakeClient(raise_exc=RuntimeError("net down"))
    asr = WhisperASR(api_key="k", http_client=client, audio_loader=lambda ref: b"A")
    t = asr.transcribe("record:x")
    assert t.text == "" and t.is_final is True  # nie rzuca


def test_whisper_noop_without_key():
    asr = WhisperASR(api_key="", http_client=None)
    t = asr.transcribe("record:x")
    assert t.text == "" and t.confidence == 0.0


# ================================================================== OpenAITTS

def test_openai_tts_uses_sink_media_uri():
    client = FakeClient(resp=FakeResp(content=b"WAVDATA"))
    seen = {}
    def sink(name, audio):
        seen["name"], seen["audio"] = name, audio
        return f"sound:{name}"
    tts = OpenAITTS(api_key="k", http_client=client, audio_sink=sink)
    u = tts.synthesize("Dzień dobry")
    assert u.audio_ref.startswith("sound:adam-tts-")
    assert seen["audio"] == b"WAVDATA"
    assert client.calls[0][0].endswith("/audio/speech")


def test_openai_tts_degrades_without_key():
    tts = OpenAITTS(api_key="", http_client=None, audio_sink=None)
    u = tts.synthesize("Halo")
    assert u.audio_ref.startswith("tts:")   # degradacja do referencji tekstowej


def test_openai_tts_fail_safe():
    client = FakeClient(raise_exc=RuntimeError("boom"))
    tts = OpenAITTS(api_key="k", http_client=client, audio_sink=lambda n, a: f"sound:{n}")
    u = tts.synthesize("Halo")
    assert u.audio_ref.startswith("tts:")   # fail-safe → fallback


# ================================================================== ElevenLabsTTS

def test_elevenlabs_uses_sink():
    client = FakeClient(resp=FakeResp(content=b"WAV"))
    tts = ElevenLabsTTS(api_key="k", voice_id="v1", http_client=client,
                        audio_sink=lambda n, a: f"sound:{n}")
    u = tts.synthesize("Cześć")
    assert u.audio_ref.startswith("sound:adam-11l-")
    assert "/text-to-speech/v1" in client.calls[0][0]


def test_elevenlabs_degrades_without_voice():
    tts = ElevenLabsTTS(api_key="k", voice_id="", http_client=None, audio_sink=None)
    u = tts.synthesize("Cześć")
    assert u.audio_ref.startswith("tts:")


# ================================================================== OpenAILLM

def _chat_resp(content):
    return FakeResp(json_data={"choices": [{"message": {"content": content}}]})


def test_openai_llm_reply_happy_path():
    client = FakeClient(resp=_chat_resp("Miło Pana słyszeć, jak się Pan czuje?"))
    llm = OpenAILLM(api_key="k", http_client=client)
    r = llm.reply(system_prompt="Jesteś Adam", history=[], user_text="Dzień dobry")
    assert "Pana" in r.text
    assert r.meta["source"] == "openai"


def test_openai_llm_reply_detects_farewell_finished():
    client = FakeClient(resp=_chat_resp("Dziękuję, do usłyszenia i spokojnego dnia."))
    llm = OpenAILLM(api_key="k", http_client=client)
    r = llm.reply(system_prompt="s", history=[], user_text="pa")
    assert r.finished is True


def test_openai_llm_reply_fail_safe():
    client = FakeClient(raise_exc=RuntimeError("timeout"))
    llm = OpenAILLM(api_key="k", http_client=client)
    r = llm.reply(system_prompt="s", history=[], user_text="x")
    assert r.text  # neutralna, nie rzuca
    assert r.meta["source"] == "error"


def test_openai_llm_reply_noop_without_key():
    llm = OpenAILLM(api_key="", http_client=None)
    r = llm.reply(system_prompt="s", history=[], user_text="x")
    assert r.meta["source"] == "no-op"


def test_openai_llm_classify_json():
    payload = json.dumps({"level": "purple", "trigger": "suicide_ideation", "confidence": 0.9})
    client = FakeClient(resp=_chat_resp(payload))
    llm = OpenAILLM(api_key="k", http_client=client)
    c = llm.classify(text="Nie chcę już żyć")
    assert isinstance(c, LLMClassification)
    assert c.level == SemaphoreLevel.purple
    assert c.confidence == 0.9
    # wymusił tryb JSON
    assert client.calls[0][1]["json"]["response_format"] == {"type": "json_object"}


def test_openai_llm_classify_fail_safe_returns_none():
    client = FakeClient(resp=_chat_resp("to nie jest json"))
    llm = OpenAILLM(api_key="k", http_client=client)
    assert llm.classify(text="cokolwiek") is None


def test_openai_llm_classify_noop_without_key():
    llm = OpenAILLM(api_key="", http_client=None)
    assert llm.classify(text="cokolwiek") is None


def test_openai_llm_classify_clamps_confidence():
    payload = json.dumps({"level": "red", "trigger": "persistent_pain", "confidence": 5.0})
    client = FakeClient(resp=_chat_resp(payload))
    llm = OpenAILLM(api_key="k", http_client=client)
    c = llm.classify(text="Strasznie boli")
    assert c.level == SemaphoreLevel.red
    assert c.confidence == 1.0  # przycięte do [0,1]
