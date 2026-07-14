"""DialogEngine — maszyna stanów rozmowy Adama (ETAP 12.2).

Czysta logika (bez sieci): steruje przebiegiem połączenia telefonicznego,
integrując:
- System Prompt (F5, semaphore/prompt.build_system_prompt) + ujawnienie AI (art. 50),
- profil mowy senioralnej (F14, speech.build_speech_profile) → parametry TTS,
- detekcję kryzysu (F3, semaphore.CrisisDetector) na każdej wypowiedzi seniora,
- klasyfikację semafora → decyzja o eskalacji (PURPLE/RED przerywa Q&A).

Silnik jest sterowany turami: `open()` → seria `handle_user(text)` → `close()`.
Warstwa I/O (ASR/TTS/kanał) jest na zewnątrz (patrz ari.CallSession), dzięki
czemu logika jest w 100% testowalna bez audio.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from adam_modules.semaphore.detector import CrisisDetector
from adam_modules.semaphore.models import SemaphoreLevel
from adam_modules.semaphore.prompt import build_system_prompt, AI_ACT_DISCLOSURE
from adam_modules.speech.profile import (
    build_speech_profile, HearingLevel, CognitivePace,
)
from .ports import LLMPort, LLMReply


class DialogState(str, Enum):
    INIT = "init"
    DISCLOSED = "disclosed"     # ujawnienie AI wypowiedziane
    ACTIVE = "active"           # trwa Q&A
    ESCALATING = "escalating"   # wykryto kryzys — przerwanie na rzecz eskalacji
    CLOSED = "closed"


class Speaker(str, Enum):
    ADAM = "adam"
    SENIOR = "senior"


@dataclass
class DialogTurn:
    speaker: Speaker
    text: str
    state: DialogState
    level: SemaphoreLevel = SemaphoreLevel.green
    trigger: str | None = None
    rate_wpm: int = 130
    volume_db: float = 0.0


@dataclass
class CallOutcome:
    senior_external_id: str | None
    turns: list[DialogTurn] = field(default_factory=list)
    max_level: SemaphoreLevel = SemaphoreLevel.green
    top_trigger: str | None = None
    escalated: bool = False
    disclosure_said: bool = False

    def transcript(self) -> str:
        return "\n".join(f"{t.speaker.value}: {t.text}" for t in self.turns)


# porządek poziomów do wyznaczania maksimum
_LEVEL_ORDER = {
    SemaphoreLevel.green: 0,
    SemaphoreLevel.yellow: 1,
    SemaphoreLevel.red: 2,
    SemaphoreLevel.purple: 3,
}


class DialogEngine:
    """Prowadzi pojedynczą rozmowę. Jedna instancja = jedno połączenie."""

    def __init__(
        self,
        llm: LLMPort,
        *,
        senior_name: str | None = None,
        senior_age: int | None = None,
        senior_external_id: str | None = None,
        hearing: HearingLevel = HearingLevel.mild_loss,
        pace: CognitivePace = CognitivePace.normal,
        detector: CrisisDetector | None = None,
    ):
        self.llm = llm
        self.senior_name = senior_name
        self.senior_age = senior_age
        self._detector = detector or CrisisDetector()
        self.state = DialogState.INIT

        # profil mowy (F14) → parametry TTS
        self.profile = build_speech_profile(
            hearing=hearing, pace=pace, age=senior_age or 75,
        )
        # przelicz mnożnik tempa (speech_rate) na przybliżone WPM (baza 140).
        self.rate_wpm = int(round(140 * self.profile.speech_rate))
        self.volume_db = self.profile.volume_gain_db

        # system prompt (F5) — wstrzykiwany do LLM
        self.system_prompt = build_system_prompt(
            senior_name=senior_name,
            senior_age=senior_age,
            speech_profile=self.profile.describe(),
        )
        self._history: list[dict] = []
        self.outcome = CallOutcome(senior_external_id=senior_external_id)

    # ---- pomocnicze ----
    def _adam_turn(self, text: str, *, level=SemaphoreLevel.green, trigger=None) -> DialogTurn:
        turn = DialogTurn(
            speaker=Speaker.ADAM, text=text, state=self.state, level=level,
            trigger=trigger, rate_wpm=self.rate_wpm, volume_db=self.volume_db,
        )
        self.outcome.turns.append(turn)
        self._history.append({"role": "assistant", "content": text})
        return turn

    def _bump_level(self, level: SemaphoreLevel, trigger: str | None):
        if _LEVEL_ORDER[level] > _LEVEL_ORDER[self.outcome.max_level]:
            self.outcome.max_level = level
            self.outcome.top_trigger = trigger

    # ---- API rozmowy ----
    def open(self) -> DialogTurn:
        """Rozpoczyna rozmowę: obowiązkowe ujawnienie natury AI (art. 50)."""
        if self.state != DialogState.INIT:
            raise ValueError("Rozmowa już rozpoczęta.")
        self.state = DialogState.DISCLOSED
        self.outcome.disclosure_said = True
        return self._adam_turn(AI_ACT_DISCLOSURE)

    def handle_user(self, text: str) -> DialogTurn:
        """Przetwarza wypowiedź seniora: detekcja kryzysu → odpowiedź Adama."""
        if self.state in (DialogState.INIT,):
            raise ValueError("Najpierw wywołaj open() (ujawnienie AI).")
        if self.state == DialogState.CLOSED:
            raise ValueError("Rozmowa zakończona.")

        # zapisz turę seniora + detekcja
        detections = self._detector.detect(text=text)
        classification = self._detector.to_classification(detections)
        level = classification.level
        # trigger istotny tylko poza zielonym (zielony = routine_ok)
        trigger = (
            classification.trigger.value
            if level != SemaphoreLevel.green else None
        )
        self._history.append({"role": "user", "content": text})
        self.outcome.turns.append(DialogTurn(
            speaker=Speaker.SENIOR, text=text, state=self.state,
            level=level, trigger=trigger,
        ))
        self._bump_level(level, trigger)

        # kryzys (PURPLE/RED) — przerwij Q&A, przejdź do eskalacji
        if level in (SemaphoreLevel.purple, SemaphoreLevel.red):
            self.state = DialogState.ESCALATING
            self.outcome.escalated = True
            msg = (
                "Słyszę, że dzieje się coś poważnego. Proszę zachować spokój — "
                "już przekazuję pilną informację do zespołu opieki i, jeśli trzeba, "
                "służb ratunkowych. Zostaję z Panem/Panią na linii."
            )
            return self._adam_turn(msg, level=level, trigger=trigger)

        # normalny tok — odpowiedź LLM
        self.state = DialogState.ACTIVE
        reply: LLMReply = self.llm.reply(
            system_prompt=self.system_prompt, history=list(self._history), user_text=text,
        )
        turn = self._adam_turn(reply.text, level=level, trigger=trigger)
        if reply.finished:
            self.state = DialogState.CLOSED
        return turn

    def close(self) -> DialogTurn:
        """Zamyka rozmowę (jeśli nie zamknięta). Pożegnanie Adama."""
        if self.state == DialogState.CLOSED:
            return self.outcome.turns[-1]
        self.state = DialogState.CLOSED
        return self._adam_turn("Dziękuję za rozmowę. Proszę o siebie dbać. Do usłyszenia!")
