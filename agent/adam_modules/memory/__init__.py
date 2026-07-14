"""
F7 — Pamięć semantyczna (RAG rozmów).

Zapis fragmentów rozmów/faktów o seniorze jako embeddingi i retrieval
najbardziej podobnych fragmentów, wstrzykiwanych do system promptu Adama (F5)
jako `extra_context`. Embedder jest pluggable (HashingEmbedder offline w dev,
model produkcyjny w Frankfurt DC).
"""
from .models import MemoryChunk, MemoryKind
from .embedder import Embedder, HashingEmbedder, cosine_similarity, tokenize
from .service import MemoryService

__all__ = [
    "MemoryChunk",
    "MemoryKind",
    "Embedder",
    "HashingEmbedder",
    "cosine_similarity",
    "tokenize",
    "MemoryService",
]
