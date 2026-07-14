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


# ---- F14 (ETAP 27): macierz decyzyjna 4-stanowa + 5 głosujących ----
def test_decision_escalate_on_critical():
    from adam_modules.consensus import ConsensusEngine, ModelVote, ConsensusDecision, VoterRole
    from adam_modules.semaphore.models import SemaphoreLevel, Trigger
    votes = [
        ModelVote("rule", SemaphoreLevel.purple, Trigger.suicide_ideation, 0.9, VoterRole.stt_primary),
        ModelVote("llm", SemaphoreLevel.purple, Trigger.suicide_ideation, 0.8, VoterRole.llm_safety),
    ]
    r = ConsensusEngine().decide(votes)
    assert r.decision == ConsensusDecision.ESCALATE


def test_decision_abstain_on_no_signal_few_sources():
    from adam_modules.consensus import ConsensusEngine, ModelVote, ConsensusDecision
    from adam_modules.semaphore.models import SemaphoreLevel, Trigger
    r = ConsensusEngine().decide([ModelVote("rule", SemaphoreLevel.green, Trigger.routine_ok, 0.9)])
    assert r.decision == ConsensusDecision.ABSTAIN


def test_decision_execute_on_agreement_green():
    from adam_modules.consensus import ConsensusEngine, ModelVote, ConsensusDecision
    from adam_modules.semaphore.models import SemaphoreLevel, Trigger
    votes = [
        ModelVote("rule", SemaphoreLevel.green, Trigger.routine_ok, 0.9),
        ModelVote("llm", SemaphoreLevel.green, Trigger.routine_ok, 0.9),
    ]
    r = ConsensusEngine().decide(votes)
    assert r.decision == ConsensusDecision.EXECUTE


def test_decision_defer_on_yellow_disagreement():
    from adam_modules.consensus import ConsensusEngine, ModelVote, ConsensusDecision
    from adam_modules.semaphore.models import SemaphoreLevel, Trigger
    votes = [
        ModelVote("rule", SemaphoreLevel.yellow, Trigger.mood_low, 0.5),
        ModelVote("llm", SemaphoreLevel.green, Trigger.routine_ok, 0.6),
    ]
    r = ConsensusEngine().decide(votes)
    assert r.decision == ConsensusDecision.DEFER


def test_crisis_consensus_five_voters():
    from adam_modules.voice.consensus import CrisisConsensus
    from adam_modules.consensus import ModelVote, VoterRole
    from adam_modules.semaphore.models import SemaphoreLevel, Trigger
    from adam_modules.voice.ports import RuleLLM

    def sentiment_voter(text):
        return ModelVote("sentiment", SemaphoreLevel.yellow, Trigger.mood_low, 0.5, VoterRole.sentiment)

    def wearable_voter(text):
        return ModelVote("wearable", SemaphoreLevel.green, Trigger.routine_ok, 0.7, VoterRole.wearable)

    def stt2_voter(text):
        return ModelVote("stt2", SemaphoreLevel.green, Trigger.routine_ok, 0.8, VoterRole.stt_secondary)

    cc = CrisisConsensus(RuleLLM(), extra_voters=[sentiment_voter, wearable_voter, stt2_voter])
    res = cc.assess("czuję się trochę smutno dzisiaj")
    # 5 źródeł: rule_detector + llm + sentiment + wearable + stt2
    assert len(res.sources) == 5
    assert res.decision is not None
