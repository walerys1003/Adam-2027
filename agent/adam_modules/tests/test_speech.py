"""Testy F14 — optymalizacja mowy senioralnej (audio profile)."""
from adam_modules.speech import (
    build_speech_profile, HearingLevel, CognitivePace, SpeechProfile,
)


def test_normal_profile():
    p = build_speech_profile(HearingLevel.normal, CognitivePace.normal)
    assert p.speech_rate == 1.0
    assert p.volume_gain_db == 0.0
    assert p.repeat_key_points is False


def test_hearing_loss_increases_gain():
    mild = build_speech_profile(HearingLevel.mild_loss)
    severe = build_speech_profile(HearingLevel.severe_loss)
    assert severe.volume_gain_db > mild.volume_gain_db
    assert severe.speech_rate < 1.0
    assert severe.repeat_key_points is True
    assert severe.simple_language is True


def test_slow_pace_adds_pauses():
    p = build_speech_profile(pace=CognitivePace.very_slow)
    assert p.pause_ms > 400
    assert p.speech_rate < 1.0
    assert p.simple_language is True


def test_age_85_simplifies():
    p = build_speech_profile(age=88)
    assert p.simple_language is True


def test_rate_never_below_floor():
    p = build_speech_profile(HearingLevel.severe_loss, CognitivePace.very_slow, age=90)
    assert p.speech_rate >= 0.6
    assert p.volume_gain_db <= 12.0
    assert 300 <= p.pause_ms <= 1500


def test_describe_and_dict():
    p = build_speech_profile(HearingLevel.moderate_loss, CognitivePace.slow)
    d = p.to_dict()
    assert "speech_rate" in d and "pause_ms" in d
    desc = p.describe()
    assert "tempo" in desc
