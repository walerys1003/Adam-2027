"""
Modele F12 — RODO (ochrona danych).

DataProcessingLog — rejestr operacji na danych osobowych (art. 30 RODO —
rejestr czynności przetwarzania). Każdy eksport/usunięcie/anonimizacja jest
logowana z podstawą prawną i zakresem.
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from adam_modules.common.db import Base


class ProcessingAction(str, enum.Enum):
    export = "export"                 # eksport danych (prawo dostępu)
    soft_delete = "soft_delete"       # oznaczenie do usunięcia
    erase = "erase"                   # trwałe usunięcie (prawo do zapomnienia)
    anonymize = "anonymize"           # anonimizacja
    retention_purge = "retention_purge"  # automatyczne czyszczenie wg retencji
    access = "access"                 # dostęp/odczyt danych


class DataCategory(str, enum.Enum):
    profile = "profile"               # dane profilowe / PII
    recordings = "recordings"         # nagrania rozmów
    transcripts = "transcripts"       # transkrypcje
    reports = "reports"               # raporty semafora / zdrowotne
    memory = "memory"                 # pamięć semantyczna
    vitals = "vitals"                 # dane z wearables


class DataProcessingLog(Base):
    __tablename__ = "data_processing_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)
    action: Mapped[ProcessingAction] = mapped_column(Enum(ProcessingAction), index=True)
    category: Mapped[DataCategory | None] = mapped_column(Enum(DataCategory), nullable=True)
    legal_basis: Mapped[str] = mapped_column(String(120), default="art. 6 ust. 1 lit. b RODO")
    actor: Mapped[str | None] = mapped_column(String(120), nullable=True)  # kto wykonał
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DataProcessingLog s{self.senior_id} {self.action.value}>"
