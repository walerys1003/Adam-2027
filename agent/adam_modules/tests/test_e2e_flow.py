"""
F18 — Testy E2E: pełny przepływ bezpieczeństwa Adama.

Scenariusz kryzysowy (PURPLE) od wypowiedzi seniora do wezwania 112:
detekcja (F8) → consensus (F16) → guardrails (F4) → semafor (F3) →
eskalacja (F3.2) → powiadomienie rodziny (F9) → payload 112 (F17) →
log ujawnienia AI (F13). Oraz scenariusz rutynowy (GREEN).
"""
from datetime import date

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.seniors.models import SemaphoreLevel
from adam_modules.semaphore import (
    CrisisDetector, SemaphoreEngine, Guardrails, EscalationLadder,
)
from adam_modules.consensus import ConsensusEngine, ModelVote
from adam_modules.family import FamilyService, FamilyRole, SmsAdapter
from adam_modules.emergency import EmergencyService
from adam_modules.compliance import ComplianceService


def _senior(session):
    return SeniorService(session).create(
        SeniorCreate(
            first_name="Halina", last_name="Nowak", phone="+48123456789",
            birth_date=date(1940, 5, 10), address="ul. Kwiatowa 3, Poznań", district="Grunwald",
        )
    )


def test_e2e_crisis_purple_to_112(session):
    s = _senior(session)

    # 0. Ujawnienie AI na starcie rozmowy (F13)
    compliance = ComplianceService(session)
    compliance.record_disclosure(s, "conv-e2e-1")
    assert compliance.assert_disclosed("conv-e2e-1") is True

    # 1. Detekcja sygnału (F8)
    detector = CrisisDetector()
    detections = detector.detect_text("Adamie, strasznie boli mnie w klatce i nie mogę oddychać")
    assert detections
    cls = detector.to_classification(detections)
    assert cls.level == SemaphoreLevel.purple

    # 2. Consensus (F16) — detektor + drugi model
    consensus = ConsensusEngine()
    result = consensus.decide([
        ModelVote("rules", cls.level, cls.trigger, cls.confidence),
        ModelVote("llm_a", SemaphoreLevel.purple, cls.trigger, 0.8),
    ])
    assert result.level == SemaphoreLevel.purple
    consensus_cls = result.to_classification()

    # 3. Guardrails (F4)
    guard = Guardrails.validate(cls)  # oryginalna klasyfikacja ma twardy trigger
    assert guard.ok is True

    # 4. Semafor (F3) — zapis i podniesienie poziomu
    engine = SemaphoreEngine(session)
    event = engine.apply(s, cls)
    assert s.semaphore == SemaphoreLevel.purple
    assert event.new_level == SemaphoreLevel.purple

    # 5. Eskalacja (F3.2) — plan PURPLE zaczyna od 112, wszystkie bypass DND
    ladder = EscalationLadder()
    plan = ladder.plan(SemaphoreLevel.purple)
    assert plan[0].action == "call_112"
    assert all(step.bypass_dnd for step in plan)

    # 6. Powiadomienie rodziny (F9) — bypass DND
    family = FamilyService(session, adapters={"sms": SmsAdapter()})
    family.add_member(s, "Córka", FamilyRole.primary, phone="+48500600700",
                      dnd_start=22, dnd_end=7)
    notifs = family.dispatch(s, SemaphoreLevel.purple, title="KRYZYS",
                             body="Halina — ból w klatce", hour=3)
    assert len(notifs) == 1 and notifs[0].status.value == "sent"

    # 7. Payload 112 (F17)
    payload = EmergencyService(session).build_payload(s, reason="ból w klatce + duszność")
    assert payload.age >= 80
    assert "Kwiatowa" in (payload.address or "")
    assert "ból w klatce" in payload.dispatch_summary()


def test_e2e_routine_green(session):
    s = _senior(session)
    detector = CrisisDetector()
    detections = detector.detect_text("Dzień dobry, wszystko w porządku, dziękuję że dzwonicie")
    assert detections == []
    cls = detector.to_classification(detections)
    assert cls.level == SemaphoreLevel.green

    engine = SemaphoreEngine(session)
    engine.apply(s, cls)
    assert s.semaphore == SemaphoreLevel.green

    # rutyna → brak powiadomień, brak eskalacji
    family = FamilyService(session, adapters={"sms": SmsAdapter()})
    family.add_member(s, "Syn", FamilyRole.primary, phone="+48500600700")
    assert family.dispatch(s, SemaphoreLevel.green, title="OK", body="rutyna") == []
    assert EscalationLadder().plan(SemaphoreLevel.green) == []


def test_e2e_yellow_no_downgrade_from_red(session):
    """State machine: po RED żółty sygnał nie obniża poziomu bez resolve."""
    s = _senior(session)
    engine = SemaphoreEngine(session)
    detector = CrisisDetector()

    # najpierw RED (upadek)
    red_cls = detector.to_classification(detector.detect_text("przewróciłem się i nie mogę wstać"))
    engine.apply(s, red_cls)
    assert s.semaphore == SemaphoreLevel.red

    # potem YELLOW (gorszy nastrój) — poziom NIE spada
    yellow_cls = detector.to_classification(detector.detect_text("jestem trochę smutny"))
    engine.apply(s, yellow_cls)
    assert s.semaphore == SemaphoreLevel.red

    # dopiero jawny resolve
    engine.resolve(s, note="koordynator potwierdził — fałszywy alarm")
    assert s.semaphore == SemaphoreLevel.green
