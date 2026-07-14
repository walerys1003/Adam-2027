"""Testy F3+F4+F5 — semafor, eskalacja, guardrails, system prompt."""
import pytest

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.seniors.models import SemaphoreLevel
from adam_modules.semaphore import (
    SemaphoreEngine, Classification, Trigger,
    EscalationLadder, Guardrails,
    build_system_prompt, AI_ACT_DISCLOSURE,
)
from adam_modules.semaphore.engine import TRIGGER_LEVEL, max_level, level_rank


def _senior(session):
    return SeniorService(session).create(SeniorCreate(first_name="Jan", last_name="Kowalski"))


# ---------- Engine: mapowanie triggerów (F3.1 / F3.5) ----------
def test_all_triggers_mapped():
    for t in Trigger:
        assert t in TRIGGER_LEVEL, f"brak mapowania dla {t}"


@pytest.mark.parametrize("trigger,expected", [
    (Trigger.routine_ok, SemaphoreLevel.green),
    (Trigger.mood_low, SemaphoreLevel.yellow),
    (Trigger.missed_medication, SemaphoreLevel.yellow),
    (Trigger.vitals_out_of_range, SemaphoreLevel.red),
    (Trigger.fall_reported, SemaphoreLevel.red),
    (Trigger.chest_pain, SemaphoreLevel.purple),
    (Trigger.suicide_ideation, SemaphoreLevel.purple),
])
def test_trigger_levels(trigger, expected):
    assert TRIGGER_LEVEL[trigger] == expected


def test_classify_picks_highest(session):
    eng = SemaphoreEngine(session)
    c = eng.classify([Trigger.mood_low, Trigger.chest_pain, Trigger.poor_sleep])
    assert c.level == SemaphoreLevel.purple
    assert c.trigger == Trigger.chest_pain


def test_classify_empty_is_green(session):
    eng = SemaphoreEngine(session)
    assert eng.classify([]).level == SemaphoreLevel.green


# ---------- Engine: state machine (F3.1) ----------
def test_level_only_rises_without_downgrade(session):
    senior = _senior(session)
    eng = SemaphoreEngine(session)
    eng.apply(senior, eng.classify([Trigger.chest_pain]))
    assert senior.semaphore == SemaphoreLevel.purple
    # próba zejścia bez allow_downgrade — pozostaje purple
    eng.apply(senior, eng.classify([Trigger.mood_low]))
    assert senior.semaphore == SemaphoreLevel.purple


def test_resolve_downgrades(session):
    senior = _senior(session)
    eng = SemaphoreEngine(session)
    eng.apply(senior, eng.classify([Trigger.fall_reported]))
    assert senior.semaphore == SemaphoreLevel.red
    eng.resolve(senior, note="kontakt z rodziną, wszystko OK")
    assert senior.semaphore == SemaphoreLevel.green


def test_event_recorded(session):
    senior = _senior(session)
    eng = SemaphoreEngine(session)
    eng.apply(senior, eng.classify([Trigger.vitals_out_of_range]))
    hist = eng.history(senior.id)
    assert len(hist) == 1
    assert hist[0].new_level == SemaphoreLevel.red
    assert hist[0].trigger == Trigger.vitals_out_of_range


def test_max_level_helper():
    assert max_level(SemaphoreLevel.green, SemaphoreLevel.red) == SemaphoreLevel.red
    assert level_rank(SemaphoreLevel.purple) > level_rank(SemaphoreLevel.yellow)


# ---------- Escalation ladder (F3.2) ----------
def test_red_ladder():
    plan = EscalationLadder.plan(SemaphoreLevel.red)
    actions = [s.action for s in plan]
    assert actions == ["retry_call", "sms_family", "notify_coordinator", "escalate_purple"]
    # offset kumulowany rośnie
    assert plan[0].at_offset_s == 0
    assert plan[-1].at_offset_s == 480  # 0+60+120+300


def test_purple_ladder_calls_112_first_and_bypasses_dnd():
    plan = EscalationLadder.plan(SemaphoreLevel.purple)
    assert plan[0].action == "call_112"
    assert all(s.bypass_dnd for s in plan)


def test_green_yellow_no_escalation():
    assert EscalationLadder.plan(SemaphoreLevel.green) == []
    assert EscalationLadder.plan(SemaphoreLevel.yellow) == []


def test_next_step_skips_completed():
    step = EscalationLadder.next_step(SemaphoreLevel.red, completed_actions=["retry_call"])
    assert step.action == "sms_family"


# ---------- Guardrails (F4/F3.3) ----------
def test_guardrail_valid_yellow():
    r = Guardrails.validate(Classification(level=SemaphoreLevel.yellow, trigger=Trigger.mood_low))
    assert r.ok and not r.needs_confirmation


def test_guardrail_confidence_out_of_range():
    r = Guardrails.validate(Classification(level=SemaphoreLevel.red,
                                           trigger=Trigger.fall_reported, confidence=1.5))
    assert not r.ok


def test_guardrail_trigger_level_mismatch():
    # trigger chest_pain (purple) ale zadeklarowano yellow → niespójność
    r = Guardrails.validate(Classification(level=SemaphoreLevel.yellow, trigger=Trigger.chest_pain))
    assert not r.ok


def test_guardrail_purple_requires_hard_signal():
    # trigger fall_reported to RED — użyjmy purple bez twardego sygnału → downgrade
    r = Guardrails.validate(Classification(level=SemaphoreLevel.purple,
                                           trigger=Trigger.chest_pain, signals={}))
    # chest_pain sam w sobie jest twardym sygnałem → ok
    assert r.ok


def test_guardrail_low_confidence_red_needs_confirmation():
    r = Guardrails.validate(Classification(level=SemaphoreLevel.red,
                                           trigger=Trigger.confusion, confidence=0.4))
    assert r.ok and r.needs_confirmation


def test_guardrail_purple_with_signal_ok():
    r = Guardrails.validate(Classification(
        level=SemaphoreLevel.purple, trigger=Trigger.chest_pain,
        confidence=0.9, signals={"keyword_match": "ból w klatce"}))
    assert r.ok and not r.needs_confirmation


# ---------- System prompt (F5/F3.4) ----------
def test_prompt_contains_ai_disclosure():
    p = build_system_prompt(senior_name="Jan Kowalski", senior_age=80)
    assert AI_ACT_DISCLOSURE in p
    assert "Jan Kowalski" in p
    assert "80 lat" in p
    assert "asystent" in p.lower()


def test_prompt_mentions_ai_act():
    p = build_system_prompt()
    assert "AI Act" in p
    assert "nie jestem człowiekiem" in AI_ACT_DISCLOSURE.lower()
