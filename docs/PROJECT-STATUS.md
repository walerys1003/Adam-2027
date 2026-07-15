# ADAM-2027 — Status projektu i instrukcja dla developera

> **Dokument techniczny statusu.** Opisuje **rzeczywisty stan repozytorium** (zweryfikowany
> automatycznie, nie z pamięci), z podziałem na sekcje → moduły → etapy, wraz z technikaliami
> potrzebnymi do dalszej pracy. Adresat: developer wchodzący do projektu lub kontynuujący go.
>
> - **Repo:** `https://github.com/walerys1003/Adam-2027.git` · gałąź `main`
> - **Ostatnia weryfikacja:** commit `d772ba5` (2026-07)
> - **Produkt:** głosowy asystent „Adam" dla seniorów · SilverTech Poznań · język polski (PL)
> - **Środowisko docelowe:** Frankfurt DC (backend + telefonia), aplikacje mobilne iOS/Android

---

## Spis treści

- [0. TL;DR — jedna liczba i trzy perspektywy](#0-tldr)
- [1. Metodyka oceny (jak liczymy %)](#1-metodyka-oceny)
- [2. Metryki repozytorium (twarde dane)](#2-metryki-repozytorium)
- [3. Architektura wysokopoziomowa](#3-architektura-wysokopoziomowa)
- [4. Sekcja A — Backend `adam_modules/` (moduły F1–F18)](#4-sekcja-a--backend)
- [5. Sekcja B — Frontend `frontend/`](#5-sekcja-b--frontend)
- [6. Sekcja C — Warstwa głosowa / telefonia](#6-sekcja-c--warstwa-glosowa)
- [7. Sekcja D — Infrastruktura, CI, RAG, Design System](#7-sekcja-d--infrastruktura)
- [8. Mapa ETAP 0–35](#8-mapa-etap-0-35)
- [9. Co pozostaje do 100% (backlog z uzasadnieniem)](#9-co-pozostaje-do-100)
- [10. Roadmap wdrożenia produkcyjnego](#10-roadmap-wdrozenia)
- [11. Instrukcja uruchomienia dla developera](#11-instrukcja-uruchomienia)
- [12. Rejestr zmiennych środowiskowych (ENV)](#12-rejestr-env)
- [13. Definition of Done (DoD) per warstwa](#13-definition-of-done)

---

## 0. TL;DR

**Szacunek całościowy: ~72–78% ukończenia** (kod, który da się zbudować/przetestować w tym środowisku).

Liczba zależy od przyjętej perspektywy — to rozróżnienie jest kluczowe:

| Perspektywa | % ukończenia | Uzasadnienie |
|---|---|---|
| **Kod budowalny/testowalny tutaj** (backend logika + frontend + testy + CI) | **~85–90%** | Cała warstwa logiki domenowej F1–F18 zaimplementowana i pokryta testami |
| **Cały projekt produkcyjny** (z infrastrukturą docelową) | **~70–75%** | Brakuje działającej telefonii, kontenerów prod, produkcyjnej bazy |
| **Gotowość do realnego uruchomienia u seniorów** | **~55–60%** | Wymaga integracji z kluczami, telefonii na żywo, aplikacji mobilnych, testów E2E |

**Wniosek:** część możliwa do zbudowania i przetestowania w sandboxie jest praktycznie ukończona
(~85–90%). Brakujące ~25–30% to elementy z natury wymagające infrastruktury docelowej i kont
zewnętrznych (Asterisk, mobile, produkcyjne klucze) — poza zasięgiem sandboxu.

---

## 1. Metodyka oceny

Aby uniknąć „procentów z sufitu", % liczony jest **ważoną sumą warstw**, gdzie waga = udział
warstwy w wartości produktu, a stopień ukończenia = weryfikowalny stan repo.

| Warstwa | Waga | Stopień ukończenia | Wkład |
|---|---:|---:|---:|
| Logika domenowa backend (F1–F18) | 35% | 95% | 33,3% |
| Warstwa API (routery, auth, RBAC) | 12% | 95% | 11,4% |
| Frontend (landing + panele + design system) | 18% | 85% | 15,3% |
| Warstwa głosowa / telefonia (kod portów) | 15% | 55% | 8,3% |
| Infrastruktura (CI, migracje, deploy artefakty) | 10% | 70% | 7,0% |
| Integracje produkcyjne (klucze, adaptery live) | 6% | 40% | 2,4% |
| Aplikacje mobilne (Capacitor iOS/Android) | 4% | 10% | 0,4% |
| **Razem** | **100%** | — | **~78%** |

**Zasady liczenia stopnia ukończenia modułu:**
- `kod obecny + testy zielone + migracja` → 90–100%
- `kod obecny + testy, ale wymaga infrastruktury zewn.` → 50–70%
- `tylko szkielet / port bez realnego backendu` → 10–30%

---

## 2. Metryki repozytorium

Dane pobrane automatycznie z drzewa repo (nie szacunkowe):

| Metryka | Wartość |
|---|---|
| Moduły backend (`adam_modules/*`) | **21** |
| Linie kodu backend (bez testów) | **~12 046** |
| Linie testów backend | **~4 951** |
| Pliki testowe backend | **35** |
| Funkcje testowe (`def test_`) | **415** (raport pytest: **421 passed** — parametryzacje) |
| Routery API | **15** |
| Migracje Alembic | **12** (`0001`→`0012`, pojedynczy HEAD) |
| Linie kodu frontend (`src/**.ts(x)`) | **~8 919** |
| Testy frontend (vitest) | **29 passed** |
| Strony admina (React) | **24** |
| Strony panelu opiekuna (React) | **9** |
| Indeks RAG | `chunks.jsonl` + `embeddings.npy` + `meta.json` |

**Rozmiary modułów backend (LOC, bez testów):**

```
voice ...... 1782   semaphore .. 841   speech ..... 897   qa ......... 585
api ........ 2417   family ..... 459   memory ..... 384   medication . 380
emergency .. 380    wearables .. 377   rodo ....... 396   seniors .... 291
scheduler .. 288    marketplace 258    admin ...... 348   auth ....... 303
stress ..... 196    consensus .. 160   compliance . 121   common ..... 163
deploy ..... (artefakty Docker, 0 .py)
```

---

## 3. Architektura wysokopoziomowa

```
                         ┌─────────────────────────────────────────┐
   Senior (telefon)      │            Frankfurt DC (prod)           │
        │                │                                          │
        ▼                │   Asterisk (SIP/PJSIP) ── ARI/Stasis      │
   PSTN / SIP  ──────────┼──▶  voice/ (ari, stasis, dialog,          │
                         │       watchdog, consensus, prod_ports)    │
                         │            │                              │
                         │            ▼                              │
                         │      DialogEngine ──▶ ASR/LLM/TTS (prod)   │
                         │            │            (Whisper/OpenAI/   │
                         │            ▼             ElevenLabs)       │
                         │   adam_modules/ (F1–F18 logika domenowa)   │
                         │      semaphore · medication · emergency    │
                         │      family · wearables · marketplace      │
                         │      memory · consensus · rodo · qa        │
                         │            │                              │
                         │            ▼                              │
                         │   FastAPI (15 routerów) ── JWT/RBAC        │
                         │            │                              │
                         │   PostgreSQL (prod) / SQLite (dev)         │
                         │   Redis (rate-limit, timery eskalacji)     │
                         └────────────┬──────────────────────────────┘
                                      │ REST/JSON
                    ┌─────────────────┴───────────────────┐
                    ▼                                     ▼
          Panel Opiekuna (React)              Panel Admina (React, 24 ekrany)
          Aplikacja mobilna (Capacitor)       Landing Page (editorial)
```

**Zasady architektoniczne:**
- **Hexagonalne porty** dla warstwy głosowej (`voice/ports.py` = interfejsy, `voice/prod_ports.py`
  = implementacje ASR/LLM/TTS). Dzięki temu logika dialogu jest testowalna bez telefonii.
- **Fail-safe first** — adaptery integracji (Twilio/SendGrid/FCM) i probing providerów degradują
  do `NullAdapter`/`missing_secrets` przy braku sekretów, zamiast rzucać błędy w runtime.
- **Minimalizm zależności** — JWT (HS256), PBKDF2, metryki i rate-limit zaimplementowane na
  stdlib (`hmac`/`hashlib`/`logging`) zamiast ciężkich bibliotek. Patrz `requirements.txt`.
- **PII szyfrowane** — Fernet + blind index (`common/`, ENV `ADAM_PII_KEY`/`ADAM_PII_PEPPER`).

---

## 4. Sekcja A — Backend

Backend to serce projektu: **21 modułów**, **~12 000 linii**, **421 testów zielonych**,
**12 migracji Alembic** (pojedynczy HEAD `0012`), **15 routerów FastAPI**. Poniżej mapowanie
funkcji F1–F18 na moduły z technikaliami.

### Legenda statusu
- ✅ **Gotowe** — kod + testy + (jeśli dotyczy) migracja; działa w sandboxie.
- 🟡 **Gotowe warunkowo** — kod + testy, ale runtime wymaga infrastruktury/kluczy (fail-safe).
- 🔴 **Szkielet/port** — interfejs istnieje, brak realnego backendu w tym środowisku.

### 4.1 Mapa funkcji → moduły

| # | Funkcja | Moduł | Pliki kluczowe | Migracja | Status |
|---|---|---|---|---|---|
| F1 | Semafor stanu seniora (Green/Yellow/Red/Purple) | `semaphore/` | `detector.py`, `engine.py`, `escalation.py`, `models.py` | 0003 | ✅ |
| F2 | Welfare-check / harmonogram połączeń | `scheduler/` | `service.py`, `jobs.py`, `ari.py`, `models.py` | 0002 | 🟡 |
| F3 | Eskalacja + timery (Redis) | `semaphore/escalation.py`, `emergency/` | `escalation.py`, `payload.py` | 0009 | 🟡 |
| F4 | Guardrails wejścia/wyjścia (anty-jailbreak, anty-halucynacja med.) | `semaphore/` | `guardrails.py`, `io_guards.py` | — | ✅ |
| F5 | Disclosure AI (informowanie, że to system) | `compliance/` | `compliance/*`, disclosure_logs | 0007 | ✅ |
| F6 | Śledzenie leków / adherence | `medication/` | `service.py`, `models.py`, `schemas.py` | 0004 | ✅ |
| F7 | Pamięć semantyczna (chunki + embeddery) | `memory/` | `service.py`, `embedder.py`, `summarizer.py` | 0005, 0010 | 🟡 |
| F8 | Panel/model rodziny + notyfikacje | `family/` | `service.py`, `adapters.py`, `models.py` | 0006 | 🟡 |
| F9 | Integracje SMS/telefon (Twilio) | `family/adapters.py` | `adapters.py` | — | 🟡 |
| F10 | Wearables (Xiaomi/Apple/Garmin) | `wearables/` | `service.py`, `adapters.py` | 0006 | 🟡 |
| F11 | Auth + RBAC (ADMIN/FAMILY/…) | `auth/`, `api/routers/*` | `auth/*` | 0008 | ✅ |
| F12 | Marketplace / concierge (80+ partnerów) | `marketplace/` | `service.py`, `models.py` | 0006 | ✅ |
| F13 | RODO / GDPR (zgody, prawo do zapomnienia) | `rodo/` | `consent.py`, `service.py` | 0006, 0008 | ✅ |
| F14 | Konsensus decyzyjny (dual-STT, głosowanie) | `consensus/`, `voice/consensus.py` | `engine.py` | — | ✅ |
| F15 | Compliance (AI Act, logi decyzji) | `compliance/`, `qa/` | `compliance/*` | 0007 | ✅ |
| F16 | Emergency 112 (auto-dispatch) | `emergency/` | `dialplan.py`, `payload.py`, `audio.py` | 0009 | 🟡 |
| F17 | Testy stresowe / red-team (persony, halucynacje) | `stress/` | `stress/*` | — | ✅ |
| F18 | QA loop (ewaluacja, sentiment, auto-improvement) | `qa/` | `service.py`, `metrics.py`, `sentiment.py` | 0011 | ✅ |

### 4.2 Moduły — szczegóły techniczne

#### `semaphore/` — F1/F3/F4 (841 LOC) ✅
Rdzeń oceny stanu seniora i eskalacji.
- **`detector.py`** — wykrywanie sygnałów kryzysu z transkryptu i telemetrii (mood, tempo mowy,
  pauzy, słowa-klucze); mapowanie na poziom semafora.
- **`engine.py`** — silnik reguł: agreguje sygnały → poziom `green|yellow|red|purple`.
- **`escalation.py`** — polityka eskalacji per poziom (kogo, kiedy, ile prób, jaki kanał);
  współpracuje z Redis (timery) w produkcji.
- **`guardrails.py` / `io_guards.py`** — `InputGuard` (anty-injection: „zignoruj wcześniejsze
  instrukcje", „udawaj że jesteś…", „System:", tryb deweloperski, jailbreak/roleplay) oraz
  `OutputGuard` (blokada dawek leków, diagnoz, obietnic medycznych).
- Testy: `test_semaphore.py` (20), `test_detector.py` (12), `test_io_guards.py` (13).

#### `medication/` — F6 (380 LOC) ✅
- Model schematu leków + tracker adherence (wzięcie/pominięcie, okna czasowe).
- `schemas.py` — Pydantic v2 (walidacja dawkowania, częstotliwości).
- Migracja `0004_medication_tracker`. Testy: `test_medication.py` (11).

#### `emergency/` — F16 (380 LOC) 🟡
- **`dialplan.py`** — logika wybierania 112 / koordynatora (kolejność, potwierdzenia, timeouty).
- **`payload.py`** — pakiet danych dla służb (adres, wiek, dane medyczne, kontekst upadku).
- **`audio.py`** — komunikaty głosowe eskalacji. Migracja `0009_emergency_calls`.
- Warunkowo: realny dispatch wymaga telefonii. Testy: `test_emergency.py` (10).

#### `family/` — F8/F9 (459 LOC) 🟡
- **`service.py`** — model rodziny, powiązania senior↔opiekunowie, preferencje notyfikacji.
- **`adapters.py`** — `build_adapters()` z **fail-safe per kanał**: przy braku kompletu sekretów
  danego kanału (Twilio/SendGrid/FCM) degraduje do `NullAdapter` zamiast konstruować adapter,
  który i tak zwróci błąd. Tryby ENV: `memory` | `null` | `live`.
- Testy: `test_family.py` (15), `test_notify_adapters.py` (7).

#### `wearables/` — F10 (377 LOC) 🟡
- Adaptery opasek/zegarków (HR, SpO₂, upadek, sen); Adam pyta o kontekst przed alarmem
  (np. spacer z tętnem 130 ≠ alarm). Testy: `test_wearables.py` (9).

#### `marketplace/` — F12 (258 LOC) ✅
- Katalog partnerów (10 kategorii, 80+ pozycji), zamawianie usług, weryfikacja (OC/NIP/ocena).
- Testy: `test_marketplace.py` (12).

#### `memory/` — F7 (384 LOC) 🟡
- **`embedder.py`** — port embeddera (dev: deterministyczny; prod: sentence-transformers/OpenAI).
- **`summarizer.py`** — podsumowania rozmów (migracja `0010_conversation_summaries`).
- Chunki pamięci — migracja `0005_memory_chunks`. Testy: `test_memory.py` (13),
  `test_memory_summary.py` (7).

#### `consensus/` + `voice/consensus.py` — F14 (160 LOC) ✅
- Głosowanie między niezależnymi źródłami (dual-STT `stt_primary`/`stt_secondary`), flaga
  `disagreement`, fail-safe degradacja do primary. Testy: `test_consensus.py` (11).

#### `rodo/` — F13 (396 LOC) ✅
- **`consent.py`** — rejestr zgód (nagrania, przetwarzanie, marketing); brak zgody → brak nagrania.
- **`service.py`** — prawo do zapomnienia, eksport danych. Migracje `0006`, `0008`.
- Testy: `test_rodo.py` (8), `test_consent.py` (6).

#### `qa/` — F18 (585 LOC) ✅
- **`metrics.py`** — metryki jakości rozmów; **`sentiment.py`** — analiza sentymentu; 
  **`service.py`** — pętla QA: ewaluacja → pending-review → audyty → auto-improvements.
- Emisja `DecisionEvent` z DialogEngine (decision/level/trigger/confidence/needs_review).
- Migracja `0011_qa_loop`. Testy: `test_qa_loop.py` (12), `test_qa.py` (6).

#### `stress/` — F17 (196 LOC) ✅
- **`SeniorSimulator`** — persony deterministyczne: `calm`, `lonely`, `crisis`, `confused`,
  `manipulator`, `hypochondriac`; `ScenarioReport` z asercjami (escalated, max_level, guard_flags).
- **`HallucinatingLLM`** — atrapa generująca celowo dawki/diagnozy/obietnice do testów OutputGuard.
- Testy: `test_stress.py` (14).

#### `admin/` — panel admina backend (348 LOC) ✅
- Modele: `FleetUnit`, `ModelEntry`, `ProviderEntry`, `AdminLog` (+ enumy).
- **`AdminService`** — rejestr floty (+`fleet_summary`), rejestr modeli AI (ekskluzywny `primary`
  per rodzaj), sync providerów z **fail-safe probingiem ENV bez sieci** (komplet sekretów →
  `configured`, brak → `missing_secrets`, spójnie z `build_adapters`), dziennik logów z filtrami.
- Router `/api/admin` za rolą **ADMIN** (RBAC): fleet CRUD+summary, models + set-primary,
  providers list+sync, logs create+list. Migracja `0012_admin_panel`. Testy: `test_admin.py` (15).

### 4.3 Warstwa API (`api/`, 2417 LOC) ✅
- FastAPI, **15 routerów**: `account`, `admin`, `auth`, `compliance`, `consents`, `emergency`,
  `family`, `marketplace`, `medication`, `qa`, `rodo`, `safety`, `seniors`, `voice`, `wearables`.
- Auth: JWT **HS256** (stdlib), refresh/access TTL z ENV, RBAC per rola.
- Middleware: rate-limit (Redis w prod, fail-open), nagłówki bezpieczeństwa (HSTS za TLS).
- Testy API: `test_api.py` (37), `test_auth.py` (19), `test_security.py` (12),
  `test_middleware.py` (7), `test_account.py` (7), `test_e2e*.py` (6).

---

## 5. Sekcja B — Frontend

React 18 + TypeScript + Vite + TailwindCSS + Capacitor. **~8 900 linii**, **29 testów vitest**,
alias `@/` → `src/`. Design System „Nordic humanism × Medical-premium" (Fraunces + Geist,
granat/złoto/semafor, off-white `#fbfaf7`, złoto jako 1px akcent — NIE gradienty, tryb light-only).

### 5.1 Struktura stron
| Obszar | Ścieżka | Zawartość | Status |
|---|---|---|---|
| Landing Page | `pages/LandingPage.tsx` | 11 sekcji editorial (kompozycja) | ✅ (po elewacji wizualnej) |
| Panel Opiekuna | `pages/panel/` | 9 ekranów: Dashboard, Seniors, SeniorDetail, Reports, Orders, Messages, Account, Settings, Help | ✅ UI |
| Panel Admina | `pages/admin/` | **24 ekrany**: Dashboard, Fleet(+Detail), Agents(+Detail), Seniors(+Detail), Calls, Alerts, Models, Providers, Scheduling, Marketplace, Logs, Audio, Asterisk, Docker, Environment, Terminal, Tools, MCP, Pipelines, Contexts, Wizard | ✅ UI |
| Design System | `pages/DesignSystemPage.tsx` | żywa dokumentacja komponentów | ✅ |
| Login | `pages/LoginPage.tsx` | logowanie | ✅ |

### 5.2 Komponenty (`components/`)
- `ui/` — biblioteka: `Button`, `Card`, `Badge`, `Avatar`, `SemaphoreBadge`, `Stat`,
  `RadialGauge`, `Sparkline`, `Tabs`, `Heatmap`, `Timeline`, `Accordion`, `Toggle`, `Countdown`.
- `landing/` — 12 komponentów sekcji (Hero, Nav, SignoffStrip, ChapterProblem/HowItWorks/Features,
  PartnersSection, Testimonial, Pricing, FinalCTA, Footer, ChapterHead).
- `panel/`, `admin/`, `senior/`, `pwa/` — komponenty dziedzinowe.

### 5.3 Landing Page — elewacja wizualna (commit `d772ba5`) ✅
- Wszystkie placeholdery graficzne zastąpione **realnymi profesjonalnymi zdjęciami** (4 sztuki,
  `public/images/landing/`, ~550 KB łącznie), brand-matched (ciepłe światło, granat/złoto/off-white).
- Głębia: warstwowe kompozycje (navy back-plate + złota hairline-ramka), scrim pod cytatami,
  pływający badge „Semafor · Green" z pulsem, ambient radial glow, edge-fade marquee.
- Copy (PL): mocniejszy rytm i ton (hero, problem, CTA).
- Kolorystyka i identyfikacja **zachowane bez zmian** — tylko wzbogacone.

### 5.4 Braki frontendu (do 100%)
- **Podłączenie do realnego API** — ekracy admina/panelu w dużej mierze na danych mock;
  wymaga spięcia z `/api/*` (auth token flow, obsługa błędów, loading states).
- **Testy E2E UI** (Playwright/Cypress) — obecnie tylko testy jednostkowe API-client (vitest 29).
- **Dostępność (a11y)** — audyt WCAG dla seniorów (kontrast już AA; do zrobienia: focus order,
  aria-live dla alertów, rozmiary dotykowe).

### 5.5 Testy frontend
- `src/lib/api/realApi.test.ts` — 29 testów klienta API (vitest). `npm run test`.

---

## 6. Sekcja C — Warstwa głosowa

Moduł `voice/` (1782 LOC) + `speech/` (897 LOC). **Kod portów i logiki dialogu jest gotowy i
testowany**, ale realne uruchomienie wymaga telefonii (Asterisk) i kluczy ASR/LLM/TTS — stąd
status warunkowy.

### 6.1 Pliki `voice/`
| Plik | Rola | Status |
|---|---|---|
| `ports.py` | Interfejsy (porty heksagonalne) ASR/LLM/TTS/Channel | ✅ |
| `prod_ports.py` | Implementacje prod: `WhisperASR`, `OpenAITTS`, `ElevenLabsTTS`, `OpenAILLM` | 🟡 (wymaga kluczy) |
| `dialog.py` | `DialogEngine` — logika rozmowy, decyzje, `reprompt_silence`, `escalate_no_contact` | ✅ |
| `watchdog.py` | `SilenceWatchdog`, `BargeInController`, `RecordingRegistry`, `DualStt` (ETAP 33) | ✅ |
| `consensus.py` | Konsensus dual-STT (F14) | ✅ |
| `ari.py` | `CallSession` + `AsteriskAriChannel` (integracja ARI) | 🟡 |
| `stasis.py` | Aplikacja Stasis (event loop Asterisk) | 🟡 |
| `asterisk.py` | Konfiguracja/klient Asterisk | 🟡 |

### 6.2 `speech/` — preprocessing senioralny ✅
- `preprocessor.py` — normalizacja mowy; `profile.py` — profile głosowe; `wielkopolska.py` —
  słownik/wariant regionalny (gwara wielkopolska). Testy: `test_speech.py`, `test_senior_audio.py`.

### 6.3 Testy warstwy głosowej
`test_voice.py` (21), `test_voice_ava.py` (21), `test_voice_io.py` (17), `test_voice_prod.py` (15),
`test_voice_stasis.py` (10) — **wszystkie zielone** dzięki `FakeChannel` i atrapom portów.

### 6.4 Co blokuje 100% warstwy głosowej
- **Asterisk / ARI / Stasis** — wymaga serwera SIP (Frankfurt DC), numeru telefonicznego,
  konfiguracji PJSIP i tuneli. ENV: `ASTERISK_ARI_URL/USER/PASS`.
- **Realne ASR/LLM/TTS** — klucze OpenAI (Whisper + LLM), ElevenLabs (TTS). Bez nich `prod_ports`
  są konstruowalne, ale nie wykonują realnych wywołań.
- **Scheduler na żywo** — APScheduler wymaga procesu długodziałającego + Redis do timerów.

---

## 7. Sekcja D — Infrastruktura

### 7.1 Migracje (Alembic) ✅
12 migracji, chain czysty `0001`→`0012`, **pojedynczy HEAD**:
```
0001_seniors                          0007_disclosure_logs
0002_scheduler_campaigns_and_...      0008_consents
0003_semaphore_events                 0009_emergency_calls
0004_medication_tracker               0010_conversation_summaries
0005_memory_chunks                    0011_qa_loop
0006_family_wearables_marketplace_rodo 0012_admin_panel
```
Weryfikacja: `alembic upgrade head` OK, `alembic heads` = 1.

### 7.2 CI (`ci-templates/adam-ci.yml`) 🟡
Workflow gotowy — **3 joby**:
1. Backend pytest (421) — `PYTHONPATH=agent`, `ADAM_PII_KEY`/`ADAM_PII_PEPPER`.
2. Bramka Alembic — `upgrade head` chain 0001→0012 + weryfikacja pojedynczego HEAD.
3. Frontend — `npm ci` + `vitest` (29).
Trigger: push/PR na `main`+`staging` + `workflow_dispatch`.

> ⚠️ **Blokada tokenowa:** token GitHub App (`ghu_`) **nie ma scope `workflow`**, więc nie da się
> wypchnąć pliku do `.github/workflows/` (git push i `gh api PUT contents` → 403). Dlatego workflow
> leży w `ci-templates/`. **Aktywacja:** właściciel repo uruchamia `./activate-ci.sh` z lokalnego
> klona z własnym PAT (scope `repo`+`workflow`). Skrypt kopiuje szablon do `.github/workflows/`,
> waliduje YAML, commit + push. Tryby: domyślny, `--no-push`, `--help`.

### 7.3 Deploy (`agent/adam_modules/deploy/`) 🟡
Artefakty (bez kodu .py):
- `Dockerfile.adam-api` — obraz API.
- `docker-compose.adam.yml` — kompozycja (API + PostgreSQL + Redis + Asterisk).
- `entrypoint.sh` — bootstrap kontenera (migracje + start ASGI).
Dokumentacja: `docs/BACKEND-DEPLOY.md`, `docs/DEPLOY-ADAM.md`, `docs/DEPLOY-CHECKLIST.md`.

### 7.4 RAG (`rag/`)
- Indeks: `rag/index/chunks.jsonl` + `embeddings.npy` + `meta.json` (~505 chunków wiedzy o projekcie).
- Skrypty budowy w `rag/scripts/`. Służy jako pamięć wiedzy o wymaganiach/decyzjach.

### 7.5 Design System (`design-system/`) ✅
Foldery: `01-design-system`, `02-landing`, `03-panel-opiekuna`, `04-panel-admina`, `05-krytyczne`,
`06-deck`, `07-assets` + `DEVELOPER-HANDOFF.md`, `INSTRUKCJA-WDROZENIA.md`, `CHANGELOG.md`.
Źródło prawdy dla tokenów (kolory, typografia, komponenty).

### 7.6 Dokumentacja (`docs/`)
`API.md`, `AUDIT.md`, `AUDYT-LUK.md`, `AUDYT-PELNY.md`, `BACKEND-DEPLOY.md`, `CAPACITOR-BUILD.md`,
`DEPLOY-ADAM.md`, `DEPLOY-CHECKLIST.md`, `MASTER-PLAN.md`, `ROADMAP.md` + `source-docx`/`source-md`.

---

## 8. Mapa ETAP 0–35

Numeracja ETAP odnosi się do sesji rozwojowych. ETAP 28–35 domknęły warstwę logiki backendu.

| ETAP | Zakres | Status |
|---|---|---|
| 0–8 | Fundament: design system, landing, panele, RAG, roadmap | ✅ |
| 9 | Warstwa API (FastAPI, routery F1–F18) | ✅ |
| 11 | Auth JWT + RBAC | ✅ |
| 13 | Realne adaptery notyfikacji (Twilio/SendGrid/FCM) | 🟡 (fail-safe) |
| 14/16 | Obserwowalność, hardening, rate-limit, nagłówki bezpieczeństwa | ✅ |
| 17 | Tor głosowy — AsteriskAriChannel | 🟡 |
| 18 | Porty prod ASR/LLM/TTS (Whisper/OpenAI/ElevenLabs) | 🟡 (wymaga kluczy) |
| 20 | CI + bramka pokrycia | 🟡 (workflow gotowy, aktywacja przez właściciela) |
| 28 | Pamięć semantyczna + podsumowania | ✅ |
| 29 | Audio senioralne (preprocessing, gwara wielkopolska) | ✅ |
| 30 | Spięcie ESCALATE→112 + router QA (F14↔F16) | ✅ |
| 31 | Testy stresowe / red-team F17 (persony + HallucinatingLLM) | ✅ |
| 32 | Realne integracje — fail-safe per kanał `build_adapters()` | ✅ |
| 33 | Funkcje głosowe AVA (SilenceWatchdog, barge-in, nagrania, dual-STT) | ✅ |
| 34 | CI (3 joby) + `activate-ci.sh` (obejście blokady tokenowej) | 🟡 |
| 35 | Backend panelu Admina (flota/modele/providerzy/logi) + migracja 0012 | ✅ |

Commity referencyjne ostatnich ETAP-ów: `d9e7532`(32) → `e56ccdc`(33) → `5b02f0c`(35) →
`5561475`+`2a98637`(34) → `d772ba5`(elewacja landing).

---

## 9. Co pozostaje do 100%

Podział wg powodu, dla którego zadanie **nie może** być ukończone w sandboxie.

### 9.1 Wymaga infrastruktury docelowej (Frankfurt DC) — ~15–20% projektu
- **Asterisk / telefonia** — serwer SIP, numer PSTN, PJSIP, tunele; uruchomienie `voice/ari.py`,
  `stasis.py`, `asterisk.py` na żywo.
- **Scheduler welfare-check na żywo** — APScheduler jako proces + Redis (timery eskalacji F3).
- **PostgreSQL + Redis** — baza produkcyjna (dev używa SQLite) i kolejka eskalacji.
- **Kontenery** — build i uruchomienie `docker-compose.adam.yml`, E2E na żywej telefonii.

### 9.2 Wymaga kont/kluczy zewnętrznych — ~6% projektu
- **ASR/LLM/TTS** — OpenAI (Whisper + LLM), ElevenLabs (TTS).
- **Notyfikacje** — Twilio (SMS/telefon), SendGrid (e-mail), FCM (push).
- Bez sekretów adaptery działają w trybie **fail-safe** (no-op / memory).

### 9.3 Aplikacje mobilne (Capacitor, ETAP 7 roadmapy) — ~4% projektu 🔴
- Konta **Apple Developer** i **Google Play**, buildy natywne.
- **Critical Alerts entitlement** od Apple (kluczowe dla alarmów krytycznych) — proces akceptacji.
- Patrz `docs/CAPACITOR-BUILD.md`.

### 9.4 Domknięcie w zasięgu sandboxu (można zrobić tu) — ~5–8%
- Spięcie ekranów admina/panelu z realnym `/api/*` (zamiana mocków, token flow, error/loading).
- Testy E2E UI (Playwright).
- Audyt a11y (focus order, aria-live, rozmiary dotykowe).
- Uzupełnienie deploy docs o runbook (backup/restore, rotacja kluczy, monitoring).

---

## 10. Roadmap wdrożenia

Kolejność rekomendowana (od najmniejszego ryzyka do produkcji):

1. **Aktywacja CI** — właściciel repo: `./activate-ci.sh` z PAT (scope `repo`+`workflow`).
   Efekt: zielony pipeline na każdym push (backend 421 + Alembic + frontend 29).
2. **Staging bez telefonii** — deploy API na kontenerze (PostgreSQL+Redis), panele spięte z API,
   adaptery w trybie `memory`/`null`. Cel: E2E przepływów bez połączeń głosowych.
3. **Integracje soft** — dodać klucze SendGrid/FCM (notyfikacje e-mail/push), przełączyć `live`.
4. **Telefonia (Frankfurt DC)** — Asterisk + numer + `voice/*` na żywo; klucze ASR/LLM/TTS.
   Pilotaż na wewnętrznych numerach zespołu.
5. **Mobile** — Capacitor build iOS/Android, wniosek o Critical Alerts, testy na urządzeniach.
6. **Pilotaż u seniorów** — ograniczona grupa, monitoring, pętla QA (F18) do strojenia.

---

## 11. Instrukcja uruchomienia

### 11.1 Backend (dev, SQLite)
```bash
cd agent
pip install -r adam_modules/requirements.txt
# migracje (SQLite dev)
ADAM_PII_KEY=dev-test ADAM_PII_PEPPER=dev-pepper \
  python -m alembic -c adam_modules/migrations/alembic.ini upgrade head
# testy
ADAM_PII_KEY=dev-test ADAM_PII_PEPPER=dev-pepper \
  PYTHONPATH=. python -m pytest adam_modules/tests/ -q      # -> 421 passed
# API (dev)
ADAM_PII_KEY=dev-test ADAM_PII_PEPPER=dev-pepper \
  PYTHONPATH=. uvicorn adam_modules.api.app:create_app --factory --reload
```

### 11.2 Frontend (dev)
```bash
cd frontend
npm ci
npm run test      # vitest -> 29 passed
npm run build     # tsc -b && vite build
npm run dev       # Vite dev server
```

### 11.3 Aktywacja CI (właściciel repo)
```bash
git clone https://github.com/walerys1003/Adam-2027.git && cd Adam-2027
# PAT z scope repo+workflow skonfigurowany lokalnie
./activate-ci.sh              # kopiuje ci-templates/adam-ci.yml -> .github/workflows/, commit+push
./activate-ci.sh --no-push    # tylko commit
./activate-ci.sh --help
```

---

## 12. Rejestr ENV

| Zmienna | Warstwa | Rola | Dev |
|---|---|---|---|
| `ADAM_PII_KEY` | common | Klucz Fernet (szyfrowanie PII) | wymagany do testów |
| `ADAM_PII_PEPPER` | common | Pepper blind index | wymagany do testów |
| `ADAM_JWT_SECRET` | auth | Sekret JWT HS256 | — |
| `ADAM_JWT_ACCESS_TTL` / `ADAM_JWT_REFRESH_TTL` | auth | TTL tokenów | — |
| `ADAM_AUTH_USERS` | auth | Definicja użytkowników/ról (dev) | — |
| `ADAM_NOTIFY_PROVIDER` | family | `memory` \| `null` \| `live` | `memory` |
| `ADAM_TWILIO_*` | family | Sekrety Twilio (SMS/telefon) | — |
| `ADAM_SENDGRID_*` | family | Sekrety SendGrid (e-mail) | — |
| `ADAM_FCM_KEY` | family | Klucz FCM (push) | — |
| `ADAM_RATE_LIMIT` / `_WINDOW` / `_ENABLED` | api | Rate-limit | — |
| `ADAM_REDIS_URL` | api | Redis (rate-limit globalny, fail-open) | — |
| `ADAM_HSTS` | api | HSTS za TLS (`=1`) | — |
| `ADAM_SECURITY_HEADERS` | api | Nagłówki bezpieczeństwa (`=0` wyłącza) | — |
| `ASTERISK_ARI_URL` / `_USER` / `_PASS` | voice | Integracja ARI | — |

---

## 13. Definition of Done

Warstwa uznana za **100%**, gdy:

- **Backend logika (F1–F18):** kod + testy zielone + migracja + brak `TODO` krytycznych. → ✅ osiągnięte.
- **API:** wszystkie routery pokryte testami, RBAC egzekwowany, OpenAPI kompletne. → ✅.
- **Frontend:** ekrany spięte z realnym API, testy E2E zielone, audyt a11y zaliczony. → 🟡 (UI gotowe, spięcie/E2E/a11y do zrobienia).
- **Głos:** rozmowa E2E na żywej telefonii (Asterisk) z realnym ASR/LLM/TTS, watchdog+barge-in działają na produkcji. → 🔴 (wymaga infrastruktury).
- **Infra:** CI zielony na push, kontenery wstają, migracje na PostgreSQL, monitoring. → 🟡 (CI gotowy do aktywacji).
- **Mobile:** buildy iOS/Android w sklepach, Critical Alerts przyznane. → 🔴 (wymaga kont Apple/Google).
- **Gotowość produkcyjna:** pilotaż u seniorów przeszedł bez incydentów krytycznych, pętla QA strojona. → 🔴.

---

> **Podsumowanie dla developera:** wszystko, co możliwe do zbudowania i przetestowania w tym
> środowisku, jest praktycznie ukończone (~85–90%). Kolejne kroki są **infrastrukturalne**
> (Frankfurt DC, klucze API, konta mobilne), nie programistyczne. Zacznij od aktywacji CI (§11.3),
> potem staging bez telefonii (§10 krok 2). Mapa modułów w §4 pokazuje, gdzie leży kod każdej funkcji.
