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
from typing import Callable

from adam_modules.semaphore.detector import CrisisDetector
from adam_modules.semaphore.models import SemaphoreLevel
from adam_modules.semaphore.prompt import build_system_prompt, AI_ACT_DISCLOSURE
from adam_modules.semaphore.io_guards import (
    InputGuard, OutputGuard, GuardAction,
    SAFE_INJECTION_REPLACEMENT,
)
from adam_modules.speech.profile import (
    build_speech_profile, HearingLevel, CognitivePace,
)
from .ports import LLMPort, LLMReply
from .consensus import CrisisConsensus


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
class DecisionEvent:
    """Ślad decyzji konsensusu na turze seniora (F14/F16, ETAP 30).

    Emitowany przez DialogEngine na każdej ocenionej wypowiedzi. Caller (warstwa
    I/O / API) może go utrwalić przez QAService.record_decision i — dla ESCALATE
    — wywołać EmergencyService.dispatch. Silnik pozostaje bez zależności od DB.
    """
    decision: str                       # EXECUTE/DEFER/ESCALATE/ABSTAIN (wartość ConsensusDecision)
    level: str                          # kolor semafora
    trigger: str | None = None
    confidence: float | None = None
    needs_review: bool = False
    text: str = ""                      # oryginalna wypowiedź seniora (do telemetrii/nastroju)


