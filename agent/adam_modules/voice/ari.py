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
from .watchdog import (
    SilenceWatchdog, SilenceAction, RecordingRegistry, DualStt,
)


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

    ETAP 33 — rozszerzenia sterowane skryptem:
    - element `None` w skrypcie oznacza turę CISZY (senior nie odpowiada) —
      `record_utterance()` zwraca None, ale skrypt się nie kończy (idziemy dalej);
    - `silence_seconds` — czasy ciszy skorelowane z pozycją w skrypcie (dla
      SilenceWatchdog); domyślnie 0 (brak ciszy);
    - `interrupt_at` — zbiór indeksów tur, w których senior przerywa TTS Adama
      (barge-in). `stop()` jest wołane przez CallSession, gdy wykryto przerwanie.
    """
    script: list[str | None] = field(default_factory=list)
    played: list[str] = field(default_factory=list)
    stopped: list[str] = field(default_factory=list)
    hung_up: bool = False
    silence_seconds: list[float] = field(default_factory=list)
    interrupt_at: set[int] = field(default_factory=set)
    _idx: int = 0
    _playing: str | None = None

    def play(self, audio_ref: str) -> None:
        self.played.append(audio_ref)
        self._playing = audio_ref

    def stop(self) -> None:
        """Przerywa bieżące odtwarzanie (barge-in)."""
        if self._playing is not None:
            self.stopped.append(self._playing)
            self._playing = None

    def current_turn_index(self) -> int:
        return self._idx

    def barge_in_now(self) -> bool:
        """Czy senior przerywa TTS w bieżącej turze (indeks kolejnej wypowiedzi)."""
        return self._idx in self.interrupt_at

    def silence_for_turn(self) -> float:
        # _idx wskazuje na NASTĘPNĄ wypowiedź; cisza dotyczy tury właśnie
        # skonsumowanej (_idx-1), gdy record_utterance() zwróciło None.
        i = self._idx - 1
        if 0 <= i < len(self.silence_seconds):
            return self.silence_seconds[i]
        return 0.0

    def record_utterance(self) -> str | None:
        if self._idx >= len(self.script):
            return None
        line = self.script[self._idx]
        self._idx += 1
        if line is None:
            return None  # cisza — brak wypowiedzi w tej turze
        return f"say:{line}"

    def hangup(self) -> None:
        self.hung_up = True


class CallSession:
    """Prowadzi pełną rozmowę na danym kanale przy pomocy DialogEngine.

    ETAP 33 — opcjonalne funkcje głosowe AVA (wszystkie fail-safe, domyślnie
    zgodne wstecz — bez konfiguracji zachowanie jak dotąd):
    - `watchdog`   — SilenceWatchdog: cisza → ponaglenie → eskalacja braku kontaktu;
    - `dual_stt`   — DualStt: drugi niezależny STT + głosy do konsensusu F14;
    - `recordings` — RecordingRegistry: referencje nagrań (RODO, wymaga zgody);
    - barge-in     — jeśli kanał wspiera `stop()` i sygnalizuje `barge_in_now()`,
                     Adam milknie, gdy senior zaczyna mówić.
    """

    def __init__(
        self,
        channel: AriChannel,
        engine: DialogEngine,
        *,
        asr: ASRPort | None = None,
        tts: TTSPort | None = None,
        max_turns: int = 20,
        watchdog: SilenceWatchdog | None = None,
        dual_stt: DualStt | None = None,
        recordings: RecordingRegistry | None = None,
        call_id: str = "call",
    ):
        self.channel = channel
        self.engine = engine
        self.asr = asr or EchoASR()
        self.tts = tts or TextTTS()
        self.max_turns = max_turns
        self.watchdog = watchdog
        self.dual_stt = dual_stt
        self.recordings = recordings
        self.call_id = call_id
        # telemetria funkcji głosowych (do QA/audytu)
        self.reprompts = 0
        self.barge_ins = 0
        self.stt_disagreements = 0
        self.silence_escalated = False

    def _speak(self, turn) -> None:
        utt = self.tts.synthesize(
            turn.text, rate_wpm=turn.rate_wpm, volume_db=turn.volume_db
        )
        self.channel.play(utt.audio_ref)
        # barge-in: jeśli kanał sygnalizuje, że senior przerywa — milkniemy
        if getattr(self.channel, "barge_in_now", None) and self.channel.barge_in_now():
            stop = getattr(self.channel, "stop", None)
            if callable(stop):
                stop()
                self.barge_ins += 1

    def _transcribe(self, audio_ref: str) -> str:
        """Transkrypcja — dual-STT (jeśli włączony) albo pojedynczy ASR."""
        if self.dual_stt is not None:
            res = self.dual_stt.transcribe(audio_ref)
            if res.disagreement:
                self.stt_disagreements += 1
            return res.text
        return self.asr.transcribe(audio_ref).text

    def _handle_silence(self) -> bool:
        """Obsługuje turę ciszy. Zwraca True, jeśli rozmowę należy zakończyć."""
        if self.watchdog is None:
            return True  # brak watchdoga → cisza = koniec (zgodność wsteczna)
        silence_s = 0.0
        getter = getattr(self.channel, "silence_for_turn", None)
        if callable(getter):
            silence_s = getter()
        event = self.watchdog.observe_silence(silence_s)
        if event.action == SilenceAction.reprompt:
            self.reprompts += 1
            self._speak(self.engine.reprompt_silence())
            return False  # kontynuujemy — dajemy seniorowi kolejną szansę
        if event.action == SilenceAction.escalate:
            self.silence_escalated = True
            self.engine.escalate_no_contact()
            return True
        # wait — czekamy dalej (kolejna tura), ale nie w nieskończoność:
        return False

    def run(self) -> CallOutcome:
        """Uruchamia rozmowę: ujawnienie AI → pętla Q&A → zamknięcie + hangup."""
        from .dialog import DialogState
        # 1) otwarcie — obowiązkowe ujawnienie natury AI
        self._speak(self.engine.open())

        # 2) pętla tur
        consecutive_silence = 0
        for _ in range(self.max_turns):
            audio = self.channel.record_utterance()
            if audio is None:
                # cisza — obsługa przez watchdog (albo koniec, gdy brak watchdoga)
                consecutive_silence += 1
                should_stop = self._handle_silence()
                if should_stop or consecutive_silence > self.max_turns:
                    break
                if self.engine.state == DialogState.ESCALATING:
                    break
                continue
            consecutive_silence = 0
            # nagranie wypowiedzi (jeśli włączone i za zgodą)
            if self.recordings is not None:
                self.recordings.register(self.call_id, audio)
            text = self._transcribe(audio)
            adam_turn = self.engine.handle_user(text)
            self._speak(adam_turn)
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
