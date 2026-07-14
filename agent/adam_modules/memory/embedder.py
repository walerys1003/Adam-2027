"""
Embeddery dla pamięci semantycznej (F7.1).

Interfejs `Embedder` pozwala podmienić model bez zmiany reszty kodu:
- HashingEmbedder — deterministyczny, bez zależności zewnętrznych (dev/test,
  fallback offline). Hashing trick + normalizacja L2.
- W produkcji (Frankfurt DC) rejestruje się `OpenAIEmbedder` lub lokalny
  model (np. sentence-transformers) implementujący ten sam protokół.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol, Sequence

_TOKEN_RE = re.compile(r"[\wąćęłńóśźż]+", re.IGNORECASE | re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


class Embedder(Protocol):
    dim: int

    def embed(self, text: str) -> list[float]:  # pragma: no cover - protokół
        ...


class HashingEmbedder:
    """Deterministyczny embedder oparty o hashing trick (bag-of-words).

    Nie wymaga sieci ani modeli — nadaje się do testów i pracy offline.
    Podobne semantycznie zdania dzielące słowa dają wysokie cosine sim.
    """

    def __init__(self, dim: int = 256):
        self.dim = dim

    def _bucket(self, token: str) -> tuple[int, float]:
        h = hashlib.md5(token.encode("utf-8")).digest()
        idx = int.from_bytes(h[:4], "big") % self.dim
        sign = 1.0 if h[4] & 1 else -1.0
        return idx, sign

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        tokens = tokenize(text)
        for tok in tokens:
            idx, sign = self._bucket(tok)
            vec[idx] += sign
        return l2_normalize(vec)


def l2_normalize(vec: Sequence[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return list(vec)
    return [v / norm for v in vec]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Wektory różnej długości")
    dot = sum(x * y for x, y in zip(a, b))
    # a i b są zwykle znormalizowane, ale liczymy bezpiecznie
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)
