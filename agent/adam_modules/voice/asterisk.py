"""Produkcyjny adapter kanału Asterisk ARI (ETAP 17.3).

`AsteriskAriChannel` implementuje port `AriChannel` przez Asterisk REST Interface
(ARI). W dev/test używamy `FakeChannel`; ten adapter jest ścieżką produkcyjną
(Frankfurt DC), gdzie Asterisk odbiera połączenie od seniora i przekazuje kanał
do aplikacji Stasis.

Zasady:
- **Sieć tylko na brzegach** — klient HTTP (`httpx`) jest wstrzykiwany, dzięki
  czemu logika sesji (`CallSession`) pozostaje w 100% testowalna offline.
- **Fail-safe** — błąd HTTP nie wywala rozmowy: `play`/`record` łapią wyjątki,
  logują i zwracają wartość bezpieczną (None dla nagrania → sesja domyka rozmowę).
  Rozłączenie (`hangup`) jest best-effort.
- Bez sekretów/URL adapter działa w trybie „no-op" (log ostrzeżenia) — nigdy
  nie rzuca przy konstrukcji.

Uwaga: pełne ARI używa WebSocket (Stasis) do zdarzeń + REST do akcji. Tu
modelujemy warstwę akcji (play/record/hangup) wystarczającą dla `CallSession`;
warstwę zdarzeń podłącza się w procesie osadzającym (poza zakresem tej klasy).
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger("adam.voice.ari")


class AsteriskAriChannel:
    """Adapter kanału ARI. Implementuje protokół `AriChannel` (play/record/hangup)."""

    def __init__(
        self,
        channel_id: str,
        *,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        http_client=None,
        record_timeout_s: int = 15,
    ):
        self.channel_id = channel_id
        self.base_url = (base_url or os.getenv("ASTERISK_ARI_URL", "")).rstrip("/")
        self.username = username or os.getenv("ASTERISK_ARI_USER", "")
        self.password = password or os.getenv("ASTERISK_ARI_PASS", "")
        self.record_timeout_s = record_timeout_s
        self._client = http_client  # wstrzykiwany httpx.Client (lub zgodny)
        self._rec_seq = 0
        if not self.base_url:
            logger.warning("AsteriskAriChannel bez ASTERISK_ARI_URL — tryb no-op")

    # -------------------------------------------------- pomocnicze
    def _ready(self) -> bool:
        return bool(self.base_url and self._client is not None)

    def _auth(self):
        return (self.username, self.password) if self.username else None

    # -------------------------------------------------- protokół AriChannel
    def play(self, audio_ref: str) -> None:
        """Odtwarza medium na kanale (POST /channels/{id}/play)."""
        if not self._ready():
            logger.info("[no-op] play channel=%s ref=%s", self.channel_id, audio_ref)
            return
        try:
            self._client.post(
                f"{self.base_url}/channels/{self.channel_id}/play",
                params={"media": self._to_media_uri(audio_ref)},
                auth=self._auth(),
            )
        except Exception as exc:  # fail-safe: nie przerywaj rozmowy
            logger.warning("ARI play error channel=%s err=%s", self.channel_id, exc)

    def record_utterance(self) -> str | None:
        """Nagrywa wypowiedź seniora i zwraca referencję audio (lub None).

        Zwracamy `record:<name>` — ASR (produkcyjny Whisper) pobiera plik po tej
        nazwie. Błąd nagrania → None → `CallSession` bezpiecznie domyka rozmowę.
        """
        if not self._ready():
            logger.info("[no-op] record channel=%s", self.channel_id)
            return None
        self._rec_seq += 1
        name = f"adam-{self.channel_id}-{self._rec_seq}"
        try:
            self._client.post(
                f"{self.base_url}/channels/{self.channel_id}/record",
                params={
                    "name": name, "format": "wav",
                    "maxDurationSeconds": self.record_timeout_s,
                    "beep": "true", "terminateOn": "#",
                },
                auth=self._auth(),
            )
            return f"record:{name}"
        except Exception as exc:
            logger.warning("ARI record error channel=%s err=%s", self.channel_id, exc)
            return None

    def hangup(self) -> None:
        """Rozłącza kanał (DELETE /channels/{id}). Best-effort."""
        if not self._ready():
            logger.info("[no-op] hangup channel=%s", self.channel_id)
            return
        try:
            self._client.delete(
                f"{self.base_url}/channels/{self.channel_id}",
                auth=self._auth(),
            )
        except Exception as exc:
            logger.warning("ARI hangup error channel=%s err=%s", self.channel_id, exc)

    # -------------------------------------------------- mapowanie audio
    @staticmethod
    def _to_media_uri(audio_ref: str) -> str:
        """Mapuje wewnętrzną referencję TTS na URI medium ARI.

        - 'tts:...' / 'say:...'  → 'sound:<...>' (plik wygenerowany przez TTS),
        - inne                    → przekazujemy bez zmian (np. 'sound:hello').
        """
        for prefix in ("tts:", "say:"):
            if audio_ref.startswith(prefix):
                return "sound:" + audio_ref[len(prefix):].strip().replace(" ", "_")[:64]
        return audio_ref
