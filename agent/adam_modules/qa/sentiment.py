"""
F16 (ETAP 30) — realny analizator nastroju seniora (deterministyczny, PL).

Zastępuje heurystykę `moodFromSemaphore` (nastrój wyprowadzany wyłącznie z koloru
semafora) właściwym pomiarem sentymentu z treści wypowiedzi + sygnałów kontekstu
(poziom semafora, prozodia z wearables — opcjonalnie). Wynik: etykieta MoodLabel
+ ciągły score [-1, +1] + dowody (słowa/frazy) do audytu.

Leksykon jest jawny i audytowalny. To nie jest model ML — świadomie, bo w domenie
wysokiego ryzyka (AI Act) preferujemy wyjaśnialność i powtarzalność.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .models import MoodLabel


# leksykon nastroju (waga: siła sygnału)
_NEGATIVE = {
    "nie chcę żyć": -1.0, "chcę umrzeć": -1.0, "nie ma sensu": -0.8,
    "beznadziejnie": -0.7, "rozpacz": -0.8, "płaczę": -0.7, "płakać": -0.6,
    "samotny": -0.6, "samotna": -0.6, "samotność": -0.6, "opuszczony": -0.6,
    "smutno": -0.6, "smutny": -0.5, "smutna": -0.5, "przygnębiony": -0.6,
    "przygnębiona": -0.6, "boję się": -0.6, "strach": -0.5, "lęk": -0.5,
    "boli": -0.5, "cierpię": -0.6, "źle": -0.5, "gorzej": -0.5, "zmęczony": -0.4,
    "zmęczona": -0.4, "tęsknię": -0.5, "martwię się": -0.5, "zmartwiony": -0.5,
    "niepokój": -0.5, "nikt": -0.4, "nudno": -0.3, "słabo": -0.4,
    "nie daję rady": -0.7, "ciężko mi": -0.6,
}
_POSITIVE = {
    "dziękuję": 0.4, "cieszę się": 0.7, "szczęśliwy": 0.8, "szczęśliwa": 0.8,
    "wesoło": 0.6, "dobrze": 0.5, "świetnie": 0.8, "wspaniale": 0.8,
    "pogodnie": 0.6, "spokojnie": 0.5, "spokojny": 0.5, "zadowolony": 0.6,
    "zadowolona": 0.6, "uśmiech": 0.5, "wnuki": 0.4, "rodzina": 0.3,
    "lubię": 0.4, "kocham": 0.6, "miło": 0.5, "raźniej": 0.5, "lepiej": 0.5,
    "super": 0.7, "radość": 0.7,
}
_NEGATORS = ("nie", "ani", "bez")


@dataclass
class SentimentResult:
    label: MoodLabel
    score: float                      # -1..+1
    evidence: list[str] = field(default_factory=list)
    source: str = "text"

    def as_polish_mood(self) -> str:
        return {
            MoodLabel.crisis: "kryzys",
            MoodLabel.distressed: "przygnębiony",
            MoodLabel.neutral: "neutralny",
            MoodLabel.content: "spokojny",
            MoodLabel.happy: "pogodny",
        }[self.label]


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").lower()).strip()


def _score_from_label_floor(score: float, crisis: bool) -> MoodLabel:
    if crisis:
        return MoodLabel.crisis
    if score <= -0.6:
        return MoodLabel.distressed
    if score < -0.15:
        return MoodLabel.distressed
    if score <= 0.15:
        return MoodLabel.neutral
    if score < 0.6:
        return MoodLabel.content
    return MoodLabel.happy


def analyze_sentiment(
    text: str,
    *,
    semaphore_level: str | None = None,
    prosody_valence: float | None = None,
    source: str = "text",
) -> SentimentResult:
    """Analiza nastroju z treści + opcjonalnych sygnałów (semafor, prozodia).

    - crisis: gdy semafor purple/red LUB wykryto frazy suicydalne (twarda reguła).
    - score: sumaryczny sygnał leksykalny znormalizowany, korygowany prozodią.
    """
    norm = _norm(text)
    evidence: list[str] = []
    raw = 0.0
    hits = 0

    words = norm.split()
    for phrase, w in {**_NEGATIVE, **_POSITIVE}.items():
        if phrase in norm:
            # prosta obsługa negacji: „nie smutno" osłabia/odwraca sygnał 1-wyrazowy
            negated = False
            if " " not in phrase:
                idx = words.index(phrase) if phrase in words else -1
                if idx > 0 and words[idx - 1] in _NEGATORS:
                    negated = True
            val = -w * 0.6 if negated else w
            raw += val
            hits += 1
            evidence.append(phrase if not negated else f"nie+{phrase}")

    # normalizacja do [-1, 1] (miękkie nasycenie)
    score = max(-1.0, min(1.0, raw / 2.0)) if hits else 0.0

    # korekta prozodią z wearable/ASR (np. drżenie głosu → obniż)
    if prosody_valence is not None:
        score = max(-1.0, min(1.0, 0.7 * score + 0.3 * prosody_valence))
        source = "prosody" if source == "text" else source

    crisis = False
    if semaphore_level in ("red", "purple"):
        crisis = True
        evidence.append(f"semafor:{semaphore_level}")
    if any(p in norm for p in ("nie chcę żyć", "chcę umrzeć", "odebrać sobie życie")):
        crisis = True

    label = _score_from_label_floor(score, crisis)
    if crisis:
        score = min(score, -0.9)
    return SentimentResult(label=label, score=round(score, 3), evidence=evidence, source=source)
