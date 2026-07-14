"""Funkcje głosowe AVA (ETAP 33) — Silence Watchdog, barge-in, nagrania, dual-STT.

Warstwa czysta (bez sieci) — wszystkie sygnały czasu/audio są wstrzykiwane,
dzięki czemu całość jest deterministycznie testowalna w sandboxie. Produkcyjnie
(Frankfurt DC) sygnały pochodzą z Asterisk/ARI (VAD, DTMF, energia ramki), a
drugi STT z niezależnego dostawcy (np. Deepgram obok Whispera).

Składniki:
- `SilenceWatchdog`  — wykrywa przedłużającą się ciszę seniora podczas rozmowy
  (brak reakcji → ponaglenie → eskalacja braku kontaktu). Kluczowe dla seniorów,
  którzy mogli zasłabnąć / odłożyć słuchawkę / nie usłyszeć.
- `BargeInController` — pozwala przerwać TTS Adama, gdy senior zaczyna mówić
  (naturalna rozmowa; senior nie musi czekać, aż Adam skończy zdanie).
- `RecordingRegistry` — rejestr referencji nagrań połączenia (audit / QA / RODO),
  z jawną zgodą na nagrywanie (fail-safe: brak zgody → brak nagrania).
- `DualStt` — łączy dwa niezależne silniki ASR i buduje głosy do konsensusu F14
  (stt_primary + stt_secondary); przy rozbieżności zaznacza `disagreement`.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Callable

from adam_modules.consensus.engine import ModelVote, VoterRole
from adam_modules.semaphore.detector import CrisisDetector
from .ports import ASRPort, Transcript


# ==================================================================
# 1) Silence Watchdog — przedłużająca się cisza
# ==================================================================

class SilenceAction(str, enum.Enum):
    """Decyzja watchdoga po kolejnym okresie ciszy."""
    wait = "wait"           # cisza w normie — czekamy dalej
    reprompt = "reprompt"   # ponaglenie („Czy mnie Pan/Pani słyszy?")
    escalate = "escalate"   # brak kontaktu utrzymuje się — eskalacja braku kontaktu


@dataclass
class SilenceConfig:
    """Progi ciszy dobrane pod seniorów (wolniejsza reakcja to norma)."""
    # dopuszczalna cisza zanim w ogóle reagujemy (senior myśli / szuka słów)
    grace_s: float = 6.0
    # kolejny próg — ponaglenie
    reprompt_s: float = 10.0
    # ile ponagleń zanim uznamy brak kontaktu za sytuację do eskalacji
    max_reprompts: int = 2
    # twardy próg pojedynczej ciszy, po którym eskalujemy natychmiast
    hard_silence_s: float = 30.0


@dataclass
class SilenceEvent:
    action: SilenceAction
    silence_s: float
    reprompts_so_far: int
    reason: str


class SilenceWatchdog:
    """Śledzi ciszę seniora i decyduje: czekać / ponaglić / eskalować.

    Model użycia (pętla rozmowy): po każdej turze, jeśli senior NIE odpowiedział
    w oknie nasłuchu, wołamy `observe_silence(silence_s)`. Gdy odpowie —
    `reset()`. Watchdog jest bezstanowy względem zegara (czas wstrzykiwany),
    więc testy są deterministyczne.
    """

    def __init__(self, config: SilenceConfig | None = None):
        self.config = config or SilenceConfig()
        self._reprompts = 0
        self._escalated = False

    @property
    def reprompts(self) -> int:
        return self._reprompts

    @property
    def escalated(self) -> bool:
        return self._escalated

    def reset(self) -> None:
        """Senior się odezwał — kasujemy licznik ponagleń."""
        self._reprompts = 0

    def observe_silence(self, silence_s: float) -> SilenceEvent:
        """Ocenia bieżący okres ciszy i zwraca decyzję."""
        cfg = self.config
        # twardy próg — natychmiastowa eskalacja braku kontaktu
        if silence_s >= cfg.hard_silence_s:
            self._escalated = True
            return SilenceEvent(
                SilenceAction.escalate, silence_s, self._reprompts,
                reason=f"cisza {silence_s:.0f}s ≥ próg twardy {cfg.hard_silence_s:.0f}s",
            )
        # cisza w granicach grace — czekamy
        if silence_s < cfg.grace_s:
            return SilenceEvent(
                SilenceAction.wait, silence_s, self._reprompts,
                reason="cisza w normie (senior może się zastanawiać)",
            )
        # cisza przekroczyła próg ponaglenia
        if silence_s >= cfg.reprompt_s:
            if self._reprompts >= cfg.max_reprompts:
                self._escalated = True
                return SilenceEvent(
                    SilenceAction.escalate, silence_s, self._reprompts,
                    reason=f"brak kontaktu po {self._reprompts} ponagleniach",
                )
            self._reprompts += 1
            return SilenceEvent(
                SilenceAction.reprompt, silence_s, self._reprompts,
                reason=f"ponaglenie #{self._reprompts}",
            )
        # między grace a reprompt — jeszcze czekamy, ale sygnalizujemy uwagę
        return SilenceEvent(
            SilenceAction.wait, silence_s, self._reprompts,
            reason="cisza wydłużona — obserwujemy",
        )


# ==================================================================
# 2) Barge-in — przerwanie TTS, gdy senior zaczyna mówić
# ==================================================================

class BargeInConfig:
    """Progi wykrycia mowy nakładającej się na TTS Adama."""
    def __init__(self, *, energy_threshold: float = 0.02, min_voiced_frames: int = 3):
        self.energy_threshold = energy_threshold
        self.min_voiced_frames = min_voiced_frames


@dataclass
class BargeInResult:
    interrupted: bool
    voiced_frames: int
    at_frame: int | None = None


class BargeInController:
    """Decyduje, czy przerwać odtwarzanie TTS, bo senior zaczął mówić.

    Otrzymuje sekwencję energii ramek nagranych RÓWNOLEGLE z odtwarzaniem TTS
    (echo-cancelled po stronie ARI). Gdy wykryje `min_voiced_frames` kolejnych
    ramek powyżej progu energii — sygnalizuje przerwanie (Adam milknie, słucha).
    """

    def __init__(self, config: BargeInConfig | None = None):
        self.config = config or BargeInConfig()

    def scan(self, frame_energies: list[float]) -> BargeInResult:
        cfg = self.config
        run = 0
        voiced_total = 0
        for i, e in enumerate(frame_energies):
            if e >= cfg.energy_threshold:
                run += 1
                voiced_total += 1
                if run >= cfg.min_voiced_frames:
                    return BargeInResult(
                        interrupted=True,
                        voiced_frames=voiced_total,
                        at_frame=i - cfg.min_voiced_frames + 1,
                    )
            else:
                run = 0
        return BargeInResult(interrupted=False, voiced_frames=voiced_total, at_frame=None)


# ==================================================================
# 3) Nagrania — rejestr referencji (audit / QA / RODO)
# ==================================================================

@dataclass
class RecordingRef:
    call_id: str
    audio_ref: str
    consented: bool
    seconds: float | None = None


class RecordingRegistry:
    """Rejestr nagrań połączenia. Fail-safe: bez zgody nie rejestrujemy audio.

    RODO: nagrywanie wymaga jawnej zgody seniora. `consented=False` → referencja
    NIE jest przechowywana (zwraca None), a próba jest logowana jako odmowa.
    """

    def __init__(self, *, consent: bool = False):
        self._consent = consent
        self._refs: list[RecordingRef] = []
        self._denied: int = 0

    @property
    def has_consent(self) -> bool:
        return self._consent

    @property
    def denied_count(self) -> int:
        return self._denied

    def register(self, call_id: str, audio_ref: str, *, seconds: float | None = None) -> RecordingRef | None:
        if not self._consent:
            self._denied += 1
            return None
        ref = RecordingRef(call_id=call_id, audio_ref=audio_ref, consented=True, seconds=seconds)
        self._refs.append(ref)
        return ref

    def refs(self) -> list[RecordingRef]:
        return list(self._refs)


# ==================================================================
# 4) Dual-STT — dwa niezależne silniki ASR → głosy konsensusu F14
# ==================================================================

@dataclass
class DualSttResult:
    primary: Transcript
    secondary: Transcript | None
    disagreement: bool
    votes: list[ModelVote] = field(default_factory=list)

    @property
    def text(self) -> str:
        """Tekst wiodący — zawsze z podstawowego STT (deterministyczne)."""
        return self.primary.text


class DualStt:
    """Łączy dwa niezależne porty ASR i przygotowuje głosy do konsensusu F14.

    - `primary`   — główny silnik (np. Whisper), wynik wiodący.
    - `secondary` — niezależny drugi silnik (np. Deepgram); opcjonalny, fail-safe:
      gdy zawiedzie lub go brak, degradujemy do samego primary (rozmowa trwa).

    Każdy transkrypt jest klasyfikowany detektorem kryzysowym F3 i zamieniany na
    `ModelVote` (role stt_primary / stt_secondary). Rozbieżność treści oznacza
    `disagreement=True` — sygnał do przeglądu / obniżonej pewności.
    """

    def __init__(
        self,
        primary: ASRPort,
        secondary: ASRPort | None = None,
        *,
        detector: CrisisDetector | None = None,
    ):
        self._primary = primary
        self._secondary = secondary
        self._detector = detector or CrisisDetector()

    def _vote(self, transcript: Transcript, role: VoterRole) -> ModelVote:
        cls = self._detector.to_classification(self._detector.detect(text=transcript.text))
        return ModelVote(
            source=role.value,
            level=cls.level,
            trigger=cls.trigger,
            confidence=min(cls.confidence, transcript.confidence),
            role=role,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join((text or "").lower().split())

    def transcribe(self, audio_ref: str) -> DualSttResult:
        primary = self._primary.transcribe(audio_ref)
        votes = [self._vote(primary, VoterRole.stt_primary)]

        secondary: Transcript | None = None
        disagreement = False
        if self._secondary is not None:
            try:
                secondary = self._secondary.transcribe(audio_ref)
            except Exception:
                secondary = None  # fail-safe — drugi STT nie może zablokować rozmowy
            if secondary is not None:
                votes.append(self._vote(secondary, VoterRole.stt_secondary))
                disagreement = self._normalize(primary.text) != self._normalize(secondary.text)

        return DualSttResult(
            primary=primary,
            secondary=secondary,
            disagreement=disagreement,
            votes=votes,
        )

    def voters(self) -> list[Callable[[str], ModelVote | None]]:
        """Zwraca dodatkowych głosujących F14 dla CrisisConsensus.add_voter.

        Głos wtórnego STT jest zbudowany „na żądanie" z tekstu wypowiedzi —
        w praktyce CrisisConsensus dostaje już tekst, więc drugi STT dokłada
        niezależną klasyfikację tego samego tekstu (nie ponownej transkrypcji).
        """
        def secondary_voter(text: str) -> ModelVote | None:
            if self._secondary is None:
                return None
            return self._vote(Transcript(text=text), VoterRole.stt_secondary)

        return [secondary_voter]
