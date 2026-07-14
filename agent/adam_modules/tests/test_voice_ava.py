"""ETAP 33 — funkcje głosowe AVA: Silence Watchdog, barge-in, nagrania, dual-STT.

Cały tor deterministyczny (bez sieci/audio): sygnały czasu/energii wstrzykiwane.
"""
import pytest

from adam_modules.voice import (
    SilenceWatchdog, SilenceConfig, SilenceAction,
    BargeInController, BargeInConfig,
    RecordingRegistry, DualStt, DualSttResult,
    CallSession, FakeChannel, DialogEngine, RuleLLM, DialogState, EchoASR,
)
from adam_modules.voice.ports import Transcript
from adam_modules.consensus.engine import VoterRole
from adam_modules.semaphore.models import SemaphoreLevel


# ============================================================ Silence Watchdog

def test_silence_watchdog_waits_in_grace():
    wd = SilenceWatchdog(SilenceConfig(grace_s=6, reprompt_s=10))
    ev = wd.observe_silence(3.0)
    assert ev.action == SilenceAction.wait
    assert wd.reprompts == 0


def test_silence_watchdog_reprompts_then_escalates():
    wd = SilenceWatchdog(SilenceConfig(grace_s=6, reprompt_s=10, max_reprompts=2))
    assert wd.observe_silence(11).action == SilenceAction.reprompt
    assert wd.observe_silence(11).action == SilenceAction.reprompt
    ev = wd.observe_silence(11)
    assert ev.action == SilenceAction.escalate
    assert wd.escalated is True


def test_silence_watchdog_hard_threshold_escalates_immediately():
    wd = SilenceWatchdog(SilenceConfig(hard_silence_s=30))
    ev = wd.observe_silence(31)
    assert ev.action == SilenceAction.escalate
    assert wd.escalated is True


def test_silence_watchdog_reset_clears_reprompts():
    wd = SilenceWatchdog(SilenceConfig(grace_s=6, reprompt_s=10))
    wd.observe_silence(11)
    assert wd.reprompts == 1
    wd.reset()
    assert wd.reprompts == 0


# ============================================================ Barge-in

def test_barge_in_detects_speech_over_tts():
    bi = BargeInController(BargeInConfig(energy_threshold=0.02, min_voiced_frames=3))
    r = bi.scan([0.0, 0.001, 0.05, 0.06, 0.07, 0.08])
    assert r.interrupted is True
    assert r.at_frame == 2


def test_barge_in_ignores_short_noise():
    bi = BargeInController(BargeInConfig(energy_threshold=0.02, min_voiced_frames=3))
    r = bi.scan([0.05, 0.0, 0.05, 0.0, 0.05])  # brak 3 z rzędu
    assert r.interrupted is False


def test_barge_in_silence_no_interrupt():
    bi = BargeInController()
    r = bi.scan([0.0, 0.0, 0.0])
    assert r.interrupted is False
    assert r.voiced_frames == 0


# ============================================================ Recordings (RODO)

def test_recording_registry_denies_without_consent():
    reg = RecordingRegistry(consent=False)
    assert reg.register("call-1", "audio-ref-1") is None
    assert reg.denied_count == 1
    assert reg.refs() == []


def test_recording_registry_stores_with_consent():
    reg = RecordingRegistry(consent=True)
    ref = reg.register("call-1", "audio-ref-1", seconds=4.2)
    assert ref is not None
    assert ref.consented is True
    assert ref.seconds == 4.2
    assert len(reg.refs()) == 1


# ============================================================ Dual-STT

class _SecondaryASR:
    """Drugi, niezależny STT — zwraca podany tekst niezależnie od audio."""
    def __init__(self, text: str, *, fail: bool = False):
        self._text = text
        self._fail = fail

    def transcribe(self, audio_ref: str) -> Transcript:
        if self._fail:
            raise RuntimeError("secondary STT down")
        return Transcript(text=self._text, confidence=0.9)


def test_dual_stt_agreement_no_disagreement():
    dual = DualStt(EchoASR(), _SecondaryASR("Dzień dobry"))
    res = dual.transcribe("say:Dzień dobry")
    assert isinstance(res, DualSttResult)
    assert res.disagreement is False
    assert res.text == "Dzień dobry"
    roles = {v.role for v in res.votes}
    assert VoterRole.stt_primary in roles
    assert VoterRole.stt_secondary in roles


