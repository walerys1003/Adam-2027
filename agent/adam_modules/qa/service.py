"""
QAService (F16, ETAP 30) — pętla jakości + telemetria decyzji + nastrój.

Spina automatyczną ocenę (QAEvaluator), ludzki audyt (ManualAudit), wnioski
poprawy (ImprovementItem), realny nastrój (SentimentReading) oraz telemetrię
decyzji konsensusu (DecisionTelemetry — w tym spięcie ESCALATE→112).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .metrics import QAEvaluator, QAResult, Turn
from .models import (
    QAEvaluation, ManualAudit, ImprovementItem, SentimentReading,
    DecisionTelemetry, AuditVerdict, ImprovementStatus, MoodLabel, DecisionKind,
)
from .sentiment import analyze_sentiment, SentimentResult


class QAService:
    def __init__(self, session: Session):
        self.session = session
        self._evaluator = QAEvaluator()

    # ---- automatyczna ocena ----
    def evaluate_and_store(
        self, turns: list[Turn], *, senior_id: int | None = None,
        conversation_ref: str | None = None, duration_s: float | None = None,
        interruptions: int = 0, completed: bool = True,
    ) -> QAEvaluation:
        result: QAResult = self._evaluator.evaluate(
            turns, duration_s=duration_s, interruptions=interruptions, completed=completed,
        )
        row = QAEvaluation(
            senior_id=senior_id,
            conversation_ref=conversation_ref,
            score=result.score,
            flags=json.dumps(result.flags, ensure_ascii=False),
            metrics=json.dumps(result.metrics, ensure_ascii=False),
            needs_review=self._evaluator.needs_human_review(result),
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def pending_review(self, limit: int = 50) -> list[QAEvaluation]:
        stmt = (
            select(QAEvaluation)
            .where(QAEvaluation.needs_review.is_(True))
            .order_by(QAEvaluation.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    # ---- ludzki audyt ----
    def record_audit(
        self, *, auditor: str, verdict: AuditVerdict, note: str | None = None,
        evaluation_id: int | None = None, senior_id: int | None = None,
        conversation_ref: str | None = None,
    ) -> ManualAudit:
        audit = ManualAudit(
            evaluation_id=evaluation_id, senior_id=senior_id,
            conversation_ref=conversation_ref, auditor=auditor,
            verdict=verdict, note=note,
        )
        self.session.add(audit)
        self.session.commit()
        self.session.refresh(audit)
        return audit

    # ---- pętla poprawy ----
    def open_improvement(
        self, *, category: str, title: str, detail: str | None = None,
        priority: int = 3, source_audit_id: int | None = None,
    ) -> ImprovementItem:
        item = ImprovementItem(
            category=category, title=title, detail=detail,
            priority=priority, source_audit_id=source_audit_id,
            status=ImprovementStatus.open,
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def resolve_improvement(self, item_id: int, *, status: ImprovementStatus) -> ImprovementItem | None:
        item = self.session.get(ImprovementItem, item_id)
        if not item:
            return None
        item.status = status
        if status in (ImprovementStatus.resolved, ImprovementStatus.dismissed):
            item.resolved_at = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(item)
        return item

    def improvement_backlog(self, *, only_open: bool = True, limit: int = 100) -> list[ImprovementItem]:
        stmt = select(ImprovementItem)
        if only_open:
            stmt = stmt.where(ImprovementItem.status.in_(
                (ImprovementStatus.open, ImprovementStatus.in_progress)
            ))
        stmt = stmt.order_by(ImprovementItem.priority.asc(), ImprovementItem.created_at.desc()).limit(limit)
        return list(self.session.scalars(stmt))

    def improvements_from_audit(self, audit: ManualAudit) -> list[ImprovementItem]:
        """Automatycznie generuje wnioski poprawy dla audytu z uwagami."""
        created: list[ImprovementItem] = []
        if audit.verdict == AuditVerdict.ok:
            return created
        priority = {
            AuditVerdict.minor_issues: 3,
            AuditVerdict.major_issues: 2,
            AuditVerdict.unsafe: 1,
        }[audit.verdict]
        created.append(self.open_improvement(
            category="audyt",
            title=f"Follow-up audytu #{audit.id} ({audit.verdict.value})",
            detail=audit.note,
            priority=priority,
            source_audit_id=audit.id,
        ))
        return created

    # ---- realny nastrój ----
    def record_sentiment(
        self, *, senior_id: int, text: str, semaphore_level: str | None = None,
        prosody_valence: float | None = None, conversation_ref: str | None = None,
        source: str = "text",
    ) -> SentimentReading:
        res: SentimentResult = analyze_sentiment(
            text, semaphore_level=semaphore_level,
            prosody_valence=prosody_valence, source=source,
        )
        row = SentimentReading(
            senior_id=senior_id, conversation_ref=conversation_ref,
            label=res.label, score=res.score, source=res.source,
            evidence=json.dumps(res.evidence, ensure_ascii=False),
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def mood_timeline(self, senior_id: int, limit: int = 20) -> list[SentimentReading]:
        stmt = (
            select(SentimentReading)
            .where(SentimentReading.senior_id == senior_id)
            .order_by(SentimentReading.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def average_mood(self, senior_id: int, limit: int = 20) -> float | None:
        rows = self.mood_timeline(senior_id, limit)
        if not rows:
            return None
        return round(sum(r.score for r in rows) / len(rows), 3)

    # ---- telemetria decyzji (ESCALATE→112) ----
    def record_decision(
        self, *, decision: DecisionKind, senior_id: int | None = None,
        conversation_ref: str | None = None, level: str | None = None,
        trigger: str | None = None, confidence: float | None = None,
        voters: list | None = None, escalated_112: bool = False,
        emergency_call_id: int | None = None, note: str | None = None,
    ) -> DecisionTelemetry:
        row = DecisionTelemetry(
            senior_id=senior_id, conversation_ref=conversation_ref,
            decision=decision, level=level, trigger=trigger, confidence=confidence,
            voters=json.dumps(voters, ensure_ascii=False) if voters is not None else None,
            escalated_112=escalated_112, emergency_call_id=emergency_call_id, note=note,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def decisions(self, *, senior_id: int | None = None, limit: int = 100) -> list[DecisionTelemetry]:
        stmt = select(DecisionTelemetry)
        if senior_id is not None:
            stmt = stmt.where(DecisionTelemetry.senior_id == senior_id)
        stmt = stmt.order_by(DecisionTelemetry.created_at.desc()).limit(limit)
        return list(self.session.scalars(stmt))

    def escalation_stats(self) -> dict:
        total = self.session.scalar(select(func.count(DecisionTelemetry.id))) or 0
        escalated = self.session.scalar(
            select(func.count(DecisionTelemetry.id)).where(DecisionTelemetry.escalated_112.is_(True))
        ) or 0
        return {"decisions_total": total, "escalated_112": escalated}
