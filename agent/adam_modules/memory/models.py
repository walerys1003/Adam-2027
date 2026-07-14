"""
Modele F7 — Pamięć semantyczna rozmów.

MemoryChunk — fragment rozmowy/wiedzy o seniorze z zapisanym embeddingiem.
Embedding przechowujemy jako JSON (Text) — przenośne między SQLite (dev) i
PostgreSQL (prod). W produkcji z pgvector można zmienić kolumnę na Vector,
zachowując resztę API (retrieval liczy cosine w Pythonie jako fallback).
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from adam_modules.common.db import Base


class MemoryKind(str, enum.Enum):
    conversation = "conversation"  # fragment rozmowy z Adamem
    fact = "fact"                  # trwały fakt (np. "lubi kawę o 15")
    preference = "preference"      # preferencja seniora
    health_note = "health_note"    # notatka zdrowotna (nie-medyczna diagnoza)


class MemoryChunk(Base):
    __tablename__ = "memory_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)

    kind: Mapped[MemoryKind] = mapped_column(Enum(MemoryKind), default=MemoryKind.conversation, index=True)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[str] = mapped_column(Text)  # JSON list[float]
    embed_model: Mapped[str] = mapped_column(String(60), default="hashing-256")
    source_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)  # np. id rozmowy

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MemoryChunk s{self.senior_id} {self.kind.value} {self.content[:24]!r}>"


class ConversationSummary(Base):
    """Streszczenie pojedynczej rozmowy (F7, ETAP 28) — pamięć długoterminowa.

    Po zakończeniu połączenia zapisujemy zwięzłe podsumowanie (nastrój, tematy,
    ustalenia, poziom semafora). Streszczenia są tańsze do przeglądania i
    stanowią bazę „ciągłości": Adam może nawiązać do poprzedniej rozmowy.
    """
    __tablename__ = "conversation_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)
    conversation_ref: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    summary: Mapped[str] = mapped_column(Text)
    mood: Mapped[str | None] = mapped_column(String(32), nullable=True)
    max_level: Mapped[str | None] = mapped_column(String(16), nullable=True)
    topics: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list[str]
    turn_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ConversationSummary s{self.senior_id} {self.summary[:24]!r}>"
