"""Testy F16 — multi-model consensus."""
from adam_modules.seniors.models import SemaphoreLevel
from adam_modules.semaphore.models import Trigger
from adam_modules.consensus import ConsensusEngine, ModelVote


def test_full_agreement():
    eng = ConsensusEngine()
    votes = [
        ModelVote("rules", SemaphoreLevel.purple, Trigger.chest_pain, 0.9),
        ModelVote("llm_a", SemaphoreLevel.purple, Trigger.chest_pain, 0.85),
    ]
    r = eng.decide(votes)
    assert r.level == SemaphoreLevel.purple
    assert r.agreement == 1.0
    assert r.needs_review is False


def test_disagreement_picks_higher_level():
    eng = ConsensusEngine()
    votes = [
        ModelVote("rules", SemaphoreLevel.red, Trigger.persistent_pain, 0.8),
        ModelVote("llm_a", SemaphoreLevel.purple, Trigger.chest_pain, 0.7),
        ModelVote("llm_b", SemaphoreLevel.red, Trigger.persistent_pain, 0.75),
    ]
    r = eng.decide(votes)
    # fail-safe: wybieramy wyższy poziom mimo mniejszości
    assert r.level == SemaphoreLevel.purple
    assert r.needs_review is True
    assert any("rozbieżność" in n for n in r.notes)


def test_single_source_critical_needs_review():
    eng = ConsensusEngine()
    votes = [ModelVote("rules", SemaphoreLevel.purple, Trigger.suicide_ideation, 0.9)]
    r = eng.decide(votes)
    assert r.needs_review is True
    assert any("za mało źródeł" in n for n in r.notes)


def test_non_critical_single_source_ok():
    eng = ConsensusEngine()
    votes = [ModelVote("rules", SemaphoreLevel.yellow, Trigger.mood_low, 0.8)]
    r = eng.decide(votes)
    assert r.level == SemaphoreLevel.yellow
    assert r.needs_review is False


def test_empty_votes():
    eng = ConsensusEngine()
    r = eng.decide([])
    assert r.level == SemaphoreLevel.green
    assert r.needs_review is True


def test_to_classification():
    eng = ConsensusEngine()
    votes = [
        ModelVote("rules", SemaphoreLevel.purple, Trigger.chest_pain, 0.9),
        ModelVote("llm_a", SemaphoreLevel.purple, Trigger.chest_pain, 0.9),
    ]
    cls = eng.decide(votes).to_classification()
    assert cls.level == SemaphoreLevel.purple
    assert "consensus_agreement" in cls.signals
