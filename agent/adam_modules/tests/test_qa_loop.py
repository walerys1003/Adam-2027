"""Testy F16 (ETAP 30) — QA loop, audyt, improvement loop, nastrój, telemetria decyzji."""
from __future__ import annotations

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.qa import (
    QAService, Turn, AuditVerdict, ImprovementStatus, DecisionKind, MoodLabel,
    analyze_sentiment,
)


def _senior(session):
    return SeniorService(session).create(SeniorCreate(first_name="Jan", last_name="Nowak"))


def test_sentiment_detects_distress():
    r = analyze_sentiment("Jestem samotny i smutno mi", semaphore_level="yellow")
    assert r.label == MoodLabel.distressed
    assert r.score < 0


def test_sentiment_crisis_from_semaphore():
    r = analyze_sentiment("wszystko dobrze", semaphore_level="purple")
    assert r.label == MoodLabel.crisis


def test_sentiment_positive():
    r = analyze_sentiment("cieszę się, odwiedziły mnie wnuki, wszystko świetnie")
    assert r.label in (MoodLabel.content, MoodLabel.happy)
    assert r.score > 0


def test_evaluate_and_store(session):
    s = _senior(session)
    svc = QAService(session)
    turns = [Turn("adam", "Jestem cyfrowym asystentem Adam"), Turn("senior", "Dzień dobry")]
    ev = svc.evaluate_and_store(turns, senior_id=s.id, conversation_ref="c1")
    assert ev.id is not None
    assert 0 <= ev.score <= 100


def test_audit_generates_improvement(session):
    s = _senior(session)
    svc = QAService(session)
    audit = svc.record_audit(auditor="koordynator", verdict=AuditVerdict.unsafe,
                             note="pominięto eskalację", senior_id=s.id)
    items = svc.improvements_from_audit(audit)
    assert len(items) == 1
    assert items[0].priority == 1
    backlog = svc.improvement_backlog()
    assert len(backlog) == 1


def test_resolve_improvement(session):
    svc = QAService(session)
    item = svc.open_improvement(category="prompt", title="popraw ton")
    resolved = svc.resolve_improvement(item.id, status=ImprovementStatus.resolved)
    assert resolved.status == ImprovementStatus.resolved
    assert resolved.resolved_at is not None
    assert svc.improvement_backlog() == []


def test_record_sentiment_and_timeline(session):
    s = _senior(session)
    svc = QAService(session)
    svc.record_sentiment(senior_id=s.id, text="smutno mi", semaphore_level="yellow")
    svc.record_sentiment(senior_id=s.id, text="cieszę się")
    timeline = svc.mood_timeline(s.id)
    assert len(timeline) == 2
    assert svc.average_mood(s.id) is not None


def test_decision_telemetry_escalate_112(session):
    s = _senior(session)
    svc = QAService(session)
    row = svc.record_decision(
        decision=DecisionKind.escalate, senior_id=s.id, conversation_ref="c9",
        level="red", trigger="chest_pain", confidence=0.9,
        voters=["stt_primary", "llm_safety"], escalated_112=True,
    )
    assert row.escalated_112 is True
    stats = svc.escalation_stats()
    assert stats["decisions_total"] == 1
    assert stats["escalated_112"] == 1
