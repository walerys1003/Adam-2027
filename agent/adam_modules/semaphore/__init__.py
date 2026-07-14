"""
F3+F4+F5 — Semafor + Eskalacja + Guardrails + System Prompt (rdzeń bezpieczeństwa).

- engine.py      SemaphoreEngine: TRIGGERS → poziom, state machine, zapis zdarzeń
- escalation.py  EscalationLadder: RED (retry→SMS→koordynator) → PURPLE → 112
- guardrails.py  walidacja klasyfikacji + anty-halucynacja
- prompt.py      System Prompt Adama + AI Act disclosure
- models.py      tabela semaphore_events
"""
from .models import SemaphoreEvent, Trigger
from .engine import SemaphoreEngine, Classification
from .escalation import EscalationLadder, EscalationStep
from .guardrails import Guardrails, GuardrailResult
from .prompt import build_system_prompt, AI_ACT_DISCLOSURE

__all__ = [
    "SemaphoreEvent", "Trigger",
    "SemaphoreEngine", "Classification",
    "EscalationLadder", "EscalationStep",
    "Guardrails", "GuardrailResult",
    "build_system_prompt", "AI_ACT_DISCLOSURE",
]
