"""
F15 — QA: metryki jakości rozmów.

Ocena pojedynczej rozmowy Adama na podstawie transkryptu z ról (adam/senior)
oraz metadanych (czas trwania, przerwania, ASR confidence). Zwraca wynik 0-100
i listę flag jakości — do monitoringu, dashboardu koordynatora i doboru
rozmów do ludzkiego przeglądu.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Turn:
    role: str          # "adam" | "senior"
    text: str
    asr_confidence: float = 1.0  # pewność rozpoznania mowy (0-1)


@dataclass
class QAResult:
    score: float                       # 0-100
    flags: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


# Wagi składowych (suma = 1.0)
_WEIGHTS = {
    "disclosure": 0.25,      # czy Adam ujawnił naturę AI
    "responsiveness": 0.20,  # czy senior odpowiadał (nie same pytania Adama)
    "asr_quality": 0.20,     # średnia pewność ASR
    "no_interruptions": 0.15,
    "completeness": 0.20,    # czy rozmowa dobiegła sensownego końca
}

_DISCLOSURE_MARKERS = ("jestem cyfrowym asystentem", "nie jestem człowiekiem",
                       "asystent", "cyfrowy", "adam")


class QAEvaluator:
    def evaluate(self, turns: list[Turn], *, duration_s: float | None = None,
                 interruptions: int = 0, completed: bool = True) -> QAResult:
        flags: list[str] = []
        metrics: dict = {}

        adam_turns = [t for t in turns if t.role == "adam"]
        senior_turns = [t for t in turns if t.role == "senior"]
        total = len(turns)

        # 1. disclosure
        disclosed = any(
            any(m in t.text.lower() for m in _DISCLOSURE_MARKERS) for t in adam_turns
        )
        if not disclosed:
            flags.append("brak_ujawnienia_AI")
        s_disclosure = 1.0 if disclosed else 0.0

        # 2. responsiveness — udział wypowiedzi seniora
        resp = (len(senior_turns) / total) if total else 0.0
        s_resp = min(1.0, resp / 0.4)  # 40%+ wypowiedzi seniora = pełny wynik
        if resp < 0.15:
            flags.append("senior_malo_mowil")

        # 3. asr quality
        confs = [t.asr_confidence for t in senior_turns] or [1.0]
        avg_conf = sum(confs) / len(confs)
        s_asr = avg_conf
        if avg_conf < 0.6:
            flags.append("niska_jakosc_ASR")

        # 4. interruptions
        s_interr = 1.0 if interruptions == 0 else max(0.0, 1.0 - 0.2 * interruptions)
        if interruptions > 2:
            flags.append("liczne_przerwania")

        # 5. completeness
        s_complete = 1.0 if completed else 0.3
        if not completed:
            flags.append("rozmowa_niezakonczona")

        score = 100.0 * (
            _WEIGHTS["disclosure"] * s_disclosure
            + _WEIGHTS["responsiveness"] * s_resp
            + _WEIGHTS["asr_quality"] * s_asr
            + _WEIGHTS["no_interruptions"] * s_interr
            + _WEIGHTS["completeness"] * s_complete
        )

        metrics = {
            "turns": total,
            "senior_ratio": round(resp, 3),
            "avg_asr_confidence": round(avg_conf, 3),
            "interruptions": interruptions,
            "disclosed": disclosed,
            "completed": completed,
            "duration_s": duration_s,
        }
        return QAResult(score=round(score, 1), flags=flags, metrics=metrics)

    def needs_human_review(self, result: QAResult, threshold: float = 60.0) -> bool:
        """Rozmowy poniżej progu lub z krytycznymi flagami idą do przeglądu."""
        critical = {"brak_ujawnienia_AI", "rozmowa_niezakonczona"}
        return result.score < threshold or bool(critical & set(result.flags))
