"""Warstwa głosowa Adama (ETAP 12).

Orkiestruje rozmowę telefoniczną: ASR (mowa→tekst) → DialogEngine (logika,
detekcja kryzysu, System Prompt, profil mowy) → TTS (tekst→mowa), spięte z
kanałem telefonicznym Asteriska przez ARI.

Porty ASR/LLM/TTS/ARI to `Protocol` — w dev/test używamy implementacji
bez sieci (Echo/Rule/Fake), produkcyjnie (Frankfurt DC) podmieniane na realne
(Whisper/GPT/ElevenLabs/asterisk-ari). DialogEngine jest czystą maszyną stanów
— w pełni testowalną w sandboxie.
"""
from __future__ import annotations

from .ports import (
    ASRPort, LLMPort, TTSPort,
    Transcript, LLMReply, LLMClassification, Utterance,
    EchoASR, RuleLLM, TextTTS,
)
from .dialog import DialogEngine, DialogState, DialogTurn, CallOutcome, Speaker
from .ari import AriChannel, FakeChannel, CallSession
from .consensus import CrisisConsensus, CrisisVoteResult
from .asterisk import AsteriskAriChannel
from .prod_ports import WhisperASR, OpenAITTS, ElevenLabsTTS, OpenAILLM
from .stasis import (
    StasisApp, CallStartRequest, CallStartResult, VoicePorts,
    build_call_session, originate_call,
)

__all__ = [
    "ASRPort", "LLMPort", "TTSPort",
    "Transcript", "LLMReply", "LLMClassification", "Utterance",
    "EchoASR", "RuleLLM", "TextTTS",
    "DialogEngine", "DialogState", "DialogTurn", "CallOutcome", "Speaker",
    "AriChannel", "FakeChannel", "CallSession",
    "CrisisConsensus", "CrisisVoteResult",
    "AsteriskAriChannel",
    # ETAP 18 — produkcyjne adaptery I/O głosu
    "WhisperASR", "OpenAITTS", "ElevenLabsTTS", "OpenAILLM",
    # ETAP 19 — warstwa zdarzeń ARI (Stasis) + webhook startu połączenia
    "StasisApp", "CallStartRequest", "CallStartResult", "VoicePorts",
    "build_call_session", "originate_call",
]
