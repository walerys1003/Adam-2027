"""Testy warstwy zdarzeń ARI/Stasis (ETAP 19) — pętla + webhook startu.

Wszystko offline: zdarzenia to listy słowników, kanał to FakeChannel, porty dev.
Weryfikujemy:
- build_call_session: buduje działającą sesję prowadzącą rozmowę,
- StasisApp.handle_event / run: StasisStart → rozmowa, StasisEnd/inne → pomiń,
- filtr aplikacji, fail-safe (brak channel.id, wyjątek resolvera),
- originate_call: happy-path + no-op bez originatora + fail-safe.
"""
from __future__ import annotations

from adam_modules.voice.ari import FakeChannel
from adam_modules.voice.stasis import (
    StasisApp, CallStartRequest, VoicePorts, build_call_session, originate_call,
)


def _resolver(event):
    return CallStartRequest(
        senior_external_id="SR-TEST",
        senior_name="Jan",
        senior_age=80,
    )


# ------------------------------------------------------------------ build_call_session

def test_build_call_session_runs_conversation():
    channel = FakeChannel(script=["Dzień dobry", "Czuję się dobrze", "do widzenia"])
    req = CallStartRequest(senior_external_id="SR-1", senior_name="Anna", senior_age=78)
    session = build_call_session(channel, req, VoicePorts.dev())
    outcome = session.run()
    # Adam się przywitał (ujawnienie AI) i rozmowa się domknęła
    assert len(channel.played) >= 1
    assert channel.hung_up is True
    assert outcome.senior_external_id == "SR-1"
    assert outcome.disclosure_said is True


# ------------------------------------------------------------------ StasisApp

def _app(channels: dict):
    def factory(cid: str):
        ch = FakeChannel(script=["Dzień dobry", "wszystko ok", "do widzenia"])
        channels[cid] = ch
        return ch
    return StasisApp(
        app_name="adam",
        channel_factory=factory,
        request_resolver=_resolver,
    )


def test_stasis_start_runs_and_records_outcome():
    channels: dict = {}
    app = _app(channels)
    out = app.handle_event({
        "type": "StasisStart", "application": "adam",
        "channel": {"id": "ch-100"},
    })
    assert out is not None
    assert "ch-100" in channels
    assert channels["ch-100"].hung_up is True
    assert len(app.outcomes) == 1


def test_stasis_end_and_other_events_ignored():
    app = _app({})
    assert app.handle_event({"type": "StasisEnd", "channel": {"id": "x"}}) is None
    assert app.handle_event({"type": "PlaybackFinished", "channel": {"id": "x"}}) is None
    assert app.outcomes == []


def test_stasis_filters_other_application():
    channels: dict = {}
    app = _app(channels)
    out = app.handle_event({
        "type": "StasisStart", "application": "inna-app",
        "channel": {"id": "ch-x"},
    })
    assert out is None
    assert channels == {}  # kanał nie utworzony


def test_stasis_start_without_channel_id_is_safe():
    app = _app({})
    out = app.handle_event({"type": "StasisStart", "application": "adam", "channel": {}})
    assert out is None


def test_stasis_resolver_error_is_fail_safe():
    def bad_resolver(event):
        raise RuntimeError("db down")
    app = StasisApp(
        app_name="adam",
        channel_factory=lambda cid: FakeChannel(script=[]),
        request_resolver=bad_resolver,
    )
    # nie rzuca — zwraca None
    out = app.handle_event({"type": "StasisStart", "application": "adam",
                            "channel": {"id": "ch-err"}})
    assert out is None


def test_stasis_run_processes_event_stream():
    channels: dict = {}
    app = _app(channels)
    events = [
        {"type": "StasisStart", "application": "adam", "channel": {"id": "ch-A"}},
        {"type": "PlaybackFinished", "application": "adam", "channel": {"id": "ch-A"}},
        {"type": "StasisStart", "application": "adam", "channel": {"id": "ch-B"}},
        {"type": "StasisEnd", "application": "adam", "channel": {"id": "ch-B"}},
    ]
    results = app.run(events)
    assert len(results) == 2          # dwa StasisStart → dwie rozmowy
    assert {"ch-A", "ch-B"} <= set(channels.keys())


# ------------------------------------------------------------------ originate_call

def test_originate_call_happy_path():
    req = CallStartRequest(senior_external_id="SR-9")
    res = originate_call(req, originator=lambda r: f"chan-{r.senior_external_id}")
    assert res.accepted is True
    assert res.channel_id == "chan-SR-9"


def test_originate_call_noop_without_originator():
    res = originate_call(CallStartRequest(senior_external_id="SR-9"))
    assert res.accepted is False
    assert "originate" in res.detail


def test_originate_call_fail_safe_on_error():
    def bad(r):
        raise RuntimeError("asterisk down")
    res = originate_call(CallStartRequest(senior_external_id="SR-9"), originator=bad)
    assert res.accepted is False
    assert "błąd" in res.detail.lower() or "asterisk" in res.detail.lower()
