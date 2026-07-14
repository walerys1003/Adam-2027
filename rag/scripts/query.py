#!/usr/bin/env python3
"""
ADAM-2027 · RAG query
=====================
Semantyczne wyszukiwanie w bazie wiedzy projektu.

Użycie:
    python3 rag/scripts/query.py "jak działa semafor eskalacji"
    python3 rag/scripts/query.py "medication tracker" --k 8 --phase F6
    python3 rag/scripts/query.py "design tokens kolory" --category design --full

Zwraca top-K najbardziej dopasowanych chunków z metadanymi i podglądem.
Model e5 wymaga prefiksu 'query:' dla zapytań.
"""
import os
import sys
import json
import argparse
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IDX = os.path.join(ROOT, "rag", "index")
CHUNKS = os.path.join(IDX, "chunks.jsonl")
EMB = os.path.join(IDX, "embeddings.npy")
META = os.path.join(IDX, "meta.json")

_texts_cache = None


def load_texts():
    global _texts_cache
    if _texts_cache is None:
        _texts_cache = {}
        with open(CHUNKS, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    o = json.loads(line)
                    _texts_cache[o["id"]] = o["text"]
    return _texts_cache


def main():
    ap = argparse.ArgumentParser(description="ADAM-2027 RAG query")
    ap.add_argument("query", help="tekst zapytania")
    ap.add_argument("--k", type=int, default=6, help="liczba wyników")
    ap.add_argument("--phase", default=None, help="filtr fazy np. F6")
    ap.add_argument("--category", default=None, help="filtr kategorii: spec-plan | design")
    ap.add_argument("--full", action="store_true", help="pełny tekst chunku zamiast podglądu")
    args = ap.parse_args()

    from sentence_transformers import SentenceTransformer

    with open(META, "r", encoding="utf-8") as fh:
        meta_obj = json.load(fh)
    meta = meta_obj["meta"]
    emb = np.load(EMB)

    model = SentenceTransformer(meta_obj["model"])
    q = model.encode([f"query: {args.query}"], normalize_embeddings=True,
                     convert_to_numpy=True).astype("float32")[0]

    sims = emb @ q  # cosine (znormalizowane)

    # filtry
    order = np.argsort(-sims)
    results = []
    texts = load_texts()
    for i in order:
        m = meta[i]
        if args.phase and m.get("phase") != args.phase:
            continue
        if args.category and m.get("category") != args.category:
            continue
        results.append((float(sims[i]), m))
        if len(results) >= args.k:
            break

    print(f"\n🔎 Zapytanie: {args.query!r}  (top {len(results)})\n" + "=" * 70)
    for rank, (score, m) in enumerate(results, 1):
        txt = texts.get(m["id"], "")
        preview = txt if args.full else (txt[:360] + ("…" if len(txt) > 360 else ""))
        phase = f" · {m['phase']}" if m.get("phase") else ""
        print(f"\n#{rank}  [{score:.3f}]  {m['category']}{phase}")
        print(f"    źródło: {m['source']}")
        print(f"    sekcja: {m['section']}")
        print("    " + preview.replace("\n", "\n    "))
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
