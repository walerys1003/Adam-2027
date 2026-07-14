"""
F16 — Multi-model consensus.

Dla klasyfikacji krytycznych (RED/PURPLE) nie polegamy na jednym modelu.
ConsensusEngine zbiera niezależne klasyfikacje z >=2 źródeł (np. detektor
regułowy F8 + model LLM A + model LLM B) i podejmuje decyzję fail-safe:

- Zgodność → wynik zgodny, wysoka pewność.
- Rozbieżność przy sygnale krytycznym → wybieramy WYŻSZY poziom (bezpieczniej
  fałszywy alarm niż przeoczenie kryzysu) i oznaczamy needs_review.
- Za mało źródeł dla poziomu krytycznego → wymuszamy potwierdzenie.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field

from adam_modules.seniors.models import SemaphoreLevel
from adam_modules.semaphore.engine import Classification, level_rank, max_level
from adam_modules.semaphore.models import Trigger

MIN_SOURCES_FOR_CRITICAL = 2
# Próg pewności, poniżej którego odkładamy decyzję (DEFER) zamiast EXECUTE.
DEFER_CONFIDENCE = 0.5


class VoterRole(str, enum.Enum):
    """Role głosujących wg specyfikacji F14 (multi-model consensus)."""
    stt_primary = "stt_primary"       # główny STT (np. whisper) + detektor regułowy
    stt_secondary = "stt_secondary"   # drugi, niezależny STT (np. deepgram) — dual-STT
    llm_safety = "llm_safety"         # LLM oceniający bezpieczeństwo/kryzys
    sentiment = "sentiment"           # analiza emocji/nastroju
    wearable = "wearable"             # sygnał z urządzeń (HR/SpO2)


class ConsensusDecision(str, enum.Enum):
    """Macierz decyzyjna 4-stanowa (F14)."""
    EXECUTE = "execute"     # działaj wg wyniku (zgodność, wystarczające źródła)
    DEFER = "defer"         # odłóż/poproś o potwierdzenie (niska pewność, brak krytyku)
    ESCALATE = "escalate"   # eskaluj do człowieka/służb (kryzys lub sporna sytuacja krytyczna)
    ABSTAIN = "abstain"     # wstrzymaj się (brak danych/za mało źródeł, bez sygnału krytycznego)


@dataclass
class ModelVote:
    source: str
    level: SemaphoreLevel
    trigger: Trigger
    confidence: float = 1.0
    role: VoterRole | None = None


@dataclass
class ConsensusResult:
    level: SemaphoreLevel
    trigger: Trigger
    confidence: float
    agreement: float                    # udział głosów za wynikowym poziomem
    needs_review: bool = False
    votes: list[ModelVote] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    decision: ConsensusDecision = ConsensusDecision.EXECUTE

    def to_classification(self) -> Classification:
        return Classification(
            level=self.level, trigger=self.trigger, confidence=self.confidence,
            signals={"consensus_agreement": self.agreement,
                     "sources": [v.source for v in self.votes]},
        )


class ConsensusEngine:
    def decide(self, votes: list[ModelVote]) -> ConsensusResult:
        if not votes:
            return ConsensusResult(
                level=SemaphoreLevel.green, trigger=Trigger.routine_ok,
                confidence=0.0, agreement=0.0, needs_review=True,
                notes=["brak głosów"], decision=ConsensusDecision.ABSTAIN,
            )

        notes: list[str] = []
        # najwyższy poziom wśród głosów (fail-safe)
        top_level = votes[0].level
        for v in votes[1:]:
            top_level = max_level(top_level, v.level)

        supporting = [v for v in votes if v.level == top_level]
        agreement = len(supporting) / len(votes)

        # trigger: najczęstszy wśród wspierających, remis → najwyższa pewność
        trigger = max(supporting, key=lambda v: v.confidence).trigger
        avg_conf = sum(v.confidence for v in supporting) / len(supporting)

        needs_review = False
        is_critical = level_rank(top_level) >= level_rank(SemaphoreLevel.red)

        if is_critical and len(votes) < MIN_SOURCES_FOR_CRITICAL:
            needs_review = True
            notes.append(f"za mało źródeł ({len(votes)}) dla poziomu krytycznego")

        if agreement < 1.0:
            notes.append(f"rozbieżność modeli — wybrano wyższy poziom {top_level.value}")
            if is_critical:
                needs_review = True

        # pewność skorygowana o zgodność
        confidence = round(avg_conf * (0.5 + 0.5 * agreement), 4)

        decision = self._decide_action(
            level=top_level, confidence=confidence, agreement=agreement,
            n_votes=len(votes), is_critical=is_critical, needs_review=needs_review,
        )

        return ConsensusResult(
            level=top_level, trigger=trigger, confidence=confidence,
            agreement=round(agreement, 3), needs_review=needs_review,
            votes=votes, notes=notes, decision=decision,
        )

    @staticmethod
    def _decide_action(*, level: SemaphoreLevel, confidence: float, agreement: float,
                       n_votes: int, is_critical: bool,
                       needs_review: bool) -> ConsensusDecision:
        """Macierz decyzyjna 4-stanowa (F14).

        - ESCALATE: sytuacja krytyczna (RED/PURPLE) LUB krytyczna sporna/niepewna
          (needs_review) — bezpieczeństwo ponad wszystko.
        - ABSTAIN: brak sygnału (zielony) przy zbyt małej liczbie źródeł.
        - DEFER: niekrytyczne, ale niska pewność / rozbieżność → poproś o potwierdzenie.
        - EXECUTE: pozostałe (pewny, zgodny wynik niekrytyczny).
        """
        if is_critical:
            # kryzys zawsze eskaluje (nawet przy pełnej zgodności — to jego cel)
            return ConsensusDecision.ESCALATE
        if needs_review:
            # sporna sytuacja niekrytyczna, ale zgłoszona do przeglądu → odłóż
            return ConsensusDecision.DEFER
        if level == SemaphoreLevel.green:
            if n_votes < MIN_SOURCES_FOR_CRITICAL:
                return ConsensusDecision.ABSTAIN
            return ConsensusDecision.EXECUTE
        # YELLOW: działaj, chyba że niska pewność/rozbieżność
        if confidence < DEFER_CONFIDENCE or agreement < 1.0:
            return ConsensusDecision.DEFER
        return ConsensusDecision.EXECUTE