def test_dual_stt_disagreement_flagged():
    dual = DualStt(EchoASR(), _SecondaryASR("coś zupełnie innego"))
    res = dual.transcribe("say:Dzień dobry")
    assert res.disagreement is True
    assert res.text == "Dzień dobry"  # tekst wiodący zawsze z primary


def test_dual_stt_secondary_failure_is_failsafe():
    dual = DualStt(EchoASR(), _SecondaryASR("x", fail=True))
    res = dual.transcribe("say:Dzień dobry")
    assert res.secondary is None
    assert res.disagreement is False
    assert res.text == "Dzień dobry"
    assert len(res.votes) == 1  # tylko primary


def test_dual_stt_without_secondary():
    dual = DualStt(EchoASR())
    res = dual.transcribe("say:Nie mogę oddychać")
    assert res.secondary is None
    assert len(res.votes) == 1


def test_dual_stt_voter_feeds_consensus():
    dual = DualStt(EchoASR(), _SecondaryASR("Nie mogę oddychać"))
    voters = dual.voters()
    assert len(voters) == 1
    vote = voters[0]("Nie mogę oddychać")
    assert vote is not None
    assert vote.role == VoterRole.stt_secondary


# ============================================================ CallSession integration

def test_call_session_silence_reprompt_then_continue():
    eng = DialogEngine(RuleLLM(), senior_name="Jan", senior_age=80)
    # tura ciszy (None), potem senior się odzywa i żegna
    ch = FakeChannel(
        script=[None, "Czuję się dobrze", "Do widzenia"],
        silence_seconds=[11.0, 0.0, 0.0],
    )
    wd = SilenceWatchdog(SilenceConfig(grace_s=6, reprompt_s=10, max_reprompts=2))
    outcome = CallSession(ch, eng, watchdog=wd, max_turns=10).run()
    # ponaglenie zostało wypowiedziane
    assert outcome.silence_reprompts >= 1
    assert ch.hung_up is True


def test_call_session_silence_escalates_no_contact():
    eng = DialogEngine(RuleLLM(), senior_name="Anna")
    ch = FakeChannel(
        script=[None, None, None],
        silence_seconds=[11.0, 11.0, 11.0],
    )
    wd = SilenceWatchdog(SilenceConfig(grace_s=6, reprompt_s=10, max_reprompts=2))
    session = CallSession(ch, eng, watchdog=wd, max_turns=10)
    outcome = session.run()
    assert session.silence_escalated is True
    assert outcome.no_contact is True
    assert outcome.escalated is True


def test_call_session_records_with_consent():
    eng = DialogEngine(RuleLLM(), senior_name="Jan")
    ch = FakeChannel(script=["Czuję się dobrze", "Do widzenia"])
    reg = RecordingRegistry(consent=True)
    CallSession(ch, eng, recordings=reg).run()
    assert len(reg.refs()) >= 1


def test_call_session_no_recording_without_consent():
    eng = DialogEngine(RuleLLM(), senior_name="Jan")
    ch = FakeChannel(script=["Czuję się dobrze", "Do widzenia"])
    reg = RecordingRegistry(consent=False)
    CallSession(ch, eng, recordings=reg).run()
    assert reg.refs() == []
    assert reg.denied_count >= 1


def test_call_session_barge_in_stops_tts():
    eng = DialogEngine(RuleLLM(), senior_name="Jan")
    # senior przerywa na turze index 0 (otwarcie) — Adam milknie
    ch = FakeChannel(
        script=["Czuję się dobrze", "Do widzenia"],
        interrupt_at={0},
    )
    session = CallSession(ch, eng)
    session.run()
    assert session.barge_ins >= 1
    assert len(ch.stopped) >= 1


def test_call_session_dual_stt_used_for_transcription():
    eng = DialogEngine(RuleLLM(), senior_name="Jan")
    ch = FakeChannel(script=["Czuję się dobrze", "Do widzenia"])
    dual = DualStt(EchoASR(), _SecondaryASR("zupełnie co innego"))
    session = CallSession(ch, eng, dual_stt=dual)
    session.run()
    # primary decyduje o treści → rozmowa działa; rozbieżności policzone
    assert session.stt_disagreements >= 1


def test_call_session_backward_compat_no_features():
    """Bez watchdog/dual/recordings zachowanie jak dotąd (cisza = koniec)."""
    eng = DialogEngine(RuleLLM(), senior_name="Jan")
    ch = FakeChannel(script=["Czuję się dobrze", "Do widzenia"])
    outcome = CallSession(ch, eng).run()
    assert ch.hung_up is True
    assert outcome.disclosure_said is True
