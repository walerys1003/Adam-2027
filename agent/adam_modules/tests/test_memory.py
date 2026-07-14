"""Testy F7 — pamięć semantyczna (embedder + retrieval + context injection)."""
import math

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.memory import (
    MemoryService,
    MemoryKind,
    HashingEmbedder,
    cosine_similarity,
    tokenize,
)


def _make_senior(session, first="Anna", last="Nowak"):
    return SeniorService(session).create(
        SeniorCreate(first_name=first, last_name=last, phone="+48111222333")
    )


# ---- embedder ----
def test_tokenize_polish():
    toks = tokenize("Pani Anna lubi kawę o 15!")
    assert "kawę" in toks
    assert "anna" in toks
    assert "15" in toks


def test_embedder_deterministic():
    e = HashingEmbedder(dim=128)
    v1 = e.embed("lubię herbatę rano")
    v2 = e.embed("lubię herbatę rano")
    assert v1 == v2
    assert len(v1) == 128


def test_embedding_is_normalized():
    e = HashingEmbedder()
    v = e.embed("test normalizacji wektora")
    norm = math.sqrt(sum(x * x for x in v))
    assert abs(norm - 1.0) < 1e-6


def test_cosine_similarity_bounds():
    e = HashingEmbedder()
    a = e.embed("senior lubi spacery po parku")
    b = e.embed("senior lubi spacery po parku")
    assert abs(cosine_similarity(a, b) - 1.0) < 1e-6
    c = e.embed("zupełnie inne słowa xyz qwerty")
    assert cosine_similarity(a, c) < cosine_similarity(a, b)


def test_empty_text_embedding():
    e = HashingEmbedder()
    v = e.embed("")
    assert len(v) == e.dim
    assert all(x == 0.0 for x in v)


# ---- service ----
def test_remember_and_retrieve(session):
    senior = _make_senior(session)
    svc = MemoryService(session)
    svc.remember(senior, "Pan Jan lubi pić kawę o godzinie 15", MemoryKind.preference)
    svc.remember(senior, "Pan Jan ma wnuczkę Zosię, która go odwiedza w weekendy")
    svc.remember(senior, "Pan Jan chodzi na spacery do parku Sołacz")

    hits = svc.retrieve(senior.id, "o której kawa dla pana Jana", top_k=3)
    assert len(hits) >= 1
    # najbardziej podobny powinien dotyczyć kawy
    top_chunk, top_score = hits[0]
    assert "kawę" in top_chunk.content or "kawa" in top_chunk.content.lower()
    assert top_score > 0


def test_retrieve_respects_top_k(session):
    senior = _make_senior(session)
    svc = MemoryService(session)
    for i in range(6):
        svc.remember(senior, f"fakt numer {i} o seniorze i jego dniu")
    hits = svc.retrieve(senior.id, "fakt o seniorze", top_k=3)
    assert len(hits) == 3


def test_retrieve_filters_by_kind(session):
    senior = _make_senior(session)
    svc = MemoryService(session)
    svc.remember(senior, "lubi muzykę klasyczną", MemoryKind.preference)
    svc.remember(senior, "rozmowa o pogodzie wczoraj", MemoryKind.conversation)
    hits = svc.retrieve(senior.id, "muzyka", top_k=5, kinds=[MemoryKind.preference])
    assert all(c.kind == MemoryKind.preference for c, _ in hits)


def test_retrieve_scoped_to_senior(session):
    a = _make_senior(session, "Anna", "A")
    b = _make_senior(session, "Barbara", "B")
    svc = MemoryService(session)
    svc.remember(a, "Anna lubi ogród i kwiaty")
    svc.remember(b, "Barbara lubi szachy")
    hits = svc.retrieve(b.id, "hobby", top_k=5)
    assert all(c.senior_id == b.id for c, _ in hits)


def test_build_context(session):
    senior = _make_senior(session)
    svc = MemoryService(session)
    svc.remember(senior, "Pan Jan lubi pić kawę o godzinie 15", MemoryKind.preference)
    ctx = svc.build_context(senior.id, "kawa jan godzina", top_k=3, min_score=0.0)
    assert "kawę" in ctx
    assert ctx.startswith("Co pamiętam")


def test_build_context_empty_when_no_memory(session):
    senior = _make_senior(session)
    svc = MemoryService(session)
    assert svc.build_context(senior.id, "cokolwiek") == ""


def test_forget_senior_rodo(session):
    senior = _make_senior(session)
    svc = MemoryService(session)
    svc.remember(senior, "fakt 1")
    svc.remember(senior, "fakt 2")
    removed = svc.forget_senior(senior.id)
    assert removed == 2
    assert svc.retrieve(senior.id, "fakt", top_k=5) == []


def test_context_injects_into_prompt(session):
    """F7 <-> F5: kontekst pamięci trafia do system promptu Adama."""
    from adam_modules.semaphore import build_system_prompt

    senior = _make_senior(session)
    svc = MemoryService(session)
    svc.remember(senior, "Pan Jan lubi rozmawiać o piłce nożnej", MemoryKind.preference)
    ctx = svc.build_context(senior.id, "piłka nożna jan", min_score=0.0)
    prompt = build_system_prompt(
        senior_name="Jan", senior_age=78, extra_context=ctx
    )
    assert "piłce" in prompt or "piłka" in prompt.lower()
