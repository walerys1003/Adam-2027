#!/usr/bin/env python3
"""
ADAM-2027 · RAG chunker
=======================
Dzieli dokumentację projektu (Markdown skonwertowany z .docx + pliki .md
z design-system i agenta) na semantyczne chunki gotowe do embeddingu.

Strategia chunkowania:
- Podział po nagłówkach Markdown (## / ###) jako granicach semantycznych.
- Sekcje dłuższe niż MAX_CHARS są dzielone na okna z zakładką (overlap),
  żeby nie tracić kontekstu na granicy.
- Każdy chunk niesie metadane: źródłowy plik, tytuł sekcji, faza (F0..F18),
  kategoria (spec/plan/design/mobile/agent-code).

Wyjście: rag/index/chunks.jsonl
"""
import os
import re
import json
import glob
import hashlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "rag", "index")
OUT_FILE = os.path.join(OUT_DIR, "chunks.jsonl")

MAX_CHARS = 1800          # ~450-600 tokenów
OVERLAP_CHARS = 250       # zakładka między oknami

# Źródła dokumentacji do zindeksowania (kategoria -> glob)
SOURCES = [
    ("spec-plan", os.path.join(ROOT, "docs", "source-md", "*.md")),
    ("design", os.path.join(ROOT, "design-system", "**", "*.md")),
    ("design", os.path.join(ROOT, "design-system", "*.md")),
]

# Wykrywanie fazy F0..F18 z tekstu / nazwy pliku
PHASE_RE = re.compile(r"\bF(\d{1,2})\b")


def detect_phase(text, filename):
    for src in (filename, text[:400]):
        m = PHASE_RE.search(src or "")
        if m:
            n = int(m.group(1))
            if 0 <= n <= 18:
                return f"F{n}"
    return None


def split_by_headers(md):
    """Zwraca listę (nagłówek, treść) dzieląc TYLKO po prawdziwych nagłówkach
    Markdown (linia zaczynająca się od 1-4 znaków # + spacja)."""
    lines = md.splitlines()
    sections = []
    cur_head = "Wprowadzenie"
    cur_body = []
    for ln in lines:
        if re.match(r"^#{1,4}\s+\S", ln):
            if cur_body:
                sections.append((cur_head, "\n".join(cur_body).strip()))
            cur_head = re.sub(r"^#+\s*", "", ln).strip()
            cur_body = []
        else:
            cur_body.append(ln)
    if cur_body:
        sections.append((cur_head, "\n".join(cur_body).strip()))
    return sections


def window_text(text):
    """Dzieli długi tekst na okna z overlap."""
    if len(text) <= MAX_CHARS:
        return [text]
    windows = []
    start = 0
    while start < len(text):
        end = min(start + MAX_CHARS, len(text))
        # spróbuj domknąć na końcu zdania/akapitu
        slice_ = text[start:end]
        last_break = max(slice_.rfind("\n"), slice_.rfind(". "))
        if last_break > MAX_CHARS * 0.6 and end < len(text):
            end = start + last_break + 1
            slice_ = text[start:end]
        windows.append(slice_.strip())
        if end >= len(text):
            break
        start = end - OVERLAP_CHARS
    return [w for w in windows if w]


def make_id(source, idx):
    h = hashlib.sha1(f"{source}:{idx}".encode()).hexdigest()[:12]
    return f"{h}"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    chunks = []
    seen_files = set()
    seen_hashes = {}   # dedup: hash treści -> id pierwszego chunku
    dup_count = 0

    for category, pattern in SOURCES:
        for path in glob.glob(pattern, recursive=True):
            if path in seen_files:
                continue
            seen_files.add(path)
            rel = os.path.relpath(path, ROOT)
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                md = fh.read()
            if not md.strip():
                continue
            filename = os.path.basename(path)
            sections = split_by_headers(md)
            for head, body in sections:
                if not body.strip():
                    continue
                phase = detect_phase(head + "\n" + body, filename)
                for win in window_text(body):
                    if len(win) < 40:
                        continue
                    # deduplikacja identycznych fragmentów (te same treści
                    # powtarzają się między PEŁNY / FAZA 0-5 / Fazy F6-F12 itd.)
                    norm = re.sub(r"\s+", " ", win).strip().lower()
                    chash = hashlib.sha1(norm.encode()).hexdigest()
                    if chash in seen_hashes:
                        dup_count += 1
                        continue
                    idx = len(chunks)
                    cid = make_id(rel, idx)
                    seen_hashes[chash] = cid
                    chunks.append({
                        "id": cid,
                        "source": rel,
                        "filename": filename,
                        "category": category,
                        "section": head[:200],
                        "phase": phase,
                        "text": f"# {head}\n\n{win}",
                        "chars": len(win),
                    })
    print(f"    (pominięto {dup_count} duplikatów treści)")

    with open(OUT_FILE, "w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")

    # Statystyki
    by_cat = {}
    by_phase = {}
    for c in chunks:
        by_cat[c["category"]] = by_cat.get(c["category"], 0) + 1
        if c["phase"]:
            by_phase[c["phase"]] = by_phase.get(c["phase"], 0) + 1
    print(f"OK: {len(chunks)} chunków zapisano do {os.path.relpath(OUT_FILE, ROOT)}")
    print(f"    kategorie: {by_cat}")
    print(f"    fazy: {dict(sorted(by_phase.items(), key=lambda x: int(x[0][1:])))}")


if __name__ == "__main__":
    main()
