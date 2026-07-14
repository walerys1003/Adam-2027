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

from dataclasses import dataclass, field

from adam_modules.seniors.models import SemaphoreLevel
from adam_modules.semaphore.engine import Classification, level_rank, max_level
from adam_modules.semaphore.models import Trigger

MIN_SOURCES_FOR_CRITICAL = 2


@dataclass
class ModelVote:
    source: str
    level: SemaphoreLevel
    trigger: Trigger
    confidence: float = 1.0


@dataclass
class ConsensusResult:
    level: SemaphoreLevel
    trigger: Trigger
    confidence: float
    agreement: float                    # udział głosów za wynikowym poziomem
    needs_review: bool = False
    votes: list[ModelVote] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

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
                notes=["brak głosów"],
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

        return ConsensusResult(
            level=top_level, trigger=trigger, confidence=confidence,
            agreement=round(agreement, 3), needs_review=needs_review,
            votes=votes, notes=notes,
        )
