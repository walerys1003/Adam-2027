"""Summarizer rozmów (F7, ETAP 28) — deterministyczne streszczenie z transkryptu.

Czysta logika (bez LLM): wyciąga nastrój, tematy i zwięzłe podsumowanie z listy tur
rozmowy. W produkcji można podmienić na streszczenie LLM (ta sama sygnatura wyniku),
ale wersja regułowa jest darmowa, powtarzalna i testowalna.
"""
from __future__ import annotations

from dataclasses import dataclass, field


# Słowa-klucze tematów (senioralny kontekst)
_TOPIC_KEYWORDS = {
    "leki": ("lek", "tabletk", "lekarstw", "dawk"),
    "samopoczucie": ("czuj", "samopoczuci", "zdrowi", "ból", "boli"),
    "samotność": ("samotn", "sam ", "nikt", "tęskni"),
    "rodzina": ("córk", "syn", "wnuk", "rodzin", "mąż", "żona"),
    "sen": ("spał", "sen ", "bezsenn", "nie spał"),
    "posiłki": ("jad", "jedzeni", "obiad", "śniadani", "posiłek"),
    "wizyta": ("lekarz", "wizyt", "przychodni", "szpital"),
}

_MOOD_POSITIVE = ("dobrze", "świetnie", "w porządku", "cieszę", "spokojn", "wesoł")
_MOOD_NEGATIVE = ("smutno", "źle", "gorzej", "martwię", "boję", "samotn", "płacz")


@dataclass
class ConversationDigest:
    summary: str
    mood: str
    topics: list[str] = field(default_factory=list)
    turn_count: int = 0


def _detect_mood(text: str, max_level: str | None) -> str:
    t = text.lower()
    if max_level in ("red", "purple"):
        return "kryzys"
    neg = sum(1 for w in _MOOD_NEGATIVE if w in t)
    pos = sum(1 for w in _MOOD_POSITIVE if w in t)
    if neg > pos:
        return "przygnębiony"
    if pos > neg:
        return "pogodny"
    return "neutralny"


def _detect_topics(text: str) -> list[str]:
    t = text.lower()
    found = [topic for topic, kws in _TOPIC_KEYWORDS.items() if any(k in t for k in kws)]
    return found


def summarize_transcript(transcript: str, *, max_level: str | None = None,
                         turn_count: int = 0) -> ConversationDigest:
    """Buduje deterministyczne streszczenie rozmowy z transkryptu tekstowego."""
    text = transcript or ""
    mood = _detect_mood(text, max_level)
    topics = _detect_topics(text)

    topic_str = ", ".join(topics) if topics else "rozmowa ogólna"
    level_str = ""
    if max_level and max_level != "green":
        level_str = f" Poziom semafora: {max_level}."
    summary = (
        f"Rozmowa ({turn_count} tur). Tematy: {topic_str}. "
        f"Nastrój rozmówcy: {mood}.{level_str}"
    )
    return ConversationDigest(summary=summary, mood=mood, topics=topics, turn_count=turn_count)
