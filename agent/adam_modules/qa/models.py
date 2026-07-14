"""
Modele F16 (ETAP 30) — pętla jakości (QA Loop) + telemetria decyzji + nastrój.

Cztery obszary trwałych danych:
  1. QAEvaluation      — zapis automatycznej oceny rozmowy (score + flagi + metryki).
  2. ManualAudit       — ludzki przegląd rozmowy (koordynator): werdykt + notatka.
  3. ImprovementItem   — wniosek z pętli poprawy (co usprawnić w Adamie/promptach).
  4. SentimentReading  — realny odczyt nastroju seniora w czasie (zamiast heurystyki).
  5. DecisionTelemetry — ślad decyzji konsensusu (EXECUTE/DEFER/ESCALATE/ABSTAIN),
                         w tym spięcie ESCALATE→112 (łączy ETAP 26+27 z QA).

Wszystko audytowalne (AI Act art. 12 — logowanie działania systemu wysokiego ryzyka).
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Integer, Float, Boolean, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from adam_modules.common.db import Base


class AuditVerdict(str, enum.Enum):
    ok = "ok"                        # rozmowa poprawna
    minor_issues = "minor_issues"    # drobne uwagi
    major_issues = "major_issues"    # poważne uchybienia
    unsafe = "unsafe"                # niebezpieczne (medyczne/eskalacja pominięta)


class ImprovementStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    dismissed = "dismissed"


class MoodLabel(str, enum.Enum):
    crisis = "crisis"
    distressed = "distressed"
    neutral = "neutral"
    content = "content"
    happy = "happy"


class DecisionKind(str, enum.Enum):
    execute = "EXECUTE"
    defer = "DEFER"
    escalate = "ESCALATE"
    abstain = "ABSTAIN"


class QAEvaluation(Base):
    __tablename__ = "qa_evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int | None] = mapped_column(ForeignKey("seniors.id"), index=True, nullable=True)
    conversation_ref: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    score: Mapped[float] = mapped_column(Float)
    flags: Mapped[str | None] = mapped_column(Text, nullable=True)      # JSON list[str]
    metrics: Mapped[str | None] = mapped_column(Text, nullable=True)    # JSON dict
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class ManualAudit(Base):
    __tablename__ = "manual_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evaluation_id: Mapped[int | None] = mapped_column(ForeignKey("qa_evaluations.id"), index=True, nullable=True)
    senior_id: Mapped[int | None] = mapped_column(ForeignKey("seniors.id"), index=True, nullable=True)
    conversation_ref: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    auditor: Mapped[str] = mapped_column(String(120))
    verdict: Mapped[AuditVerdict] = mapped_column(Enum(AuditVerdict), index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class ImprovementItem(Base):
    __tablename__ = "improvement_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_audit_id: Mapped[int | None] = mapped_column(ForeignKey("manual_audits.id"), index=True, nullable=True)
    category: Mapped[str] = mapped_column(String(64), index=True)  # np. prompt/asr/eskalacja/ton
    title: Mapped[str] = mapped_column(String(240))
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ImprovementStatus] = mapped_column(
        Enum(ImprovementStatus), default=ImprovementStatus.open, index=True
    )
    priority: Mapped[int] = mapped_column(Integer, default=3)  # 1=najwyższy
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class SentimentReading(Base):
    __tablename__ = "sentiment_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)
    conversation_ref: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    label: Mapped[MoodLabel] = mapped_column(Enum(MoodLabel), index=True)
    score: Mapped[float] = mapped_column(Float)   # -1..+1 (negatywny..pozytywny)
    source: Mapped[str] = mapped_column(String(48), default="text")  # text|prosody|wearable|consensus
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class DecisionTelemetry(Base):
    __tablename__ = "decision_telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senior_id: Mapped[int | None] = mapped_column(ForeignKey("seniors.id"), index=True, nullable=True)
    conversation_ref: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    decision: Mapped[DecisionKind] = mapped_column(Enum(DecisionKind), index=True)
    level: Mapped[str | None] = mapped_column(String(16), nullable=True)
    trigger: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    voters: Mapped[str | None] = mapped_column(Text, nullable=True)     # JSON list
    escalated_112: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    emergency_call_id: Mapped[int | None] = mapped_column(
        ForeignKey("emergency_calls.id"), nullable=True
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
