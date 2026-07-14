# ADAM-2027 — PEŁNY AUDYT FUNKCJONALNY

> **Projekt:** ADAM-2027 (AVA v7.3.2 → asystent głosowy „Adam" dla seniorów)
> **Wykonawca:** SilverTech Poznań
> **Data audytu:** 2026-07-14
> **Commit audytowany:** `27db989` (ETAP 16+17), branch `main`
> **Metoda:** inwentaryzacja rzeczywistego repozytorium (nie z pamięci) — każda liczba zweryfikowana komendą w repo.

---

## 0. STRESZCZENIE ZARZĄDCZE (TL;DR)

| Warstwa | Stan kodu | Wdrożone (działa na infra) | Gotowość do deployu |
|---|---|---|---|
| **Backend (logika F1–F18)** | ✅ Kompletny | ❌ Nie uruchomiony | **~90%** |
| **API (FastAPI, 41 endpointów)** | ✅ Kompletny | ❌ Nie uruchomiony | **~90%** |
| **Baza danych (18 modeli, 7 migracji)** | ✅ Kompletna (schemat) | ❌ Brak instancji PG | **~85%** |
| **Frontend (36 stron, 40 komponentów)** | ✅ Kompletny (UI) | 🟡 Tylko mock/podgląd | **~55%** (integracja) |
| **Integracje (Twilio/SendGrid/FCM/Asterisk)** | 🟡 Adaptery gotowe | ❌ Brak kluczy/infra | **~40%** |
| **Tor głosowy realny (ASR/TTS/LLM)** | ❌ Tylko dev-porty | ❌ | **~25%** |
| **CI/CD** | 🟡 Plik istnieje | ❌ Nieaktywny (zły path) | **~50%** |
| **iOS/Android (Capacitor)** | ✅ Kod gotowy | ❌ Brak buildu/publikacji | **~60%** |

### 🎯 OGÓLNA GOTOWOŚĆ DO DEPLOYU: **~70%**

**Co to znaczy:** cała logika biznesowa, model danych, API i UI **istnieją i są przetestowane** (256 testów backend). Brakuje przede wszystkim **elementów infrastrukturalnych i integracyjnych**, których nie da się wytworzyć w sandboxie:
1. uruchomionej infrastruktury (serwer Frankfurt DC, PostgreSQL, Redis, Asterisk),
2. realnych **credentiali** (klucze API dostawców),
3. **podpięcia frontendu do żywego backendu** (dziś część paneli działa na mockach),
4. realnego toru głosowego (ASR/TTS/LLM — ETAP 18).

---

## 1. WARSTWA BACKEND (`agent/adam_modules/`)

### 1.1. Inwentaryzacja (zweryfikowana)
- **21 modułów domenowych:** `api, auth, common, compliance, consensus, emergency, family, marketplace, medication, memory, migrations, qa, rodo, scheduler, semaphore, seniors, speech, voice, wearables, tests, deploy`
- **18 modeli ORM (SQLAlchemy):** Senior, Campaign, CallAttempt, SemaphoreEvent, Medication, MedicationSchedule, DoseLog, MemoryChunk, FamilyMember, Notification, WearableDevice, VitalReading, VitalThreshold, Partner, Service, Order, DataProcessingLog, DisclosureLog
- **26 plików testowych, 256 testów pytest** — ostatni przebieg: `256 passed`
- **Feature set F1–F18 kompletny w kodzie**

### 1.2. Opis funkcji (mapa F1–F18)
| Feature | Funkcja | Moduł |
|---|---|---|
| F1 | Profile seniorów + szyfrowanie PII | `seniors/` |
| F2 | Scheduler welfare-check (kampanie, próby połączeń) | `scheduler/` |
| F3 | Semafor bezpieczeństwa (detektor kryzysu) | `semaphore/` |
| F4/F5 | Guardrails + System Prompt Adama | `voice/`, `common/` |
| F6 | Medication tracker (leki, harmonogram, adherence) | `medication/` |
| F7 | Pamięć semantyczna rozmów | `memory/` |
| F8 | Crisis detection | `semaphore/`, `voice/` |
| F9 | Dashboard rodzinny + powiadomienia SMS/email | `family/` |
| F10 | Wearables (urządzenia, odczyty, progi vital) | `wearables/` |
| F11 | Marketplace usług | `marketplace/` |
| F12 | RODO (eksport/soft-delete/erase/audit) | `rodo/` |
| F13 | AI Act compliance (rejestr systemu, disclosure) | `compliance/` |
| F14 | Mowa senioralna (profil mowy) | `speech/` |
| F15 | QA evaluate | `qa/` |
| F16 | Konsensus decyzyjny (multi-głos) | `consensus/` |
| F17 | Emergency payload (112) | `emergency/` |
| F18 | Testy end-to-end | `tests/` |

### 1.3. Stan wdrożenia
- ✅ **Kod:** kompletny, przetestowany (256 testów zielone).
- ❌ **Runtime:** nieuruchomiony — brak działającej instancji na docelowym serwerze.
- ✅ **Artefakty deployu gotowe:** `Dockerfile.adam-api`, `docker-compose.adam.yml`, `entrypoint.sh`, `.env.adam.example`, `docs/DEPLOY-ADAM.md`.

### **Backend: ~90%** (brakuje tylko realnego uruchomienia na infra + tor głosowy = osobna warstwa)

---

## 2. WARSTWA API (FastAPI — 11 routerów, 41 endpointów)

### 2.1. Architektura
- `create_app()` factory, per-request session DI.
- **Stos middleware (od zewnątrz):** `SecurityHeaders → CORS → RequestContext → RateLimit → app`.
- Ochrona: **X-API-Key** (guard) + **JWT** (auth, ETAP 11).
- Rate-limit: pluggable backend — **in-memory** lub **Redis** (fixed-window, fail-open).

### 2.2. Pełna mapa endpointów (41)
| Router | Endpointy |
|---|---|
| **auth** (3) | `POST /login`, `POST /refresh`, `GET /me` |
| **seniors** (6) | `GET /`, `POST /`, `GET /{id}`, `GET /by-external/{ext}`, `PATCH /{id}`, `DELETE /{id}` |
| **safety** (3) | `POST /analyze`, `POST /seniors/{id}/resolve`, `GET /seniors/{id}/history` |
| **medication** (3) | `GET`, `POST`, `GET /adherence` |
| **family** (5) | `GET /members`, `POST /members`, `POST /dispatch`, `GET /feed`, `GET /events` |
| **wearables** (5) | `GET /devices`, `POST /devices`, `POST /readings`, `GET /latest/{type}`, `GET /breaches` |
| **marketplace** (4) | `GET /services`, `POST /orders`, `GET /seniors/{id}/orders`, `POST /orders/{id}/cancel` |
| **rodo** (4) | `GET /export`, `POST /soft-delete`, `POST /erase`, `GET /audit` |
| **compliance** (7) | `GET /system-register`, `POST /disclosures`, `GET /disclosures/{ref}/asserted`, `POST /qa/evaluate`, `POST /consensus/decide`, `POST /emergency/{id}/payload`, `POST /speech/profile` |
| **voice** (1) | `POST /simulate-call` |

### 2.3. Stan wdrożenia
- ✅ Wszystkie 41 endpointów zaimplementowane i objęte testami.
- ❌ Brak żywego adresu (deploy).
- 🟡 CORS trzeba skonfigurować pod docelową domenę frontendu.

### **API: ~90%**

---

## 3. WARSTWA BAZY DANYCH

### 3.1. Inwentaryzacja
- **18 modeli ORM** (jak wyżej).
- **7 migracji Alembic** (0001→0007):
  1. `0001_seniors`
  2. `0002_scheduler_campaigns_and_call_attempts`
  3. `0003_semaphore_events`
  4. `0004_medication_tracker`
  5. `0005_memory_chunks`
  6. `0006_family_wearables_marketplace_rodo`
  7. `0007_disclosure_logs`
- **Dev:** SQLite (lokalnie). **Prod:** PostgreSQL (przez `ADAM_DATABASE_URL`).
- Migracje testowane w CI (upgrade head → verify 0007 → downgrade base → upgrade).

### 3.2. Stan wdrożenia
- ✅ Schemat kompletny, migracje odwracalne.
- ❌ Brak uruchomionej instancji PostgreSQL na produkcji.
- ⚠️ Wymaga: utworzenia bazy + uruchomienia `alembic upgrade head`.

### **Baza danych: ~85%** (schemat gotowy; brak instancji + migracji na prod)

---

## 4. WARSTWA FRONTEND (`frontend/`)

### 4.1. Inwentaryzacja
- **36 stron (.tsx):** 3 top (DesignSystem/Landing/Login) + panel opiekuna + 24 admin.
- **40 komponentów.**
- Stack: React + TypeScript + Vite + Capacitor (iOS/Android). Ostatni build: `✓ built in 11.84s`.
- Fasada API: `client.ts` → `USE_MOCK = !import.meta.env.VITE_API_URL`.

### 4.2. ⚠️ KLUCZOWA LUKA INTEGRACYJNA (zweryfikowana w kodzie)
Frontend ma pełen UI, ale **żywe** podpięcie do backendu jest CZĘŚCIOWE. `realApi.ts` obsługuje na żywo tylko **5 ścieżek**:
- `GET /api/seniors?limit=200`
- `GET /api/seniors/by-external/{id}`
- `GET /api/seniors/{id}/medications/adherence?days=30`
- `GET /api/marketplace/seniors/{id}/orders`
- `POST /api/marketplace/orders/{id}/cancel`

**Działa na żywo:** lista/szczegóły seniorów, nastrój (mood), zamówienia.
**Nadal MOCK-only:** logowanie (`api.login` zawsze mock), wiadomości (Messages), konto (Account/faktury/sesje).

> 🔴 Komentarz w `client.ts` (*„backend nie ma jeszcze /auth"*) jest **NIEAKTUALNY** — backend `POST /api/auth/login` **istnieje** (ETAP 11). To potwierdza opóźnienie integracji frontu, nie brak API.

### 4.3. Stan wdrożenia
- ✅ UI kompletny, buduje się.
- 🟡 Deployowalny na Cloudflare Pages (statyk), ale bez pełnego podpięcia backendu.
- ❌ Auth + Messages + Account wymagają przepięcia z mock na `realApi`.

### **Frontend: ~55%** (UI 100%, integracja z żywym API ~40%)

---

## 5. WARSTWA INTEGRACJI

### 5.1. Zewnętrzne integracje (adaptery istnieją: `family/adapters.py`, `wearables/adapters.py`, `voice/asterisk.py`)
| Integracja | Cel | Stan kodu | Stan wdrożenia |
|---|---|---|---|
| **Twilio** (SMS) | powiadomienia rodziny | ✅ adapter | ❌ brak kluczy |
| **SendGrid** (email) | powiadomienia rodziny | ✅ adapter | ❌ brak kluczy |
| **FCM** (push) | powiadomienia mobilne | ✅ adapter | ❌ brak klucza |
| **Asterisk ARI** | telefonia (play/record/hangup) | 🟡 adapter REST, **bez pętli Stasis** | ❌ brak serwera |
| **Wearables** | odczyty vital | ✅ adapter | 🟡 zależnie od dostawcy |
| **Redis** | rate-limit rozproszony | ✅ backend fail-open | ❌ brak instancji |
| **Konsensus LLM** (F16) | głosowanie decyzyjne | ✅ RuleLLM (dev) | ❌ brak realnego LLM |

### 5.2. Tor głosowy realny (ASR/TTS/LLM)
Obecnie tylko **dev-porty**: `EchoASR`, `TextTTS`, `RuleLLM`. **Brak realnych adapterów** (Whisper/ElevenLabs/GPT) — to zaplanowany **ETAP 18**.

### **Integracje: ~40%** (kod adapterów gotów, brak kluczy + infra + realnego toru głosu)

---

## 6. CI/CD

- Plik `agent/.github/workflows/backend-ci.yml` **istnieje** (pytest + Alembic up/down).
- 🔴 **NIEAKTYWNY** — leży pod `agent/.github`, a nie w root `.github/workflows/`. Wg noty w pliku: *„aby aktywować CI... przenieś ten plik do `.github/workflows/backend-ci.yml` (wymaga uprawnienia `workflows`)."*
- Brak jeszcze: gate pokrycia + jawne dołączenie `test_security.py`/`test_voice_prod.py` (auto-łapane, ale bez bramki) — **ETAP 20**.

### **CI/CD: ~50%**

---

## 7. WYMAGANE CREDENTIALE I INFORMACJE (do podpięcia całości)

> Wszystkie jako **zmienne środowiskowe / sekrety** (nigdy w kodzie / froncie).

### 7.1. Infrastruktura (SilverTech / Frankfurt DC)
| Co | Zmienna | Kto dostarcza |
|---|---|---|
| PostgreSQL URL | `ADAM_DATABASE_URL` | SilverTech (DC) |
| Redis URL | `ADAM_REDIS_URL` | SilverTech (DC) |
| Serwer Asterisk | `ASTERISK_ARI_URL/USER/PASS` | SilverTech (telefonia) |

### 7.2. Sekrety bezpieczeństwa (wygenerować przed deployem)
| Co | Zmienna |
|---|---|
| Klucz API (guard) | `ADAM_API_KEY` |
| Sekret JWT | `ADAM_JWT_SECRET` (+ `ADAM_JWT_ACCESS_TTL`, `ADAM_JWT_REFRESH_TTL`) |
| Szyfrowanie PII | `ADAM_PII_KEY`, `ADAM_PII_PEPPER` |
| Użytkownicy auth | `ADAM_AUTH_USERS` |
| HSTS/nagłówki | `ADAM_HSTS`, `ADAM_SECURITY_HEADERS` |

### 7.3. Dostawcy zewnętrzni (konta + klucze)
| Dostawca | Zmienne | Potrzebne info |
|---|---|---|
| **Twilio** | `ADAM_TWILIO_SID`, `ADAM_TWILIO_TOKEN`, `ADAM_TWILIO_FROM` | konto + numer nadawczy |
| **SendGrid** | `ADAM_SENDGRID_KEY`, `ADAM_SENDGRID_FROM` | konto + zweryfikowany nadawca |
| **FCM** | `ADAM_FCM_KEY` | projekt Firebase |
| **Provider powiadomień** | `ADAM_NOTIFY_PROVIDER`, `ADAM_NOTIFY_TIMEOUT` | wybór dostawcy |

### 7.4. Dla ETAP 18 (realny głos) — dodatkowo
| Dostawca | Potrzebne |
|---|---|
| **OpenAI / Whisper** | klucz API (STT + opcjonalnie LLM) |
| **ElevenLabs / OpenAI TTS** | klucz API (synteza mowy) |

### 7.5. Frontend
| Co | Zmienna | Kto |
|---|---|---|
| Adres backendu | `VITE_API_URL` | po uruchomieniu backendu |
| Klucz API frontu | `VITE_API_KEY` | z `ADAM_API_KEY` |
| Cloudflare | token API Pages | do publikacji statyku |

### 7.6. Mobile (Capacitor)
- Konto **Apple Developer** ($99/rok) + macOS/Xcode → `.ipa`.
- Konto **Google Play** ($25) → `.aab`.
- Realizacja po stronie SilverTech.

---

## 8. PROCENTOWO — CO ZOSTAŁO DO DEPLOYU

### 8.1. Ogólna gotowość: **~70%**

### 8.2. Rozbicie brakujących ~30% (co dorobić)
| Zadanie | Waga | Typ |
|---|---|---|
| Uruchomienie infra (PG + Redis + Asterisk + serwer) | **~10%** | Infra (SilverTech) |
| Zebranie i wpięcie credentiali (7.1–7.4) | **~5%** | Konfiguracja |
| Przepięcie frontu na żywe API (auth + Messages + Account) | **~7%** | Kod (mogę zrobić) |
| ETAP 18 — realny tor głosowy (Whisper/ElevenLabs/LLM) | **~5%** | Kod (mogę zrobić) |
| ETAP 19 — pętla ARI Stasis + webhook startu połączenia | **~2%** | Kod (mogę zrobić) |
| ETAP 20 — aktywacja CI (przeniesienie pliku) + gate pokrycia | **~1%** | Kod + uprawnienie |

### 8.3. Podział wg odpowiedzialności
- **Mogę dorobić w kodzie (sandbox): ~15%** → integracja frontu + ETAP 18/19/20.
- **Wymaga SilverTech (infra + konta + klucze): ~15%** → serwer, PG, Redis, Asterisk, klucze dostawców, publikacja mobile.

---

## 9. PLAN OTWARTY (co jeszcze przed nami)

- **ETAP 18** — realne adaptery I/O w torze głosowym: `WhisperASR` (STT) + `ElevenLabsTTS`/`OpenAITTS` (httpx, fail-safe) jako produkcyjne podmiany portów; opcjonalnie realny `LLMPort` (GPT) z zachowaniem konsensusu.
- **ETAP 19** — warstwa zdarzeń ARI (Stasis WebSocket) osadzająca `CallSession` w pętli Asteriska + endpoint webhook startu połączenia.
- **ETAP 20** — CI: dołączenie `test_security.py`/`test_voice_prod.py` do workflow + gate pokrycia; ewentualnie load-test rate-limitu Redis.

---

## 10. REKOMENDACJA — KOLEJNOŚĆ DO DEPLOYU

1. **SilverTech:** postawić infra (PG + Redis + Asterisk) i przekazać credentiale (7.1–7.3).
2. **Ja:** przepiąć frontend na żywe API (usunąć mock z auth/Messages/Account) — domyka integrację.
3. **Ja:** ETAP 18 (realny głos) → ETAP 19 (ARI) → ETAP 20 (CI aktywne).
4. **Deploy:** backend (Docker, Frankfurt) + `alembic upgrade head`, frontend (Cloudflare Pages z `VITE_API_URL`).
5. **Mobile:** build `.ipa`/`.aab` po stronie SilverTech.

> **Wniosek:** projekt jest **gotowy w warstwie kodu (~90% backend/API, 100% UI)**. Do produkcyjnego deployu brakuje głównie **infrastruktury + credentiali (~15%)** oraz **domknięcia integracji i realnego głosu (~15%, w większości po mojej stronie)**.
