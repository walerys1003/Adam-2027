"""
Wrapper ARI originate (F2).

AriOriginator to abstrakcja połączenia wychodzącego przez Asterisk ARI.
Produkcyjnie łączy się z istniejącym klientem AVA (src/ari_client.py); tutaj
definiujemy interfejs + implementację NULL do testów (nie dzwoni naprawdę).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Protocol


@dataclass
class OriginateResult:
    ok: bool
    channel_id: str | None = None
    reason: str | None = None


class AriOriginator(Protocol):
    def originate(self, phone: str, *, senior_external_id: str, context: str) -> OriginateResult:
        ...


class NullOriginator:
    """Implementacja testowa — konfigurowalny wynik, bez realnego dzwonienia."""

    def __init__(self, *, should_answer: bool = True, fail: bool = False):
        self.should_answer = should_answer
        self.fail = fail
        self.calls: list[dict] = []

    def originate(self, phone: str, *, senior_external_id: str, context: str) -> OriginateResult:
        self.calls.append({"phone": phone, "senior": senior_external_id, "context": context})
        if self.fail:
            return OriginateResult(ok=False, reason="ari_error")
        if not self.should_answer:
            return OriginateResult(ok=False, reason="no_answer")
        return OriginateResult(ok=True, channel_id=f"PJSIP/adam-{uuid.uuid4().hex[:6]}")
