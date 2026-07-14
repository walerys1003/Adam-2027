#!/usr/bin/env python3
"""
ADAM-2027 · RAG embeddings builder
===================================
Wczytuje rag/index/chunks.jsonl, liczy embeddingi lokalnym modelem
multilingual (obsługa polskiego) i zapisuje:
  - rag/index/embeddings.npy   (macierz float32 [N, D], znormalizowana)
  - rag/index/meta.json        (metadane chunków w kolejności wierszy)

Model: intfloat/multilingual-e5-small (384 wymiary, dobra jakość PL, mały).
Prefiks 'passage:' wymagany przez rodzinę e5 dla dokumentów.
"""
import os
import json
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IDX = os.path.join(ROOT, "rag", "index")
CHUNKS = os.path.join(IDX, "chunks.jsonl")
EMB_OUT = os.path.join(IDX, "embeddings.npy")
META_OUT = os.path.join(IDX, "meta.json")
MODEL_NAME = "intfloat/multilingual-e5-small"


def main():
    from sentence_transformers import SentenceTransformer

    rows = []
    with open(CHUNKS, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    print(f"Wczytano {len(rows)} chunków. Ładowanie modelu {MODEL_NAME} ...")

    model = SentenceTransformer(MODEL_NAME)
    texts = [f"passage: {r['text']}" for r in rows]

    print("Liczenie embeddingów ...")
    emb = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")

    np.save(EMB_OUT, emb)
    meta = [
        {k: r[k] for k in ("id", "source", "filename", "category", "section", "phase", "chars")}
        for r in rows
    ]
    with open(META_OUT, "w", encoding="utf-8") as fh:
        json.dump({"model": MODEL_NAME, "dim": int(emb.shape[1]), "count": len(rows), "meta": meta},
                  fh, ensure_ascii=False)

    print(f"OK: embeddingi {emb.shape} -> {os.path.relpath(EMB_OUT, ROOT)}")
    print(f"    metadane -> {os.path.relpath(META_OUT, ROOT)}")


if __name__ == "__main__":
    main()
