"""dialplan 112 (F15, ETAP 26) — generator dialplanu Asterisk + originator (fail-safe).

Dwie odpowiedzialności:
1. `render_emergency_dialplan()` — generuje fragment dialplanu Asterisk (extensions.conf)
   dla kontekstu `adam-emergency`: originate → Playback komunikatu → most z dyspozytorem.
2. `EmergencyOriginator` (Protocol) + `NullEmergencyOriginator` — port do realnego
   wywołania 112 przez ARI. W dev/sandbox originator=None → zwracamy `simulated`
   (fail-safe: nigdy nie wywala się brakiem telefonii).

Numer 112 jest KONFIGUROWALNY (env EMERGENCY_NUMBER) — w testach/dev używamy numeru
testowego, by nie było ryzyka realnego wybrania 112.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from .audio import EmergencyAudioScript

# W produkcji '112'; w dev/testach numer testowy (ochrona przed realnym wybraniem).
EMERGENCY_NUMBER = os.getenv("ADAM_EMERGENCY_NUMBER", "112")
EMERGENCY_TRUNK = os.getenv("ADAM_EMERGENCY_TRUNK", "")  # np. 'PJSIP/trunk-112'


@dataclass
class OriginateResult:
    ok: bool
    channel_id: str | None = None
    detail: str = ""
    simulated: bool = False


class EmergencyOriginator(Protocol):
    def originate(self, *, number: str, audio_ref: str) -> OriginateResult: ...  # pragma: no cover


class NullEmergencyOriginator:
    """Dev/sandbox: nie dzwoni nigdzie — zwraca wynik symulowany (fail-safe)."""
    def originate(self, *, number: str, audio_ref: str) -> OriginateResult:
        return OriginateResult(
            ok=False, simulated=True,
            detail=f"symulacja (dev) — brak realnej telefonii; docelowo numer {number}",
        )


def render_emergency_dialplan(*, audio_file: str = "adam-emergency-msg",
                              number: str | None = None,
                              trunk: str | None = None) -> str:
    """Zwraca fragment extensions.conf dla wezwania 112 (kontekst adam-emergency)."""
    num = number or EMERGENCY_NUMBER
    trk = trunk or EMERGENCY_TRUNK or "PJSIP/emergency-trunk"
    return "\n".join([
        "; --- Adam F15: dialplan wezwania ratunkowego (ETAP 26) ---",
        "[adam-emergency]",
        f"exten => call112,1,NoOp(Adam emergency dispatch → {num})",
        f" same => n,Set(CALLERID(name)=Adam-Opieka)",
        f" same => n,Dial({trk}/{num},60,g)",
        f" same => n,Playback({audio_file})",   # komunikat głosowy do dyspozytora
        " same => n,Playback(silence/1)",
        f" same => n,Playback({audio_file})",   # powtórzenie
        " same => n,Wait(2)",
        " same => n,Hangup()",
        "",
    ])


def originate_emergency(script: EmergencyAudioScript,
                        originator: EmergencyOriginator | None = None,
                        *, number: str | None = None) -> OriginateResult:
    """Uruchamia wezwanie. Bez originatora (dev) → wynik symulowany, bez wyjątku."""
    num = number or EMERGENCY_NUMBER
    if originator is None:
        return NullEmergencyOriginator().originate(
            number=num, audio_ref="emergency:" + script.full_text()[:48]
        )
    return originator.originate(number=num, audio_ref="emergency:" + script.full_text()[:48])
