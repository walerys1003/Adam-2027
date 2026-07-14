"""
F16 — QA (metryki jakości rozmów + pętla poprawy + nastrój + telemetria decyzji).

QAEvaluator ocenia rozmowę (0-100) po składowych: ujawnienie AI, responsywność
seniora, jakość ASR, brak przerwań, kompletność. QAService utrwala oceny,
ludzkie audyty, wnioski poprawy (improvement loop), realny nastrój
(SentimentReading — zastępuje heurystykę) oraz telemetrię decyzji konsensusu,
w tym spięcie ESCALATE→112 (ETAP 30, łączy ETAP 26+27).
"""
from .metrics import Turn, QAResult, QAEvaluator
from .models import (
    QAEvaluation, ManualAudit, ImprovementItem, SentimentReading, DecisionTelemetry,
    AuditVerdict, ImprovementStatus, MoodLabel, DecisionKind,
)
from .sentiment import analyze_sentiment, SentimentResult
from .service import QAService

__all__ = [
    "Turn", "QAResult", "QAEvaluator",
    "QAEvaluation", "ManualAudit", "ImprovementItem", "SentimentReading",
    "DecisionTelemetry", "AuditVerdict", "ImprovementStatus", "MoodLabel",
    "DecisionKind", "analyze_sentiment", "SentimentResult", "QAService",
]
