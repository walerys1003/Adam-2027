"""Testy F7 (ETAP 28) — streszczenia rozmów + ciągłość pamięci długoterminowej."""
from __future__ import annotations

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.memory import MemoryService, summarize_transcript


def _senior(session):
    return SeniorService(session).create(SeniorCreate(first_name="Zofia", last_name="Wójcik"))


def test_summarize_transcript_detects_mood_and_topics():
    transcript = (
        "adam: Dzień dobry\n"
        "senior: Czuję się dzisiaj bardzo smutno i samotnie, tęsknię za córką\n"
        "adam: Rozumiem\n"
        "senior: Zapomniałam wziąć tabletki"
    )
    digest = summarize_transcript(transcript, max_level="yellow", turn_count=4)
    assert digest.mood == "przygnębiony"
    assert "samotność" in digest.topics
    assert "leki" in digest.topics
    assert "4 tur" in digest.summary


def test_summarize_crisis_mood():
    d = summarize_transcript("senior: nie chcę żyć", max_level="purple", turn_count=1)
    assert d.mood == "kryzys"


def test_save_summary_and_recent(session):
    s = _senior(session)
    svc = MemoryService(session)
    svc.save_summary(s, "Rozmowa spokojna, senior pogodny.", mood="pogodny",
                     max_level="green", topics=["samopoczucie"], turn_count=3)
    rows = svc.recent_summaries(s.id)
    assert len(rows) == 1
    assert rows[0].mood == "pogodny"


def test_summary_also_stored_as_searchable_chunk(session):
    s = _senior(session)
    svc = MemoryService(session)
    svc.save_summary(s, "Senior mówił, że lubi kawę o 15 i słucha radia.",
                     mood="pogodny", turn_count=5, remember_as_chunk=True)
    hits = svc.retrieve(s.id, "kawa radio", top_k=3)
    assert any("kawę" in c.content for c, _ in hits)


def test_continuity_context(session):
    s = _senior(session)
    svc = MemoryService(session)
    svc.save_summary(s, "Pierwsza rozmowa: senior pogodny.", mood="pogodny")
    svc.save_summary(s, "Druga rozmowa: senior zmęczony.", mood="neutralny")
    ctx = svc.continuity_context(s.id, limit=2)
    assert "poprzednich rozmów" in ctx
    assert "Druga rozmowa" in ctx


def test_forget_removes_summaries(session):
    s = _senior(session)
    svc = MemoryService(session)
    svc.save_summary(s, "cokolwiek", remember_as_chunk=False)
    removed = svc.forget_senior(s.id)
    assert removed >= 1
    assert svc.recent_summaries(s.id) == []


def test_dialog_engine_injects_memory_context_into_prompt(session):
    """F7↔F5: kontekst ciągłości z MemoryService trafia do system promptu (ETAP 28)."""
    from adam_modules.voice.dialog import DialogEngine
    from adam_modules.voice.ports import RuleLLM

    s = _senior(session)
    svc = MemoryService(session)
    svc.save_summary(s, "Senior wspominał, że w niedzielę odwiedza go wnuczka Ania.",
                     mood="pogodny", topics=["rodzina"], turn_count=4)
    memory_ctx = svc.continuity_context(s.id, limit=2)
    assert "poprzednich rozmów" in memory_ctx

    engine = DialogEngine(
        RuleLLM(), senior_name="Zofia", senior_age=80,
        memory_context=memory_ctx, use_consensus=False,
    )
    assert engine.memory_context == memory_ctx
    assert "wnuczka Ania" in engine.system_prompt
    assert "poprzednich rozmów" in engine.system_prompt
