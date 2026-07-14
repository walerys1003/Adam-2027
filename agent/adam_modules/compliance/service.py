"""
ComplianceService (F13) — rejestr systemu AI + log ujawnień (AI Act).

SYSTEM_REGISTER: statyczny opis systemu wysokiego ryzyka (art. 11 + zał. IV) —
przeznaczenie, nadzór ludzki, ograniczenia, dane treningowe. record_disclosure()
zapisuje dowód ujawnienia natury AI dla konkretnej rozmowy; assert_disclosed()
weryfikuje, że rozmowa spełnia obowiązek art. 50.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from adam_modules.seniors.models import Senior
from adam_modules.semaphore.prompt import AI_ACT_DISCLOSURE
from .models import DisclosureLog, DisclosureChannel

# Rejestr systemu AI (art. 11 / zał. IV AI Act) — metadane zgodności.
SYSTEM_REGISTER = {
    "system_name": "Adam",
    "provider": "SilverTech, Poznań",
    "purpose": "Głosowy asystent welfare-check dla seniorów (klasyfikacja ryzyka).",
    "risk_class": "high-risk (opieka zdrowotna / bezpieczeństwo osób)",
    "human_oversight": "Koordynator SilverTech + rodzina; eskalacja do 112.",
    "limitations": "Nie diagnozuje, nie zmienia leków; klasyfikuje sygnały.",
    "transparency": "Ujawnia naturę AI na początku każdej rozmowy (art. 50).",
    "logging": "Zdarzenia semafora, ujawnienia, przetwarzanie danych (RODO).",
    "version": "1.0",
}


class ComplianceService:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def system_register() -> dict:
        return dict(SYSTEM_REGISTER)

    def record_disclosure(self, senior: Senior, conversation_ref: str,
                          channel: DisclosureChannel = DisclosureChannel.voice,
                          disclosed: bool = True,
                          disclosure_text: str | None = None) -> DisclosureLog:
        log = DisclosureLog(
            senior_id=senior.id,
            conversation_ref=conversation_ref,
            channel=channel,
            disclosed=disclosed,
            disclosure_text=disclosure_text or (AI_ACT_DISCLOSURE if disclosed else None),
        )
        self.session.add(log)
        self.session.flush()
        return log

    def assert_disclosed(self, conversation_ref: str) -> bool:
        """True, gdy dla rozmowy istnieje wpis z disclosed=True."""
        log = self.session.scalar(
            select(DisclosureLog).where(
                DisclosureLog.conversation_ref == conversation_ref,
                DisclosureLog.disclosed.is_(True),
            )
        )
        return log is not None

    def disclosure_history(self, senior_id: int, limit: int = 50) -> list[DisclosureLog]:
        return list(self.session.scalars(
            select(DisclosureLog).where(DisclosureLog.senior_id == senior_id)
            .order_by(DisclosureLog.id.desc()).limit(limit)
        ))
