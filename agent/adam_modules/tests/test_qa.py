"""Testy F15 — QA (metryki jakości rozmów)."""
from adam_modules.qa import QAEvaluator, Turn


def _good_conversation():
    return [
        Turn("adam", "Dzień dobry, tu Adam, jestem cyfrowym asystentem, nie jestem człowiekiem."),
        Turn("senior", "Dzień dobry.", asr_confidence=0.95),
        Turn("adam", "Jak się Pan dziś czuje?"),
        Turn("senior", "Całkiem dobrze, dziękuję.", asr_confidence=0.9),
        Turn("adam", "Cieszę się. Czy wziął Pan leki?"),
        Turn("senior", "Tak, rano.", asr_confidence=0.92),
    ]


def test_good_conversation_high_score():
    qa = QAEvaluator()
    r = qa.evaluate(_good_conversation(), duration_s=120, interruptions=0, completed=True)
    assert r.score > 75
    assert "brak_ujawnienia_AI" not in r.flags
    assert qa.needs_human_review(r) is False


def test_missing_disclosure_flags_review():
    qa = QAEvaluator()
    turns = [
        Turn("adam", "Jak się Pan czuje?"),
        Turn("senior", "Dobrze.", asr_confidence=0.9),
    ]
    r = qa.evaluate(turns, completed=True)
    assert "brak_ujawnienia_AI" in r.flags
    assert qa.needs_human_review(r) is True


def test_low_asr_flag():
    qa = QAEvaluator()
    turns = [
        Turn("adam", "Tu Adam, jestem cyfrowym asystentem."),
        Turn("senior", "...", asr_confidence=0.3),
        Turn("senior", "co?", asr_confidence=0.4),
    ]
    r = qa.evaluate(turns, completed=True)
    assert "niska_jakosc_ASR" in r.flags


def test_incomplete_conversation():
    qa = QAEvaluator()
    r = qa.evaluate(_good_conversation(), completed=False)
    assert "rozmowa_niezakonczona" in r.flags
    assert qa.needs_human_review(r) is True


def test_interruptions_flag():
    qa = QAEvaluator()
    r = qa.evaluate(_good_conversation(), interruptions=3, completed=True)
    assert "liczne_przerwania" in r.flags


def test_metrics_populated():
    qa = QAEvaluator()
    r = qa.evaluate(_good_conversation(), duration_s=100, completed=True)
    assert r.metrics["turns"] == 6
    assert r.metrics["disclosed"] is True
    assert 0 <= r.metrics["senior_ratio"] <= 1
