"""Testy warstwy głosowej (ETAP 12): porty, DialogEngine, kanał ARI, endpoint.

Cały tor jest bez sieci i bez audio — EchoASR/RuleLLM/TextTTS + FakeChannel
sterowany skryptem. Endpoint `/api/voice/simulate-call` testowany TestClientem
na SQLite in-memory (ten sam wzorzec co test_api.py).

Uwaga o detektorze kryzysu (F3): mapa fraz jest stała i poza zakresem tej
warstwy. W testach kryzysu używamy fraz, które istniejący detektor faktycznie
rozpoznaje (np. „klatce piersiowej" → chest_pain). Warstwa głosowa jedynie
poprawnie propaguje wynik detektora.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from adam_modules.common import db as db_mod
from adam_modules.api import create_app
from adam_modules.semaphore.models import SemaphoreLevel
from adam_modules.speech.profile import HearingLevel, CognitivePace
from adam_modules.voice import (
    EchoASR, RuleLLM, TextTTS, Transcript, LLMReply, Utterance,
    DialogEngine, DialogState, Speaker, CallOutcome,
    FakeChannel, CallSession,
)


# ============================================================ porty (dev impls)

def test_echo_asr_strips_say_prefix():
    asr = EchoASR()
    t = asr.transcribe("say:Dzień dobry")
    assert isinstance(t, Transcript)
    assert t.text == "Dzień dobry"
    assert t.is_final is True


def test_echo_asr_passthrough_without_prefix():
    assert EchoASR().transcribe("  Halo  ").text == "Halo"


def test_rule_llm_farewell_finishes():
    r = RuleLLM().reply(system_prompt="", history=[], user_text="Do widzenia")
    assert isinstance(r, LLMReply)
    assert r.finished is True
    assert r.meta["intent"] == "farewell"


def test_rule_llm_wellbeing_and_meds_and_reprompt():
    llm = RuleLLM()
    assert llm.reply(system_prompt="", history=[], user_text="Czuję się dobrze").meta["intent"] == "wellbeing_ok"
    assert llm.reply(system_prompt="", history=[], user_text="Wziąłem tabletki").meta["intent"] == "medication"
    assert llm.reply(system_prompt="", history=[], user_text="").meta["intent"] == "reprompt"
    assert llm.reply(system_prompt="", history=[], user_text="hmm").meta["intent"] == "followup"
    # domyślna kontynuacja nie kończy rozmowy
    assert llm.reply(system_prompt="", history=[], user_text="hmm").finished is False


def test_text_tts_carries_speech_params():
    utt = TextTTS().synthesize("Halo", rate_wpm=110, volume_db=6.0)
    assert isinstance(utt, Utterance)
    assert utt.text == "Halo"
    assert utt.audio_ref.startswith("tts:")
    assert utt.rate_wpm == 110
    assert utt.volume_db == 6.0


# ============================================================ DialogEngine

def test_engine_open_emits_ai_disclosure():
    eng = DialogEngine(RuleLLM(), senior_name="Jan", senior_age=80)
    assert eng.state == DialogState.INIT
    turn = eng.open()
    assert eng.state == DialogState.DISCLOSED
    assert turn.speaker == Speaker.ADAM
    assert eng.outcome.disclosure_said is True
    # ujawnienie to pierwsza tura
    assert eng.outcome.turns[0] is turn


def test_engine_handle_user_before_open_raises():
    eng = DialogEngine(RuleLLM())
    with pytest.raises(ValueError):
        eng.handle_user("cokolwiek")


def test_engine_normal_flow_and_farewell_closes():
    eng = DialogEngine(RuleLLM(), senior_name="Anna", senior_age=78)
    eng.open()
    t1 = eng.handle_user("Czuję się dobrze")
    assert eng.state == DialogState.ACTIVE
    assert t1.speaker == Speaker.ADAM
    t2 = eng.handle_user("Do widzenia")
    assert eng.state == DialogState.CLOSED
    assert t2.text  # pożegnalna odpowiedź Adama
    assert eng.outcome.max_level == SemaphoreLevel.green
    assert eng.outcome.escalated is False


def test_engine_green_turn_has_no_trigger():
    eng = DialogEngine(RuleLLM())
    eng.open()
    eng.handle_user("Wszystko w porządku")
    senior_turns = [t for t in eng.outcome.turns if t.speaker == Speaker.SENIOR]
    assert senior_turns[-1].level == SemaphoreLevel.green
    assert senior_turns[-1].trigger is None


def test_engine_crisis_escalates_and_interrupts():
    eng = DialogEngine(RuleLLM(), senior_name="Jan", senior_age=82)
    eng.open()
    turn = eng.handle_user("Mam silny ból w klatce piersiowej")
    assert eng.state == DialogState.ESCALATING
    assert eng.outcome.escalated is True
    assert eng.outcome.max_level in (SemaphoreLevel.red, SemaphoreLevel.purple)
    assert eng.outcome.top_trigger is not None
    # komunikat eskalacyjny, nie zwykła odpowiedź LLM
    assert "112" in turn.text or "służb" in turn.text or "zespół" in turn.text.lower() or "przekazuję" in turn.text


def test_engine_close_is_idempotent_after_farewell():
    eng = DialogEngine(RuleLLM())
    eng.open()
    eng.handle_user("koniec")            # farewell → CLOSED
    assert eng.state == DialogState.CLOSED
    last = eng.outcome.turns[-1]
    again = eng.close()                  # nie tworzy nowej tury
    assert again is last


def test_engine_speech_profile_scales_wpm_and_volume():
    # słabszy słuch → wolniejsze tempo i głośniej niż domyślnie
    strong = DialogEngine(RuleLLM(), senior_age=90, hearing=HearingLevel.severe_loss,
                          pace=CognitivePace.very_slow)
    mild = DialogEngine(RuleLLM(), senior_age=70, hearing=HearingLevel.normal,
                        pace=CognitivePace.normal)
    assert strong.rate_wpm == int(round(140 * strong.profile.speech_rate))
    assert strong.rate_wpm <= mild.rate_wpm
    assert strong.volume_db >= mild.volume_db


# ============================================================ FakeChannel + CallSession

def test_fake_channel_scripts_and_hangup():
    ch = FakeChannel(script=["Dzień dobry", "Do widzenia"])
    assert ch.record_utterance() == "say:Dzień dobry"
    assert ch.record_utterance() == "say:Do widzenia"
    assert ch.record_utterance() is None      # skrypt wyczerpany
    ch.play("tts:coś")
    assert ch.played == ["tts:coś"]
    ch.hangup()
    assert ch.hung_up is True


def test_call_session_full_normal_run():
    eng = DialogEngine(RuleLLM(), senior_name="Maria", senior_age=76)
    ch = FakeChannel(script=["Czuję się dobrze", "Do widzenia"])
    outcome = CallSession(ch, eng).run()
    assert isinstance(outcome, CallOutcome)
    assert outcome.disclosure_said is True
    assert outcome.escalated is False
    assert ch.hung_up is True
    # co najmniej: ujawnienie + odpowiedzi Adama zostały odtworzone
    assert len(ch.played) >= 2
    # transkrypcja zawiera obu rozmówców
    tr = outcome.transcript()
    assert "senior:" in tr and "adam:" in tr


def test_call_session_stops_on_crisis():
    eng = DialogEngine(RuleLLM(), senior_age=84)
    ch = FakeChannel(script=["Nie mogę oddychać", "cokolwiek dalej"])
    outcome = CallSession(ch, eng).run()
    # outcome.escalated to trwały sygnał kryzysu; stan silnika po run() zostaje
    # domknięty (close() na końcu sesji), więc sprawdzamy flagę wyniku.
    assert outcome.escalated is True
    assert outcome.max_level in (SemaphoreLevel.red, SemaphoreLevel.purple)
    assert ch.hung_up is True
    # druga wypowiedź nie została przetworzona (przerwanie na kryzysie)
    senior_turns = [t for t in outcome.turns if t.speaker == Speaker.SENIOR]
    assert len(senior_turns) == 1


def test_call_session_respects_max_turns():
    eng = DialogEngine(RuleLLM(), senior_age=75)
    # same neutralne wypowiedzi → nigdy nie kończy; max_turns ucina pętlę
    ch = FakeChannel(script=["hmm"] * 50)
    outcome = CallSession(ch, eng, max_turns=3).run()
    senior_turns = [t for t in outcome.turns if t.speaker == Speaker.SENIOR]
    assert len(senior_turns) == 3
    assert ch.hung_up is True


# ============================================================ endpoint /api/voice

@pytest.fixture()
def client():
    db_mod.init_engine("sqlite:///:memory:")
    app = create_app(init_db=True)
    with TestClient(app) as c:
        yield c


def _make_senior(client, first="Jan", last="Kowalski"):
    r = client.post("/api/seniors", json={
        "first_name": first, "last_name": last,
        "birth_date": "1945-03-01", "address": "ul. Sołacka 5, Poznań",
        "district": "Jeżyce",
    })
    assert r.status_code == 201, r.text
    return r.json()


def test_simulate_call_404_when_senior_missing(client):
    r = client.post("/api/voice/simulate-call", json={
        "senior_external_id": "SR-NOPE", "utterances": ["Dzień dobry"],
    })
    assert r.status_code == 404


def test_simulate_call_normal_dialog(client):
    s = _make_senior(client)
    ext = s["external_id"]
    r = client.post("/api/voice/simulate-call", json={
        "senior_external_id": ext,
        "utterances": ["Czuję się dobrze", "Do widzenia"],
        "hearing": "moderate_loss",
        "pace": "slow",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["senior_external_id"] == ext
    assert body["disclosure_said"] is True
    assert body["escalated"] is False
    assert body["max_level"] == "green"
    assert body["rate_wpm"] > 0
    # pierwsza tura Adama = ujawnienie AI
    assert body["turns"][0]["speaker"] == "adam"
    assert any(t["speaker"] == "senior" for t in body["turns"])


def test_simulate_call_crisis_escalates(client):
    s = _make_senior(client, first="Halina")
    ext = s["external_id"]
    r = client.post("/api/voice/simulate-call", json={
        "senior_external_id": ext,
        "utterances": ["Mam silny ból w klatce piersiowej"],
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["escalated"] is True
    assert body["max_level"] in ("red", "purple")
    assert body["top_trigger"] is not None
