"""
F16 — Multi-model consensus.

Dla klasyfikacji krytycznych łączy głosy >=2 niezależnych źródeł. Fail-safe:
przy rozbieżności wybiera wyższy poziom i oznacza needs_review.
"""
from .engine import (
    ModelVote, ConsensusResult, ConsensusEngine, MIN_SOURCES_FOR_CRITICAL,
)

__all__ = [
    "ModelVote", "ConsensusResult", "ConsensusEngine", "MIN_SOURCES_FOR_CRITICAL",
]
