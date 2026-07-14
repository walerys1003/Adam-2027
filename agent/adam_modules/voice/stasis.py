"""Warstwa zdarzeń ARI (Stasis) — osadzenie CallSession w pętli Asteriska (ETAP 19).

Pełne ARI to dwa kanały:
- **REST** (akcje: play/record/hangup) — pokrywa `AsteriskAriChannel` (ETAP 17),
- **WebSocket (Stasis)** — strumień zdarzeń (`StasisStart`, `StasisEnd`, ...).

Ten moduł dokłada brakującą warstwę zdarzeń:
- `StasisApp` — pętla konsumująca zdarzenia i uruchamiająca `CallSession` na
  `StasisStart` (nowe połączenie od seniora wchodzi do aplikacji Stasis),
- `CallStartRequest` — kontrakt webhooka startu połączenia (dla originate z
  Schedulera F2: „zadzwoń do seniora X"),
- `build_call_session` — fabryka spinająca kanał ARI + DialogEngine + porty
  (dev Echo/Rule/Text lub produkcyjne Whisper/OpenAI/ElevenLabs z ETAP 18).

Zasady (spójne z resztą warstwy głosu):
- **Sieć/websocket tylko na brzegach** — połączenie WS jest wstrzykiwane
  (`event_source`), dzięki czemu pętla jest w 100% testowalna offline listą
  zdarzeń-słowników.
- **Fail-safe** — błąd obsługi jednego zdarzenia nie zatrzymuje pętli; błąd
  jednej rozmowy nie przewraca aplikacji.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Iterable

from .ari import AriChannel, CallSession
from .dialog import DialogEngine, CallOutcome
from .ports import ASRPort, TTSPort, LLMPort, RuleLLM, EchoASR, TextTTS

logger = logging.getLogger("adam.voice.stasis")


# ------------------------------------------------------------------ kontrakty

@dataclass
class CallStartRequest:
    """Żądanie rozpoczęcia połączenia (webhook / originate ze Schedulera F2)."""
    senior_external_id: str
    senior_name: str | None = None
    senior_age: int | None = None
    phone: str | None = None
    reason: str = "welfare_check"


@dataclass
class VoicePorts:
    """Zestaw portów I/O dla rozmowy (dev lub produkcyjne z ETAP 18)."""
    llm: LLMPort
    asr: ASRPort
    tts: TTSPort

    @classmethod
    def dev(cls) -> "VoicePorts":
        """Deweloperskie porty bez sieci (Echo/Rule/Text)."""
        return cls(llm=RuleLLM(), asr=EchoASR(), tts=TextTTS())


# ------------------------------------------------------------------ fabryka sesji

def build_call_session(
    channel: AriChannel,
    req: CallStartRequest,
    ports: VoicePorts | None = None,
    *,
    use_consensus: bool = True,
    max_turns: int = 20,
) -> CallSession:
    """Buduje CallSession: DialogEngine (z profilem seniora) + kanał + porty."""
    p = ports or VoicePorts.dev()
    engine = DialogEngine(
        p.llm,
        senior_name=req.senior_name,
        senior_age=req.senior_age,
        senior_external_id=req.senior_external_id,
        use_consensus=use_consensus,
    )
    return CallSession(channel, engine, asr=p.asr, tts=p.tts, max_turns=max_turns)


# ------------------------------------------------------------------ aplikacja Stasis

class StasisApp:
    """Aplikacja Stasis: konsumuje zdarzenia ARI i prowadzi rozmowy.

    Parametry wstrzykiwane (testowalność offline):
    - `channel_factory(channel_id) -> AriChannel` — tworzy kanał REST (prod:
      `AsteriskAriChannel`; test: FakeChannel/atrapa),
    - `request_resolver(event) -> CallStartRequest` — mapuje zdarzenie
      `StasisStart` na profil seniora (prod: lookup po numerze/kanale w DB),
    - `ports` — zestaw portów I/O (dev lub produkcyjne).

    `app_name` filtruje zdarzenia do naszej aplikacji Stasis (Asterisk może
    multipleksować wiele aplikacji na jednym WS).
    """

    def __init__(
        self,
        *,
        app_name: str = "adam",
        channel_factory: Callable[[str], AriChannel],
        request_resolver: Callable[[dict], CallStartRequest],
        ports: VoicePorts | None = None,
        use_consensus: bool = True,
        max_turns: int = 20,
    ):
        self.app_name = app_name
        self._channel_factory = channel_factory
        self._resolve = request_resolver
        self._ports = ports or VoicePorts.dev()
        self._use_consensus = use_consensus
        self._max_turns = max_turns
        self.outcomes: list[CallOutcome] = []

    # -------------------------------------------------- pojedyncze zdarzenie
    def handle_event(self, event: dict) -> CallOutcome | None:
        """Obsługuje jedno zdarzenie ARI. Zwraca CallOutcome dla StasisStart."""
        etype = event.get("type")
        # filtr aplikacji (jeśli Asterisk podaje 'application')
        app = event.get("application")
        if app is not None and app != self.app_name:
            return None

        if etype == "StasisStart":
            return self._on_start(event)
        if etype == "StasisEnd":
            logger.info("StasisEnd channel=%s", _channel_id(event))
            return None
        # inne zdarzenia (ChannelDtmfReceived, PlaybackFinished...) — log i pomiń
        logger.debug("Zdarzenie ARI pominięte: %s", etype)
        return None

    def _on_start(self, event: dict) -> CallOutcome | None:
        channel_id = _channel_id(event)
        if not channel_id:
            logger.warning("StasisStart bez channel.id — pomijam")
            return None
        try:
            req = self._resolve(event)
            channel = self._channel_factory(channel_id)
            session = build_call_session(
                channel, req, self._ports,
                use_consensus=self._use_consensus, max_turns=self._max_turns,
            )
            outcome = session.run()
            self.outcomes.append(outcome)
            logger.info(
                "Rozmowa zakończona channel=%s senior=%s escalated=%s needs_review=%s",
                channel_id, req.senior_external_id,
                getattr(outcome, "escalated", None), getattr(outcome, "needs_review", None),
            )
            return outcome
        except Exception as exc:  # fail-safe: jedna rozmowa nie wywala aplikacji
            logger.exception("Błąd obsługi StasisStart channel=%s err=%s", channel_id, exc)
            return None

    # -------------------------------------------------- pętla zdarzeń
    def run(self, event_source: Iterable[dict]) -> list[CallOutcome]:
        """Konsumuje strumień zdarzeń (WS lub lista). Fail-safe per zdarzenie."""
        results: list[CallOutcome] = []
        for event in event_source:
            try:
                out = self.handle_event(event)
                if out is not None:
                    results.append(out)
            except Exception as exc:  # nie zatrzymuj pętli
                logger.warning("Błąd pętli Stasis err=%s", exc)
        return results


# ------------------------------------------------------------------ webhook startu

@dataclass
class CallStartResult:
    """Wynik żądania startu połączenia (odpowiedź webhooka)."""
    accepted: bool
    channel_id: str | None = None
    detail: str = ""


def originate_call(
    req: CallStartRequest,
    *,
    originator: Callable[[CallStartRequest], str] | None = None,
) -> CallStartResult:
    """Inicjuje połączenie wychodzące do seniora (originate).

    `originator(req) -> channel_id` jest wstrzykiwany (prod: POST /channels do
    Asteriska; test: atrapa). Bez originatora → no-op (odrzucone, ale bez wyjątku)
    — spójne z zasadą fail-safe.
    """
    if originator is None:
        logger.warning("originate_call bez originatora — no-op (odrzucone)")
        return CallStartResult(accepted=False, detail="brak konfiguracji originate")
    try:
        channel_id = originator(req)
        return CallStartResult(accepted=True, channel_id=channel_id, detail="ok")
    except Exception as exc:  # fail-safe
        logger.warning("originate_call error senior=%s err=%s", req.senior_external_id, exc)
        return CallStartResult(accepted=False, detail=f"błąd originate: {exc}")


# ------------------------------------------------------------------ helpery

def _channel_id(event: dict) -> str | None:
    ch = event.get("channel") or {}
    return ch.get("id")
