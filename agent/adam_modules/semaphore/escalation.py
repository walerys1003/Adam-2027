"""
EscalationLadder (F3.2) — drabina eskalacji po alercie semafora.

RED:
  1. retry_call        (ponów próbę kontaktu — powiązane z F2)
  2. sms_family        (SMS do rodziny / opiekuna)
  3. notify_coordinator(powiadom koordynatora SilverTech)
  4. escalate_purple   (brak reakcji w oknie → podnieś do PURPLE)

PURPLE (kryzys):
  1. call_112          (natychmiastowe zgłoszenie 112 z payloadem — F17)
  2. notify_coordinator
  3. sms_family

Każdy krok ma opóźnienie (delay_s) względem poprzedniego. Ta klasa NIE śpi
realnie — zwraca plan kroków z czasami; wykonanie/timery robi warstwa runtime
(APScheduler / kolejka) w Frankfurt DC. Dzięki temu logika jest w pełni testowalna.
"""
from __future__ import annotations

from dataclasses import dataclass

from adam_modules.seniors.models import SemaphoreLevel


@dataclass
class EscalationStep:
    order: int
    action: str
    delay_s: int          # opóźnienie od poprzedniego kroku
    at_offset_s: int      # skumulowany offset od startu eskalacji
    bypass_dnd: bool = False
    description: str = ""


# Definicje drabin (delay_s względem poprzedniego kroku)
_RED_LADDER = [
    ("retry_call", 0, "Ponów próbę kontaktu telefonicznego z seniorem"),
    ("sms_family", 60, "Wyślij SMS do rodziny/opiekuna głównego"),
    ("notify_coordinator", 120, "Powiadom koordynatora SilverTech"),
    ("escalate_purple", 300, "Brak reakcji — podnieś alert do poziomu FIOLETOWEGO"),
]

_PURPLE_LADDER = [
    ("call_112", 0, "Natychmiastowe zgłoszenie 112 (adres, wiek, leki)"),
    ("notify_coordinator", 0, "Równolegle powiadom koordynatora"),
    ("sms_family", 0, "Równolegle SMS do rodziny — bypass trybu Nie przeszkadzać"),
]


class EscalationLadder:
    @staticmethod
    def plan(level: SemaphoreLevel) -> list[EscalationStep]:
        """Zwraca uporządkowany plan kroków eskalacji dla danego poziomu."""
        if level == SemaphoreLevel.purple:
            raw, bypass = _PURPLE_LADDER, True
        elif level == SemaphoreLevel.red:
            raw, bypass = _RED_LADDER, False
        else:
            return []

        steps: list[EscalationStep] = []
        offset = 0
        for i, (action, delay, desc) in enumerate(raw, start=1):
            offset += delay
            steps.append(EscalationStep(
                order=i, action=action, delay_s=delay, at_offset_s=offset,
                bypass_dnd=bypass or action == "call_112",
                description=desc,
            ))
        return steps

    @staticmethod
    def next_step(level: SemaphoreLevel, completed_actions: list[str]) -> EscalationStep | None:
        """Zwraca pierwszy krok, który nie został jeszcze wykonany."""
        for step in EscalationLadder.plan(level):
            if step.action not in completed_actions:
                return step
        return None
