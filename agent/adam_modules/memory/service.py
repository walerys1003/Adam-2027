"""
MemoryService — zapis i retrieval pamięci semantycznej (F7).

remember()  — zapisuje fragment z embeddingiem.
retrieve()  — top-k najbardziej podobnych fragmentów (cosine) dla zapytania.
build_context() — składa fragmenty w blok tekstu do wstrzyknięcia do system
                  promptu Adama (F5.build_system_prompt(extra_context=...)).
"""
from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from adam_modules.seniors.models import Senior
from .models import MemoryChunk, MemoryKind, ConversationSummary
from .embedder import Embedder, HashingEmbedder, cosine_similarity


class MemoryService:
    def __init__(self, session: Session, embedder: Embedder | None = None):
        self.session = session
        self.embedder = embedder or HashingEmbedder()
        self._model_tag = f"hashing-{self.embedder.dim}" if isinstance(self.embedder, HashingEmbedder) else "custom"

    def remember(
        self,
        senior: Senior,
        content: str,
        kind: MemoryKind = MemoryKind.conversation,
        source_ref: str | None = None,
    ) -> MemoryChunk:
        vec = self.embedder.embed(content)
        chunk = MemoryChunk(
            senior_id=senior.id,
            kind=kind,
            content=content,
            embedding=json.dumps(vec),
            embed_model=self._model_tag,
            source_ref=source_ref,
        )
        self.session.add(chunk)
        self.session.flush()
        return chunk

    def _all_for_senior(self, senior_id: int, kinds: list[MemoryKind] | None = None) -> list[MemoryChunk]:
        stmt = select(MemoryChunk).where(MemoryChunk.senior_id == senior_id)
        if kinds:
            stmt = stmt.where(MemoryChunk.kind.in_(kinds))
        return list(self.session.scalars(stmt))

    def retrieve(
        self,
        senior_id: int,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
        kinds: list[MemoryKind] | None = None,
    ) -> list[tuple[MemoryChunk, float]]:
        """Zwraca listę (chunk, score) posortowaną malejąco po podobieństwie."""
        q_vec = self.embedder.embed(query)
        scored: list[tuple[MemoryChunk, float]] = []
        for chunk in self._all_for_senior(senior_id, kinds):
            try:
                vec = json.loads(chunk.embedding)
            except (ValueError, TypeError):
                continue
            if len(vec) != len(q_vec):
                continue  # embedding z innego modelu — pomiń
            score = cosine_similarity(q_vec, vec)
            if score >= min_score:
                scored.append((chunk, score))
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:top_k]

    def build_context(
        self,
        senior_id: int,
        query: str,
        top_k: int = 5,
        min_score: float = 0.15,
    ) -> str:
        """Blok kontekstu do wstrzyknięcia do promptu. Pusty string, gdy brak."""
        hits = self.retrieve(senior_id, query, top_k=top_k, min_score=min_score)
        if not hits:
            return ""
        lines = ["Co pamiętam o rozmówcy (użyj naturalnie, nie cytuj wprost):"]
        for chunk, score in hits:
            lines.append(f"- [{chunk.kind.value}] {chunk.content}")
        return "\n".join(lines)

    def forget_senior(self, senior_id: int) -> int:
        """RODO (F12) — usuwa całą pamięć seniora. Zwraca liczbę usuniętych."""
        chunks = self._all_for_senior(senior_id)
        for c in chunks:
            self.session.delete(c)
        # usuń również streszczenia rozmów
        summaries = list(self.session.scalars(
            select(ConversationSummary).where(ConversationSummary.senior_id == senior_id)
        ))
        for s in summaries:
            self.session.delete(s)
        self.session.flush()
        return len(chunks) + len(summaries)

    # ---- F7 (ETAP 28): streszczenia rozmów (pamięć długoterminowa) ----
    def save_summary(
        self,
        senior: Senior,
        summary: str,
        *,
        conversation_ref: str | None = None,
        mood: str | None = None,
        max_level: str | None = None,
        topics: list[str] | None = None,
        turn_count: int = 0,
        remember_as_chunk: bool = True,
    ) -> ConversationSummary:
        """Zapisuje streszczenie rozmowy; opcjonalnie też jako przeszukiwalny chunk."""
        row = ConversationSummary(
            senior_id=senior.id,
            conversation_ref=conversation_ref,
            summary=summary,
            mood=mood,
            max_level=max_level,
            topics=json.dumps(topics or [], ensure_ascii=False),
            turn_count=turn_count,
        )
        self.session.add(row)
        if remember_as_chunk:
            # streszczenie trafia też do pamięci wektorowej → retrieval w kolejnych rozmowach
            self.remember(senior, summary, kind=MemoryKind.conversation,
                          source_ref=conversation_ref)
        self.session.flush()
        return row

    def recent_summaries(self, senior_id: int, limit: int = 5) -> list[ConversationSummary]:
        return list(self.session.scalars(
            select(ConversationSummary).where(ConversationSummary.senior_id == senior_id)
            .order_by(ConversationSummary.id.desc()).limit(limit)
        ))

    def continuity_context(self, senior_id: int, limit: int = 2) -> str:
        """Blok „ciągłości" z ostatnich rozmów do wstrzyknięcia do promptu."""
        rows = self.recent_summaries(senior_id, limit=limit)
        if not rows:
            return ""
        lines = ["Z poprzednich rozmów (nawiąż naturalnie, jeśli pasuje):"]
        for r in rows:
            mood = f" (nastrój: {r.mood})" if r.mood else ""
            lines.append(f"- {r.summary}{mood}")
        return "\n".join(lines)