@dataclass
class CallOutcome:
    senior_external_id: str | None
    turns: list[DialogTurn] = field(default_factory=list)
    max_level: SemaphoreLevel = SemaphoreLevel.green
    top_trigger: str | None = None
    escalated: bool = False
    disclosure_said: bool = False
    needs_review: bool = False          # konsensus F16 zgłosił rozbieżność/braki (ETAP 17)
    guard_flags: list[str] = field(default_factory=list)  # F4 (ETAP 24): zdarzenia guardrails I/O
    decisions: list[DecisionEvent] = field(default_factory=list)  # F16 (ETAP 30): telemetria decyzji
    silence_reprompts: int = 0          # ETAP 33: liczba ponagleń przy ciszy
    no_contact: bool = False            # ETAP 33: eskalacja braku kontaktu (cisza)

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
        use_consensus: bool = True,
        memory_context: str | None = None,
        regional_dialect: bool = False,
        on_decision: Callable[[DecisionEvent], None] | None = None,
    ):
        self.llm = llm
        self.senior_name = senior_name
        self.senior_age = senior_age
        # F13 (ETAP 29): regional_dialect=True → detektor rozumie gwarę wielkopolską.
        self._detector = detector or CrisisDetector(regional=regional_dialect)
        # Konsensus kryzysowy (ETAP 17): detektor regułowy + głos LLM → fail-safe.
        # Gdy wyłączony, spadamy do samego detektora (zachowanie z ETAP 12).
        self._use_consensus = use_consensus
        self._consensus = CrisisConsensus(
            llm, detector=self._detector, use_llm=use_consensus,
        )
        self.state = DialogState.INIT
        # F16 (ETAP 30): hook telemetrii decyzji — caller utrwala/dispatch 112.
        self._on_decision = on_decision

        # profil mowy (F14) → parametry TTS
        self.profile = build_speech_profile(
            hearing=hearing, pace=pace, age=senior_age or 75,
        )
        # przelicz mnożnik tempa (speech_rate) na przybliżone WPM (baza 140).
        self.rate_wpm = int(round(140 * self.profile.speech_rate))
        self.volume_db = self.profile.volume_gain_db

        # system prompt (F5) — wstrzykiwany do LLM
        # F7 (ETAP 28): ciągłość pamięci — kontekst „z poprzednich rozmów"
        # budowany przez MemoryService.continuity_context i podany przez wołającego.
        self.memory_context = memory_context
        self.system_prompt = build_system_prompt(
            senior_name=senior_name,
            senior_age=senior_age,
            speech_profile=self.profile.describe(),
            extra_context=memory_context,
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

        # F4 (ETAP 24) — WARSTWA 1: input guard (pre-LLM).
        # Detekcja kryzysu działa na ORYGINALNYM tekście (maskowanie PII nie może
        # ukryć wołania o pomoc), ale do LLM trafia tekst zsanityzowany.
        in_guard = InputGuard.sanitize(text)
        if in_guard.flags:
            self.outcome.guard_flags.extend(f"in:{f}" for f in in_guard.flags)
        llm_input_text = in_guard.text

        # zapisz turę seniora + ocena kryzysu
        decision_str = "EXECUTE"
        confidence: float | None = None
        needs_review = False
        if self._use_consensus:
            assessment = self._consensus.assess(text)
            level = assessment.level
            trigger_enum = assessment.trigger
            decision_str = assessment.decision.value
            confidence = assessment.confidence
            needs_review = assessment.needs_review
            if assessment.needs_review:
                self.outcome.needs_review = True
        else:
            detections = self._detector.detect(text=text)
            classification = self._detector.to_classification(detections)
            level = classification.level
            trigger_enum = classification.trigger
            confidence = getattr(classification, "confidence", None)
        # trigger istotny tylko poza zielonym (zielony = routine_ok)
        trigger = trigger_enum.value if level != SemaphoreLevel.green else None

        # F16 (ETAP 30) — telemetria decyzji: emitujemy zdarzenie i (opcjonalnie)
        # przekazujemy je do callera (QAService.record_decision + dispatch 112).
        event = DecisionEvent(
            decision=decision_str, level=level.value, trigger=trigger,
            confidence=confidence, needs_review=needs_review, text=text,
        )
        self.outcome.decisions.append(event)
        if self._on_decision is not None:
            self._on_decision(event)
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

        # normalny tok
        self.state = DialogState.ACTIVE

        # F4 — jeśli wykryto próbę manipulacji (prompt-injection), NIE wołamy LLM:
        # odpowiadamy bezpiecznie i zgodnie z rolą (fail-safe), by nie dać się „przełamać".
        if in_guard.injection_detected:
            turn = self._adam_turn(SAFE_INJECTION_REPLACEMENT, level=level, trigger=trigger)
            return turn

        reply: LLMReply = self.llm.reply(
            system_prompt=self.system_prompt, history=list(self._history),
            user_text=llm_input_text,
        )

        # F4 (ETAP 24) — WARSTWA 3: output guard (post-LLM).
        out_guard = OutputGuard.review(reply.text)
        if out_guard.action == GuardAction.BLOCKED:
            self.outcome.guard_flags.extend(f"out:{f}" for f in out_guard.flags)
            # nadpisujemy niebezpieczną treść bezpiecznym zamiennikiem
            turn = self._adam_turn(out_guard.text, level=level, trigger=trigger)
            return turn

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

    # ---- ETAP 33: funkcje głosowe AVA (cisza → ponaglenie → eskalacja) ----
    def reprompt_silence(self) -> DialogTurn:
        """Ponaglenie po wydłużonej ciszy seniora (Silence Watchdog).

        Nie zmienia stanu rozmowy — Adam delikatnie sprawdza kontakt i słucha
        dalej. Zliczane w `outcome.silence_reprompts` (telemetria QA/audyt).
        """
        if self.state == DialogState.CLOSED:
            raise ValueError("Rozmowa zakończona.")
        self.outcome.silence_reprompts += 1
        return self._adam_turn(
            "Czy mnie Pan/Pani słyszy? Jestem tutaj i słucham — proszę śmiało mówić."
        )

    def escalate_no_contact(self) -> DialogTurn:
        """Brak kontaktu utrzymuje się mimo ponagleń — eskalacja braku kontaktu.

        Przechodzi w stan ESCALATING i oznacza `no_contact=True` oraz
        `escalated=True` (rodzina/opiekun zostaną powiadomieni poza kanałem).
        Fail-safe: przedłużona cisza u seniora traktowana jest jako sygnał ryzyka.
        """
        self.state = DialogState.ESCALATING
        self.outcome.escalated = True
        self.outcome.no_contact = True
        return self._adam_turn(
            "Nie mogę się z Panem/Panią skontaktować. Dla bezpieczeństwa powiadomię "
            "bliską osobę. Proszę się nie martwić — pomoc jest w drodze.",
            level=SemaphoreLevel.yellow,
        )
