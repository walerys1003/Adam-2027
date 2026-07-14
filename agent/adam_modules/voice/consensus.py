"""Konsensus kryzysowy warstwy głosowej (ETAP 17.1).

Produkcyjnie decyzji o eskalacji nie opieramy na jednym źródle. `CrisisConsensus`
łączy dwa niezależne głosy dla każdej wypowiedzi seniora:

1. **Detektor regułowy (F3/F8)** — deterministyczny, audytowalny; twarde sygnały
   kryzysowe MUSZĄ być wykrywane regułowo (wymóg fail-safe / AI Act).
2. **Klasyfikator LLM** — model językowy ocenia tę samą wypowiedź (port
   `LLMPort.classify`); w dev używamy `RuleLLM` (heurystyki), w produkcji GPT/itp.

Głosy trafiają do `ConsensusEngine` (F16), który stosuje regułę fail-safe:
przy rozbieżności wybiera **wyższy** poziom i oznacza `needs_review`. Dzięki temu
LLM może *podnieść* czujność (np. wykryć niuans, którego reguła nie ma), ale nie
może *obniżyć* twardego sygnału detektora.

Moduł jest czysty (bez sieci): LLM to wstrzykiwany port.
"""
from __future__ import annotations

from dataclasses import dataclass

from adam_modules.semaphore.detector import CrisisDetector
from adam_modules.semaphore.models import SemaphoreLevel, Trigger
from adam_modules.consensus.engine import ConsensusEngine, ModelVote, ConsensusResult
from .ports import LLMPort


@dataclass
class CrisisVoteResult:
    """Wynik konsensusu dla pojedynczej wypowiedzi."""
    level: SemaphoreLevel
    trigger: Trigger
    confidence: float
    needs_review: bool
    agreement: float
    sources: list[str]
    notes: list[str]

    @property
    def is_critical(self) -> bool:
        return self.level in (SemaphoreLevel.red, SemaphoreLevel.purple)


class CrisisConsensus:
    """Łączy głos detektora regułowego i klasyfikatora LLM w decyzję fail-safe."""

    def __init__(
        self,
        llm: LLMPort,
        *,
        detector: CrisisDetector | None = None,
        engine: ConsensusEngine | None = None,
        use_llm: bool = True,
    ):
        self._llm = llm
        self._detector = detector or CrisisDetector()
        self._engine = engine or ConsensusEngine()
        # LLM-głos jest opcjonalny: gdy port nie wspiera classify albo świadomie
        # wyłączony, konsensus degraduje się do samego detektora (nadal fail-safe).
        self._use_llm = use_llm and hasattr(llm, "classify")

    def _detector_vote(self, text: str) -> ModelVote:
        detections = self._detector.detect(text=text)
        cls = self._detector.to_classification(detections)
        return ModelVote(
            source="rule_detector",
            level=cls.level,
            trigger=cls.trigger,
            confidence=cls.confidence,
        )

    def _llm_vote(self, text: str) -> ModelVote | None:
        if not self._use_llm:
            return None
        try:
            v = self._llm.classify(text=text)  # type: ignore[attr-defined]
        except Exception:
            # LLM zawiódł → pomijamy jego głos; detektor pozostaje (fail-safe).
            return None
        if v is None:
            return None
        return ModelVote(
            source="llm", level=v.level, trigger=v.trigger, confidence=v.confidence,
        )

    def assess(self, text: str) -> CrisisVoteResult:
        votes: list[ModelVote] = [self._detector_vote(text)]
        llm_vote = self._llm_vote(text)
        if llm_vote is not None:
            votes.append(llm_vote)

        result: ConsensusResult = self._engine.decide(votes)
        return CrisisVoteResult(
            level=result.level,
            trigger=result.trigger,
            confidence=result.confidence,
            needs_review=result.needs_review,
            agreement=result.agreement,
            sources=[v.source for v in result.votes],
            notes=result.notes,
        )
