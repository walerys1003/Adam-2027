"""Testy produkcyjnej ścieżki głosowej (ETAP 17).

Pokrywa:
- `CrisisConsensus` (F3 detektor + głos LLM → F16 fail-safe): zgodność,
  podniesienie czujności przez LLM, degradacja bez LLM, odporność na błąd LLM;
- `RuleLLM.classify` (niezależny głos klasyfikacyjny);
- `DialogEngine` z konsensusem: eskalacja gdy LLM łapie sygnał pominięty przez
  detektor + `outcome.needs_review`;
- `AsteriskAriChannel`: mapowanie audio, no-op bez URL, akcje z atrapą httpx,
  **fail-safe** przy błędach HTTP.
"""
from __future__ import annotations

import pytest

from adam_modules.semaphore.models import SemaphoreLevel, Trigger
from adam_modules.voice import (
    RuleLLM, LLMClassification, CrisisConsensus,
    DialogEngine, DialogState, AsteriskAriChannel, FakeChannel, CallSession,
)


# ============================================================ RuleLLM.classify

def test_rulellm_classify_green_for_neutral():
    v = RuleLLM().classify(text="Dzień dobry, u mnie spokojnie")
    assert v.level == SemaphoreLevel.green
    assert v.trigger == Trigger.routine_ok


def test_rulellm_classify_detects_yellow_mood():
    v = RuleLLM().classify(text="Jest mi dziś smutno i samotnie")
    assert v.level == SemaphoreLevel.yellow


def test_rulellm_classify_detects_purple():
    v = RuleLLM().classify(text="Chyba tracę przytomność")
    assert v.level == SemaphoreLevel.purple


# ============================================================ CrisisConsensus

def test_consensus_agreement_on_hard_signal():
    # „ból w klatce" — detektor łapie chest_pain (purple); oba głosy krytyczne
    r = CrisisConsensus(RuleLLM()).assess("Mam silny ból w klatce piersiowej")
    assert r.level == SemaphoreLevel.purple
    assert r.is_critical
    assert "rule_detector" in r.sources and "llm" in r.sources


def test_consensus_llm_raises_alarm_detector_misses():
    # „krwawię/tracę przytomność" NIE są w słowniku detektora (zwróciłby green),
    # ale LLM je łapie → konsensus fail-safe podnosi poziom i oznacza needs_review.
    r = CrisisConsensus(RuleLLM()).assess("Krwawię mocno i tracę przytomność")
    assert r.level in (SemaphoreLevel.red, SemaphoreLevel.purple)
    assert r.needs_review is True


def test_consensus_degrades_without_llm_vote():
    # use_llm=False → tylko detektor. Neutralne zdanie = green, jedno źródło.
    r = CrisisConsensus(RuleLLM(), use_llm=False).assess("Wszystko w porządku")
    assert r.level == SemaphoreLevel.green
    assert r.sources == ["rule_detector"]


class _BrokenLLM:
    """LLM, którego classify rzuca — konsensus musi to znieść (fail-safe)."""
    def reply(self, *, system_prompt, history, user_text):  # pragma: no cover
        raise AssertionError("nieużywane w teście")

    def classify(self, *, text):
        raise RuntimeError("model down")


def test_consensus_survives_llm_error():
    r = CrisisConsensus(_BrokenLLM()).assess("Mam silny ból w klatce piersiowej")
    # LLM padł → zostaje głos detektora (nadal łapie chest_pain = purple)
    assert r.level == SemaphoreLevel.purple
    assert r.sources == ["rule_detector"]


# ============================================================ DialogEngine + konsensus

def test_engine_escalates_when_llm_catches_missed_signal():
    eng = DialogEngine(RuleLLM(), senior_name="Jan", senior_age=82)
    eng.open()
    eng.handle_user("Krwawię mocno i tracę przytomność")
    assert eng.state == DialogState.ESCALATING
    assert eng.outcome.escalated is True
    assert eng.outcome.needs_review is True
    assert eng.outcome.max_level in (SemaphoreLevel.red, SemaphoreLevel.purple)


def test_engine_no_false_escalation_on_wellbeing():
    eng = DialogEngine(RuleLLM(), senior_age=75)
    eng.open()
    eng.handle_user("Czuję się dobrze, dziękuję")
    assert eng.state == DialogState.ACTIVE
    assert eng.outcome.escalated is False
    assert eng.outcome.max_level == SemaphoreLevel.green


def test_engine_consensus_can_be_disabled():
    # bez konsensusu — zachowanie z ETAP 12 (sam detektor)
    eng = DialogEngine(RuleLLM(), senior_age=80, use_consensus=False)
    eng.open()
    # fraza spoza słownika detektora → detektor sam da green (brak eskalacji)
    eng.handle_user("Krwawię mocno i tracę przytomność")
    assert eng.outcome.escalated is False


# ============================================================ AsteriskAriChannel

def test_asterisk_media_uri_mapping():
    f = AsteriskAriChannel._to_media_uri
    assert f("tts:Dzień dobry").startswith("sound:")
    assert f("say:Halo") == "sound:Halo"
    assert f("sound:hello") == "sound:hello"  # bez zmian


def test_asterisk_noop_without_url_never_raises():
    ch = AsteriskAriChannel("CH-1")  # brak ASTERISK_ARI_URL
    ch.play("tts:cześć")
    assert ch.record_utterance() is None
    ch.hangup()  # nie rzuca


class _FakeHttp:
    """Atrapa httpx.Client rejestrująca wywołania."""
    def __init__(self, *, fail=False):
        self.fail = fail
        self.calls: list[tuple[str, str]] = []

    def post(self, url, params=None, auth=None):
        self.calls.append(("POST", url))
        if self.fail:
            raise ConnectionError("network down")
        return None

    def delete(self, url, auth=None):
        self.calls.append(("DELETE", url))
        if self.fail:
            raise ConnectionError("network down")
        return None


def test_asterisk_actions_hit_http_client():
    http = _FakeHttp()
    ch = AsteriskAriChannel("CH-9", base_url="http://asterisk:8088/ari",
                            username="u", password="p", http_client=http)
    ch.play("tts:Dzień dobry")
    ref = ch.record_utterance()
    ch.hangup()
    assert ref is not None and ref.startswith("record:")
    methods = [m for m, _ in http.calls]
    assert methods == ["POST", "POST", "DELETE"]  # play, record, hangup
    assert http.calls[-1][1].endswith("/channels/CH-9")


def test_asterisk_failsafe_on_http_errors():
    http = _FakeHttp(fail=True)
    ch = AsteriskAriChannel("CH-err", base_url="http://asterisk:8088/ari",
                            http_client=http)
    # żadna akcja nie może rzucić mimo błędów sieci
    ch.play("tts:x")
    assert ch.record_utterance() is None   # błąd nagrania → None (bezpiecznie)
    ch.hangup()


def test_call_session_runs_over_asterisk_adapter():
    # pełen tor z adapterem no-op: record_utterance() = None natychmiast,
    # więc sesja robi ujawnienie AI i domyka rozmowę bez błędu.
    from adam_modules.voice import DialogEngine as DE
    eng = DE(RuleLLM(), senior_age=77)
    ch = AsteriskAriChannel("CH-2")  # no-op (brak URL) → record zwraca None
    outcome = CallSession(ch, eng).run()
    assert outcome.disclosure_said is True
    # brak wypowiedzi seniora → brak eskalacji
    assert outcome.escalated is False
