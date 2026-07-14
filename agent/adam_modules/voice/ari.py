"""Adapter kanału telefonicznego (ETAP 12.3) — Asterisk ARI + CallSession.

`AriChannel` (Protocol) abstrahuje operacje na kanale (odtwórz audio, nagraj
wypowiedź, rozłącz). W dev/test używamy `FakeChannel` sterowanego skryptem
wypowiedzi seniora — pozwala przejść pełen tor rozmowy bez Asteriska.

`CallSession` spina: kanał → ASR → DialogEngine → TTS → kanał, tura po turze.
Produkcyjnie (Frankfurt DC) `AriChannel` implementuje realne wywołania
Asterisk REST Interface (ari-py / websocket Stasis).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .ports import ASRPort, TTSPort, EchoASR, TextTTS
from .dialog import DialogEngine, CallOutcome, Speaker


class AriChannel(Protocol):
    def play(self, audio_ref: str) -> None: ...             # pragma: no cover
    def record_utterance(self) -> str | None: ...           # pragma: no cover
    def hangup(self) -> None: ...                            # pragma: no cover


@dataclass
class FakeChannel:
    """Kanał testowy: senior „mówi" ze skryptu; odtworzone audio jest logowane.

    `script` — kolejne wypowiedzi seniora. `record_utterance()` zwraca kolejną
    (jako audio_ref 'say:<tekst>' zgodnie z konwencją EchoASR). Po wyczerpaniu
    skryptu zwraca None (koniec mowy → sesja zamyka rozmowę).
    """
    script: list[str] = field(default_factory=list)
    played: list[str] = field(default_factory=list)
    hung_up: bool = False
    _idx: int = 0

    def play(self, audio_ref: str) -> None:
        self.played.append(audio_ref)

    def record_utterance(self) -> str | None:
        if self._idx >= len(self.script):
            return None
        line = self.script[self._idx]
        self._idx += 1
        return f"say:{line}"

    def hangup(self) -> None:
        self.hung_up = True


class CallSession:
    """Prowadzi pełną rozmowę na danym kanale przy pomocy DialogEngine."""

    def __init__(
        self,
        channel: AriChannel,
        engine: DialogEngine,
        *,
        asr: ASRPort | None = None,
        tts: TTSPort | None = None,
        max_turns: int = 20,
    ):
        self.channel = channel
        self.engine = engine
        self.asr = asr or EchoASR()
        self.tts = tts or TextTTS()
        self.max_turns = max_turns

    def _speak(self, turn) -> None:
        utt = self.tts.synthesize(
            turn.text, rate_wpm=turn.rate_wpm, volume_db=turn.volume_db
        )
        self.channel.play(utt.audio_ref)

    def run(self) -> CallOutcome:
        """Uruchamia rozmowę: ujawnienie AI → pętla Q&A → zamknięcie + hangup."""
        # 1) otwarcie — obowiązkowe ujawnienie natury AI
        self._speak(self.engine.open())

        # 2) pętla tur
        for _ in range(self.max_turns):
            audio = self.channel.record_utterance()
            if audio is None:
                break  # senior przestał mówić
            transcript = self.asr.transcribe(audio)
            adam_turn = self.engine.handle_user(transcript.text)
            self._speak(adam_turn)
            from .dialog import DialogState
            if self.engine.state in (DialogState.CLOSED,):
                break
            if self.engine.state == DialogState.ESCALATING:
                # kryzys obsłużony — kończymy tor rozmowy (eskalacja poza kanałem)
                break

        # 3) zamknięcie
        if self.engine.state.value != "closed":
            self._speak(self.engine.close())
        self.channel.hangup()
        return self.engine.outcome
