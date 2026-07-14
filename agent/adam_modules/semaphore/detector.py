"""
CrisisDetector (F8) — detekcja sygnałów z wypowiedzi seniora + pomiarów.

Zamienia surowy tekst rozmowy (transkrypcja) i/lub sygnały wearables na listę
wyzwalaczy (Trigger) wraz z pewnością i dowodami. Wynik zasila SemaphoreEngine
(F3) i przechodzi przez Guardrails (F4).

Detekcja jest regułowa (słowniki fraz PL) — deterministyczna, audytowalna
(wymóg AI Act). W produkcji można dołożyć warstwę modelu LLM, ale twarde
sygnały kryzysowe (fioletowe) MUSZĄ pozostać wykrywane regułowo dla
niezawodności (fail-safe).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from adam_modules.seniors.models import SemaphoreLevel
from .models import Trigger
from .engine import TRIGGER_LEVEL, level_rank, Classification

# Frazy PL → Trigger. Dobrane pod mowę senioralną (potoczne, opisowe).
# Uwaga: kolejność bez znaczenia — dopasowujemy wszystkie.
_PHRASE_TRIGGERS: dict[Trigger, list[str]] = {
    # PURPLE — twarde sygnały kryzysowe
    Trigger.chest_pain: [
        "ból w klatce", "boli mnie w klatce", "ściska mnie w piersi",
        "ucisk w klatce", "ból serca", "piecze mnie w klatce",
    ],
    Trigger.breathing_difficulty: [
        "nie mogę oddychać", "duszę się", "brakuje mi tchu", "brak powietrza",
        "łapię powietrze", "ciężko mi oddychać", "duszność",
    ],
    Trigger.stroke_symptoms: [
        "nie czuję ręki", "opadła mi twarz", "nie mogę mówić", "bełkoczę",
        "zdrętwiała mi połowa", "krzywe usta", "nie widzę na jedno oko",
    ],
    Trigger.suicide_ideation: [
        "nie chcę żyć", "chcę umrzeć", "odebrać sobie życie", "nie ma po co żyć",
        "zrobię sobie krzywdę", "lepiej mnie nie będzie", "skończyć ze sobą",
    ],
    Trigger.unconscious: [
        "zemdlał", "stracił przytomność", "nie reaguje", "zasłabł",
        "nie mogę go dobudzić", "leży i nie odpowiada",
    ],
    Trigger.severe_bleeding: [
        "silne krwawienie", "dużo krwi", "leje się krew", "krwotok",
        "nie mogę zatamować krwi",
    ],
    # RED — pilne
    Trigger.persistent_pain: [
        "cały czas boli", "ból nie ustępuje", "bardzo mnie boli", "silny ból",
        "boli od rana", "nie do wytrzymania",
    ],
    Trigger.confusion: [
        "nie wiem gdzie jestem", "nie pamiętam", "jestem zdezorientowany",
        "pomieszało mi się", "nie poznaję",
    ],
    Trigger.fall_reported: [
        "przewróciłem się", "upadłem", "spadłem", "leżę na podłodze",
        "nie mogę wstać", "przewrócił się",
    ],
    # YELLOW — obserwacja
    Trigger.mood_low: [
        "jestem smutny", "przygnębiony", "nic mi się nie chce", "źle się czuję psychicznie",
        "jestem samotny", "płacze mi się",
    ],
    Trigger.missed_medication: [
        "nie wziąłem leków", "zapomniałem tabletki", "nie brałem leków",
        "pominąłem lek", "skończyły mi się leki",
    ],
    Trigger.poor_sleep: [
        "nie spałem", "nie mogę spać", "źle śpię", "budzę się w nocy",
        "bezsenność",
    ],
    Trigger.social_isolation: [
        "nikt do mnie nie dzwoni", "nie mam z kim pogadać", "jestem sam",
        "nikt mnie nie odwiedza",
    ],
    Trigger.minor_complaint: [
        "boli mnie głowa", "trochę mnie boli", "nie najlepiej się czuję",
        "mam katar", "lekko gorzej",
    ],
}


@dataclass
class Detection:
    trigger: Trigger
    level: SemaphoreLevel
    confidence: float
    evidence: list[str] = field(default_factory=list)


# Progi pewności wg poziomu (regułowe dopasowanie frazy = wysoka pewność).
_LEVEL_CONFIDENCE = {
    SemaphoreLevel.purple: 0.9,
    SemaphoreLevel.red: 0.8,
    SemaphoreLevel.yellow: 0.7,
    SemaphoreLevel.green: 1.0,
}

# Twarde sygnały kryzysowe — muszą pokrywać się z Guardrails._HARD_CRISIS_SIGNALS
HARD_CRISIS_TRIGGERS = {
    Trigger.chest_pain,
    Trigger.breathing_difficulty,
    Trigger.stroke_symptoms,
    Trigger.suicide_ideation,
    Trigger.unconscious,
    Trigger.severe_bleeding,
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


class CrisisDetector:
    """Regułowy detektor sygnałów kryzysowych i obserwacyjnych."""

    def __init__(
        self,
        phrase_map: dict[Trigger, list[str]] | None = None,
        *,
        regional: bool = False,
    ):
        self.phrase_map = phrase_map or _PHRASE_TRIGGERS
        # F13 (ETAP 29): opcjonalna normalizacja gwary wielkopolskiej przed detekcją,
        # tak by regionalizmy kryzysowe (np. „nie mogę dychać") trafiały w reguły.
        self.regional = regional

    def detect_text(self, text: str) -> list[Detection]:
        """Wykrywa wszystkie triggery obecne w tekście wypowiedzi."""
        if self.regional and text:
            from adam_modules.speech.wielkopolska import normalize_regional
            text = normalize_regional(text).normalized
        norm = _normalize(text)
        found: list[Detection] = []
        for trigger, phrases in self.phrase_map.items():
            hits = [p for p in phrases if p in norm]
            if hits:
                level = TRIGGER_LEVEL[trigger]
                found.append(Detection(
                    trigger=trigger,
                    level=level,
                    confidence=_LEVEL_CONFIDENCE[level],
                    evidence=hits,
                ))
        return found

    def detect_vitals(self, vitals: dict[str, float]) -> list[Detection]:
        """Wykrywa nieprawidłowe parametry życiowe (wearables/pomiary, F10)."""
        out: list[Detection] = []
        ev: list[str] = []
        hr = vitals.get("heart_rate")
        spo2 = vitals.get("spo2")
        sys_bp = vitals.get("systolic")
        if hr is not None and (hr < 40 or hr > 130):
            ev.append(f"heart_rate={hr}")
        if spo2 is not None and spo2 < 90:
            ev.append(f"spo2={spo2}")
        if sys_bp is not None and (sys_bp < 90 or sys_bp > 180):
            ev.append(f"systolic={sys_bp}")
        if ev:
            out.append(Detection(
                trigger=Trigger.vitals_out_of_range,
                level=SemaphoreLevel.red,
                confidence=0.85,
                evidence=ev,
            ))
        return out

    def detect(self, text: str = "", vitals: dict[str, float] | None = None) -> list[Detection]:
        """Łączna detekcja z tekstu i pomiarów."""
        result = self.detect_text(text)
        if vitals:
            result.extend(self.detect_vitals(vitals))
        return result

    def top_trigger(self, detections: list[Detection]) -> Detection | None:
        """Zwraca detekcję o najwyższym poziomie (do zasilenia SemaphoreEngine)."""
        if not detections:
            return None
        return max(detections, key=lambda d: (level_rank(d.level), d.confidence))

    def to_classification(self, detections: list[Detection]) -> Classification:
        """Buduje Classification z najsilniejszej detekcji (lub zielony, gdy brak).

        `signals` zawiera wartości triggerów wszystkich detekcji — dzięki temu
        Guardrails (F4) widzi twardy sygnał kryzysowy przy PURPLE.
        """
        top = self.top_trigger(detections)
        if top is None:
            return Classification(level=SemaphoreLevel.green, trigger=Trigger.routine_ok)
        signals = {d.trigger.value: d.evidence for d in detections}
        return Classification(
            level=top.level,
            trigger=top.trigger,
            confidence=top.confidence,
            signals=signals,
        )
