"""
Testy F18 — E2E: pełny przepływ bezpieczeństwa Adama.

Scenariusz kryzysowy PURPLE łączy wszystkie moduły:
detekcja (F8) → consensus (F16) → guardrails (F4) → semafor (F3) →
eskalacja (F3.2) → powiadomienia rodziny (F9) → payload 112 (F17) →
log ujawnienia AI (F13) → audyt RODO (F12).
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
from adam_modules.rodo import RodoService, ProcessingAction
from adam_modules.medication import MedicationService, MedicationCreate, MedForm


def _senior(session):
    return SeniorService(session).create(
        SeniorCreate(
            first_name="Jan", last_name="Kowalski", phone="+48123456789",
            birth_date=date(1945, 5, 1), address="ul. Sołacka 5, Poznań", district="Sołacz",
        )
    )


def test_e2e_purple_crisis_flow(session):
    s = _senior(session)
    conv = "conv-e2e-001"

    # 0. ujawnienie AI (F13) na starcie rozmowy
    compliance = ComplianceService(session)
    compliance.record_disclosure(s, conv)
    assert compliance.assert_disclosed(conv) is True

    # opiekun + lek (kontekst dla 112)
    fam = FamilyService(session, adapters={"sms": SmsAdapter()})
    fam.add_member(s, "Anna", FamilyRole.primary, phone="+48500600700",
                   dnd_start=22, dnd_end=7)
    MedicationService(session).create(
        s, MedicationCreate(name="Ramipril", dosage="5mg", form=MedForm.tablet)
    )

    # 1. detekcja sygnału kryzysowego (F8)
    detector = CrisisDetector()
    detections = detector.detect_text("Panie Adamie, strasznie boli mnie w klatce i duszę się")
    assert detections
    cls_from_rules = detector.to_classification(detections)
    assert cls_from_rules.level == SemaphoreLevel.purple

    # 2. consensus 2 źródeł (F16): reguły + „model LLM"
    consensus = ConsensusEngine()
    result = consensus.decide([
        ModelVote("rules", cls_from_rules.level, cls_from_rules.trigger, cls_from_rules.confidence),
        ModelVote("llm_a", SemaphoreLevel.purple, cls_from_rules.trigger, 0.88),
    ])
    assert result.level == SemaphoreLevel.purple
    assert result.needs_review is False  # pełna zgodność, 2 źródła

    classification = result.to_classification()
    classification.trigger = cls_from_rules.trigger  # zachowaj konkretny trigger kryzysowy

    # 3. guardrails (F4) — PURPLE ma twardy sygnał, przechodzi
    guard = Guardrails.validate(classification)
    assert guard.ok is True

    # 4. semafor (F3) — poziom rośnie do purple, zdarzenie zapisane
    engine = SemaphoreEngine(session)
    event = engine.apply(s, classification)
    assert s.semaphore == SemaphoreLevel.purple
    assert event.id is not None

    # 5. eskalacja (F3.2) — ladder PURPLE, 112 pierwszy, wszystko bypass DND
    ladder = EscalationLadder()
    plan = ladder.plan(SemaphoreLevel.purple)
    assert plan[0].action == "call_112"
    assert all(step.bypass_dnd for step in plan)

    # 6. powiadomienia rodziny (F9) — bypass DND mimo nocy
    notifs = fam.dispatch(s, SemaphoreLevel.purple, title="KRYZYS",
                          body="Wykryto sygnały kryzysowe", hour=3)
    assert len(notifs) == 1
    assert notifs[0].status.value == "sent"

    # 7. payload 112 (F17) — kompletny
    emerg = EmergencyService(session)
    payload = emerg.build_payload(s, reason="ból w klatce + duszność")
    assert payload.age >= 80
    assert "Sołacka" in (payload.address or "")
    assert any("Ramipril" in m for m in payload.medications)
    summary = payload.dispatch_summary()
    assert "ból w klatce" in summary

    # 8. audyt RODO (F12) — przekazanie do 112 logowane
    rodo = RodoService(session)
    rodo.log(s.id, ProcessingAction.access, actor="112-dispatch",
             detail="payload przekazany do 112", legal_basis="art. 6 ust. 1 lit. d RODO")
    trail = rodo.audit_trail(s.id)
    assert any(t.actor == "112-dispatch" for t in trail)


def test_e2e_resolve_returns_to_green(session):
    s = _senior(session)
    engine = SemaphoreEngine(session)
    detector = CrisisDetector()
    cls = detector.to_classification(detector.detect_text("upadłem i nie mogę wstać"))
    engine.apply(s, cls)
    assert s.semaphore == SemaphoreLevel.red
    # koordynator rozwiązuje incydent
    engine.resolve(s, note="fałszywy alarm — senior bezpieczny")
    assert s.semaphore == SemaphoreLevel.green


def test_e2e_low_confidence_needs_review(session):
    """Rozbieżność modeli przy krytycznym → needs_review (F16 fail-safe)."""
    consensus = ConsensusEngine()
    result = consensus.decide([
        ModelVote("rules", SemaphoreLevel.red, __import__("adam_modules.semaphore.models", fromlist=["Trigger"]).Trigger.confusion, 0.6),
        ModelVote("llm_a", SemaphoreLevel.yellow, __import__("adam_modules.semaphore.models", fromlist=["Trigger"]).Trigger.mood_low, 0.7),
    ])
    assert result.level == SemaphoreLevel.red  # wyższy poziom
    assert result.needs_review is True
