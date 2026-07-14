"""Testy F8 — crisis detection (detektor sygnałów → semafor)."""
import pytest

from adam_modules.seniors.models import SemaphoreLevel
from adam_modules.semaphore import CrisisDetector, Trigger, Guardrails
from adam_modules.semaphore.detector import HARD_CRISIS_TRIGGERS


@pytest.fixture()
def det():
    return CrisisDetector()


def test_detects_chest_pain(det):
    d = det.detect_text("Panie Adamie, mam ból w klatce od rana")
    triggers = {x.trigger for x in d}
    assert Trigger.chest_pain in triggers


def test_detects_suicide_ideation(det):
    d = det.detect_text("nie chcę żyć, nie ma po co")
    assert any(x.trigger == Trigger.suicide_ideation for x in d)
    assert all(x.level == SemaphoreLevel.purple for x in d if x.trigger == Trigger.suicide_ideation)


def test_detects_fall(det):
    d = det.detect_text("przewróciłem się i nie mogę wstać")
    assert any(x.trigger == Trigger.fall_reported for x in d)


def test_yellow_signals(det):
    d = det.detect_text("nie wziąłem leków i źle śpię")
    triggers = {x.trigger for x in d}
    assert Trigger.missed_medication in triggers
    assert Trigger.poor_sleep in triggers


def test_no_signal_returns_empty(det):
    assert det.detect_text("dzień dobry, wszystko w porządku, dziękuję") == []


def test_vitals_out_of_range(det):
    d = det.detect_vitals({"heart_rate": 35, "spo2": 85})
    assert len(d) == 1
    assert d[0].trigger == Trigger.vitals_out_of_range
    assert d[0].level == SemaphoreLevel.red


def test_vitals_normal(det):
    assert det.detect_vitals({"heart_rate": 72, "spo2": 98, "systolic": 120}) == []


def test_top_trigger_picks_highest(det):
    d = det.detect("boli mnie głowa i nie mogę oddychać")  # minor + purple
    top = det.top_trigger(d)
    assert top.trigger == Trigger.breathing_difficulty
    assert top.level == SemaphoreLevel.purple


def test_to_classification_passes_guardrails(det):
    d = det.detect_text("duszę się, nie mogę oddychać")
    cls = det.to_classification(d)
    assert cls.level == SemaphoreLevel.purple
    result = Guardrails.validate(cls)
    assert result.ok is True


def test_to_classification_empty_is_green(det):
    cls = det.to_classification([])
    assert cls.level == SemaphoreLevel.green
    assert cls.trigger == Trigger.routine_ok


def test_hard_crisis_triggers_all_purple(det):
    from adam_modules.semaphore.engine import TRIGGER_LEVEL
    for trig in HARD_CRISIS_TRIGGERS:
        assert TRIGGER_LEVEL[trig] == SemaphoreLevel.purple


def test_combined_text_and_vitals(det):
    d = det.detect("nie wziąłem leków", vitals={"spo2": 84})
    triggers = {x.trigger for x in d}
    assert Trigger.missed_medication in triggers
    assert Trigger.vitals_out_of_range in triggers
