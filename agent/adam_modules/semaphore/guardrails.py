"""
Guardrails (F4/F3.3) — walidacja klasyfikacji semafora + anty-halucynacja.

Cel: żaden alert krytyczny nie powstaje „z powietrza", a klasyfikacja o niskiej
pewności nie eskaluje bez potwierdzenia. Reguły:

1. PURPLE wymaga min. jednego twardego sygnału kryzysowego w `signals`
   (nie wolno oprzeć kryzysu na samym tonie rozmowy).
2. Klasyfikacja RED/PURPLE o pewności < progu → wymusza potwierdzenie
   (needs_confirmation), zamiast natychmiastowej eskalacji.
3. Confidence spoza [0,1] → odrzucone.
4. Anty-halucynacja: trigger musi być zgodny z zadeklarowanym poziomem.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from adam_modules.seniors.models import SemaphoreLevel
from .engine import Classification, TRIGGER_LEVEL

# Twarde sygnały wymagane, by dopuścić poziom PURPLE
_HARD_CRISIS_SIGNALS = {
    "chest_pain", "breathing_difficulty", "stroke_symptoms",
    "suicide_ideation", "unconscious", "severe_bleeding",
    "explicit_help_request", "keyword_match",
}

RED_MIN_CONFIDENCE = 0.6
PURPLE_MIN_CONFIDENCE = 0.5  # niższy próg — przy kryzysie wolimy fałszywy alarm niż przeoczenie


@dataclass
class GuardrailResult:
    ok: bool
    needs_confirmation: bool = False
    errors: list[str] = field(default_factory=list)
    adjusted_level: SemaphoreLevel | None = None


class Guardrails:
    @staticmethod
    def validate(classification: Classification) -> GuardrailResult:
        errors: list[str] = []

        # 3. zakres confidence
        if not (0.0 <= classification.confidence <= 1.0):
            errors.append(f"confidence poza zakresem [0,1]: {classification.confidence}")
            return GuardrailResult(ok=False, errors=errors)

        # 4. spójność trigger↔poziom (anty-halucynacja)
        expected = TRIGGER_LEVEL.get(classification.trigger)
        if expected is None:
            errors.append(f"nieznany trigger: {classification.trigger}")
            return GuardrailResult(ok=False, errors=errors)
        if expected != classification.level:
            errors.append(
                f"niespójność: trigger {classification.trigger.value} implikuje "
                f"{expected.value}, podano {classification.level.value}"
            )
            return GuardrailResult(ok=False, errors=errors)

        # 1. PURPLE wymaga twardego sygnału
        if classification.level == SemaphoreLevel.purple:
            has_hard = bool(_HARD_CRISIS_SIGNALS & set(classification.signals.keys()))
            # sam trigger kryzysowy też jest twardym sygnałem
            has_hard = has_hard or classification.trigger.value in _HARD_CRISIS_SIGNALS
            if not has_hard:
                errors.append("PURPLE bez twardego sygnału kryzysowego — odrzucono")
                return GuardrailResult(ok=False, errors=errors,
                                       adjusted_level=SemaphoreLevel.red)

        # 2. progi pewności dla eskalacji
        needs_confirmation = False
        if classification.level == SemaphoreLevel.red and classification.confidence < RED_MIN_CONFIDENCE:
            needs_confirmation = True
        if classification.level == SemaphoreLevel.purple and classification.confidence < PURPLE_MIN_CONFIDENCE:
            needs_confirmation = True

        return GuardrailResult(ok=True, needs_confirmation=needs_confirmation)
