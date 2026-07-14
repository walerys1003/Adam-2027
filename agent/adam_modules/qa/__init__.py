"""
F15 — QA (metryki jakości rozmów).

QAEvaluator ocenia rozmowę (0-100) po składowych: ujawnienie AI, responsywność
seniora, jakość ASR, brak przerwań, kompletność. Wskazuje rozmowy do przeglądu
przez człowieka.
"""
from .metrics import Turn, QAResult, QAEvaluator

__all__ = ["Turn", "QAResult", "QAEvaluator"]
