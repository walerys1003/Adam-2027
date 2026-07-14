# ADAM-2027 · Agent konwersacyjny dla seniorów (SilverTech, Poznań)

Monorepo projektu **Adam** — wyspecjalizowanego, empatycznego agenta głosowego
dla seniorów, zbudowanego na bazie open-source'owego voice-agenta AVA (MIT),
wraz z trzema warstwami interfejsu (Landing / Panel Opiekuna / Panel Admina),
Design Systemem i planem konwersji do aplikacji mobilnej (Capacitor iOS + Android).

> *„Adam nie jest aplikacją. Jest codzienną praktyką opieki. Interfejs ma to wspierać, nie zastępować."*

---

## 📁 Struktura repozytorium

```
ADAM-2027/
├── README.md                  ← ten plik
├── agent/                     ← Backend głosowy (Python + Asterisk ARI) — baza AVA v7.3.2
│   ├── src/                   ←   silnik AI, providerzy, pipeline'y, narzędzia
│   ├── admin_ui/              ←   panel operatora (React/TS + Python backend)
│   ├── docs/ · config/ · tests/
│   └── docker-compose*.yml    ←   orkiestracja (Asterisk, AI engine, local AI)
│
├── design-system/             ← Adam Design System (handoff gotowy do wdrożenia)
│   ├── 01-design-system/      ←   tokens.css / tokens.json / tailwind.config
│   ├── 02-landing/            ←   mockupy landingu (Wariant B Editorial — wybrany)
│   ├── 03-panel-opiekuna/     ←   mockup + SCREENS-MAP + API-CONTRACTS
│   ├── 04-panel-admina/       ←   mockup 20 ekranów + renderery JS
│   ├── 05-krytyczne/          ←   ekrany alertów RED/PURPLE + escalation ladder
│   ├── 07-assets/             ←   kolory, typografia, ikony, inwentarz komponentów
│   ├── README.md · DEVELOPER-HANDOFF.md · INSTRUKCJA-WDROZENIA.md
│
├── docs/                      ← Dokumentacja wdrożeniowa
│   ├── ROADMAP.md             ←   ★ roadmapa etapów + krytyczna analiza
│   ├── source-md/             ←   13 dokumentów źródłowych (Markdown)
│   └── source-docx/           ←   oryginalne .docx (archiwum)
│
└── rag/                       ← Baza wiedzy RAG (semantyczne wyszukiwanie w dokumentacji)
    ├── README.md
    ├── scripts/               ←   chunk_documents / build_embeddings / query
    └── index/                 ←   chunks.jsonl + embeddings.npy + meta.json
```

## 🎯 Czym jest Adam

- **Dla seniora (70–90 lat):** dzwoni sam (welfare-check 2×/dzień), rozmawia po polsku,
  przypomina o lekach, wykrywa kryzys, w razie zagrożenia dzwoni po pomoc. Senior używa
  **tylko telefonu** — bez aplikacji.
- **Dla opiekuna/rodziny:** panel webowy/mobilny — semafor stanu (🟢🟡🔴🟣), historia rozmów,
  wykres nastroju, adherence leków, alerty, zamawianie usług.
- **Dla koordynatora SilverTech (admin):** pełne zarządzanie seniorami, agentami AI,
  marketplace, wearables, raporty.

## 🚦 Kluczowe mechanizmy

| Mechanizm | Opis |
|---|---|
| **Czterokolorowy semafor (F3)** | 🟢 96% OK · 🟡 3.2% uwaga · 🔴 0.7% alarm (koordynator <18s) · 🟣 0.1% zagrożenie życia (112 <12s) |
| **Guardrails (F4)** | Pre-LLM (input seniora) + Post-LLM (blokada porad medycznych/obietnic) |
| **AI Act disclosure (F5)** | Adam przedstawia się jako AI w pierwszym zdaniu (art. 50, „limited risk") |
| **RODO (F12)** | Szyfrowanie PII (AES-256), retencja nagrań 30 dni, prawo do bycia zapomnianym |

## 🎨 Design System (źródło prawdy)

- **Kierunek:** Nordic humanism × Medical-premium
- **Kolory:** granat `#1a2744` (primary) · złoto matowe `#c8963e` (accent, nigdy gradient)
- **Fonty:** Fraunces (nagłówki, serif) + Geist (body) — darmowe, anti-AI-slop
- **Tło:** off-white `#fbfaf7` (nie kliniczna biel)
- **Semafor:** progresywny — pulsuje TYLKO red/purple (zapobiega alarm fatigue)

## 🧠 Baza wiedzy RAG

Cała dokumentacja (505 chunków) jest zaindeksowana semantycznie. Szybkie wyszukiwanie:

```bash
python3 rag/scripts/query.py "jak działa semafor eskalacji" --k 6
python3 rag/scripts/query.py "medication tracker" --phase F6
```

Szczegóły: [`rag/README.md`](rag/README.md).

## 🗺️ Roadmapa i status

Pełna roadmapa z krytyczną analizą: **[`docs/ROADMAP.md`](docs/ROADMAP.md)**.

| Etap | Zakres | Status |
|---|---|---|
| 0 | Fundament repo + RAG + roadmapa | ✅ w toku |
| 1 | Design System w kodzie (React) | ⏳ następny |
| 2 | Landing Page (Wariant B) | ⏳ |
| 3 | Kontrakty danych + mock API + RBAC | ⏳ |
| 4 | Panel Opiekuna (8 ekranów, mobile-first) | ⏳ |
| 5 | Panel Admina (redesign + nowe zakładki) | ⏳ |
| 6 | PWA | ⏳ |
| 7 | Capacitor iOS + Android | ⏳ (wymaga kont Apple/Google) |
| 8+ | Moduły backendu F1–F18 | ⏳ (wymaga infra docelowej) |

## ⚠️ Ważne uwarunkowania techniczne

Adam to **NIE** aplikacja Cloudflare Pages. Backend głosowy (Asterisk/ARI, scheduler,
PostgreSQL, Redis, kontenery Docker) wymaga docelowego serwera. To repo pełni rolę
**monorepo źródłowego** + środowiska pracy nad frontendem, Design Systemem i dokumentacją.
Zob. sekcję „Krytyczna analiza" w [`docs/ROADMAP.md`](docs/ROADMAP.md).

## 📝 Licencja

- Baza AVA: **MIT** (hkjarral/AVA-AI-Voice-Agent-for-Asterisk)
- Fonty: Fraunces + Geist — **SIL OFL** (darmowe komercyjnie)
- Design tokens + rozszerzenia Adam: proprietary **SilverTech**
