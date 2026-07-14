# ADAM-2027 · Baza wiedzy RAG

Lokalna, samodzielna baza wiedzy semantycznej zbudowana z całej dokumentacji
projektu (specyfikacje, plany faz F0–F18, design system). Pozwala szybko
odnajdywać właściwe fragmenty dokumentacji podczas rozbudowy projektu —
bez ręcznego przeszukiwania kilkunastu długich dokumentów.

## Dlaczego lokalny RAG (a nie API)

- **Offline / deterministyczny** — działa bez klucza API, w każdym środowisku.
- **Polski** — model `intfloat/multilingual-e5-small` dobrze rozumie polski.
- **Lekki** — 384 wymiary, indeks < 2 MB, CPU-only (bez GPU).
- **Wersjonowalny** — indeks trzymany w repo, reprodukowalny jedną komendą.

## Struktura

```
rag/
├── README.md
├── requirements.txt          # zależności do budowy indeksu
├── scripts/
│   ├── chunk_documents.py     # 1. dzieli dokumentację na semantyczne chunki
│   ├── build_embeddings.py    # 2. liczy embeddingi (multilingual-e5-small)
│   └── query.py               # 3. wyszukiwanie semantyczne (CLI)
└── index/
    ├── chunks.jsonl           # chunki + metadane (id, source, phase, section)
    ├── embeddings.npy         # macierz [N, 384] float32, znormalizowana
    └── meta.json              # metadane chunków w kolejności wierszy
```

## Użycie

### Wyszukiwanie (najczęstsze)

```bash
python3 rag/scripts/query.py "jak działa czterokolorowy semafor eskalacji"
python3 rag/scripts/query.py "medication adherence tracker" --k 8
python3 rag/scripts/query.py "design tokens kolory" --category design --full
python3 rag/scripts/query.py "guardrails pre-LLM filter" --phase F4
```

Opcje:
- `--k N` — liczba wyników (domyślnie 6)
- `--phase F0..F18` — filtr fazy wdrożeniowej
- `--category spec-plan|design` — filtr kategorii źródła
- `--full` — pełny tekst chunku zamiast podglądu

### Przebudowa indeksu (po zmianie dokumentacji)

```bash
pip install -r rag/requirements.txt          # torch CPU + sentence-transformers
python3 rag/scripts/chunk_documents.py        # regeneruje chunks.jsonl
python3 rag/scripts/build_embeddings.py       # regeneruje embeddings.npy + meta.json
```

## Statystyki bieżącego indeksu

- **505 chunków** (po deduplikacji 183 powtórzonych fragmentów między dokumentami)
- Kategorie: `spec-plan` 332 · `design` 173
- Model: `intfloat/multilingual-e5-small` (384 dim)
- Źródła: `docs/source-md/*.md` + `design-system/**/*.md`

## Jak to działa (technicznie)

1. **Chunking** — dokumenty dzielone są po prawdziwych nagłówkach Markdown
   (`#`…`####`). Sekcje > 1800 znaków dzielone są na okna z zakładką 250 znaków,
   żeby nie tracić kontekstu na granicy. Każdy chunk niesie metadane:
   źródło, tytuł sekcji, wykrytą fazę (F0–F18), kategorię.
2. **Deduplikacja** — te same treści powtarzają się między dokumentami
   (`PEŁNY DOKUMENT`, `FAZA 0-5`, `Fazy F6-F12`…). Identyczne fragmenty
   (po normalizacji whitespace) są pomijane.
3. **Embeddingi** — każdy chunk → wektor 384D (prefiks `passage:`),
   znormalizowany. Zapytanie → wektor (prefiks `query:`).
4. **Wyszukiwanie** — cosine similarity (iloczyn skalarny znormalizowanych
   wektorów), sortowanie malejąco, opcjonalne filtry metadanych.
