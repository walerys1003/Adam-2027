"""emergency_audio (F15, ETAP 26) — komunikat głosowy dla dyspozytora 112.

Buduje ustrukturyzowany, WOLNO czytany skrypt głosowy przekazywany operatorowi 112
przy eskalacji PURPLE. Skrypt jest deterministyczny, powtarzalny (dyspozytor może
poprosić o powtórzenie) i zoptymalizowany pod syntezę mowy (krótkie zdania, brak
skrótów, cyfry rozpisane słownie tam, gdzie to krytyczne — adres/telefon).

Warstwa czysto logiczna (bez TTS/telefonii) — zwraca tekst + segmenty. Realna synteza
i odtworzenie na kanale ARI to warstwa I/O (patrz dialplan.py + prod TTS).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .payload import EmergencyPayload


@dataclass
class EmergencyAudioScript:
    """Skrypt głosowy 112: pełny tekst + segmenty (do TTS/odtwarzania po kolei)."""
    intro: str
    location: str
    patient: str
    condition: str
    vitals: str
    repeat_notice: str
    segments: list[str] = field(default_factory=list)

    def full_text(self) -> str:
        return " ".join(s for s in self.segments if s)


def _spell_phone(phone: str | None) -> str:
    """Rozpisuje numer telefonu cyfra-po-cyfrze (czytelność dla dyspozytora)."""
    if not phone:
        return "numer nieznany"
    digits = [c for c in phone if c.isdigit()]
    names = {
        "0": "zero", "1": "jeden", "2": "dwa", "3": "trzy", "4": "cztery",
        "5": "pięć", "6": "sześć", "7": "siedem", "8": "osiem", "9": "dziewięć",
    }
    return " ".join(names[d] for d in digits) if digits else "numer nieznany"


def build_emergency_audio(payload: EmergencyPayload) -> EmergencyAudioScript:
    """Tworzy skrypt głosowy 112 z payloadu eskalacji."""
    intro = (
        "Tu automatyczny system opieki senioralnej Adam. "
        "Zgłaszam sytuację zagrożenia życia. Proszę o pilną pomoc."
    )
    who = f"{payload.full_name}, wiek {payload.age} lat." if payload.age else f"{payload.full_name}."
    patient = f"Osoba wymagająca pomocy: {who}"

    where = payload.address or "adres nieznany"
    district = f" Dzielnica {payload.district}." if payload.district else ""
    location = f"Adres zdarzenia: {where}.{district} Telefon kontaktowy: {_spell_phone(payload.phone)}."

    condition = f"Powód wezwania: {payload.reason}."
    if payload.medications:
        condition += f" Osoba przyjmuje leki: {', '.join(payload.medications)}."

    if payload.recent_vitals:
        readings = ", ".join(f"{k} {v}" for k, v in payload.recent_vitals.items())
        vitals = f"Ostatnie pomiary życiowe: {readings}."
    else:
        vitals = "Brak dostępnych pomiarów życiowych."

    repeat_notice = "Powtarzam najważniejsze informacje."

    segments = [intro, patient, location, condition, vitals]
    # sekcja powtórzenia (adres + powód) — kluczowe dla dyspozytora
    segments += [repeat_notice, location, condition]

    return EmergencyAudioScript(
        intro=intro, location=location, patient=patient,
        condition=condition, vitals=vitals, repeat_notice=repeat_notice,
        segments=segments,
    )
