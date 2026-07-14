# Adam API — warstwa REST (ETAP 9)

Warstwa `adam_modules/api` (FastAPI) wystawia funkcje backendu F1–F18 przez
REST/JSON, tak by frontend (panel opiekuna / admina) mógł docelowo połączyć się
z prawdziwym backendem we **Frankfurt DC** zamiast `mockApi.ts`.

## Uruchomienie

```bash
cd agent
pip install -r adam_modules/requirements.txt

# dev (autoreload)
ADAM_PII_KEY=dev ADAM_PII_PEPPER=dev \
  uvicorn adam_modules.api.app:app --reload --port 8787

# produkcja (Frankfurt DC) — wiele workerów
ADAM_DATABASE_URL="postgresql+psycopg://user:pass@host/adam" \
ADAM_PII_KEY="$PII_KEY" ADAM_PII_PEPPER="$PII_PEPPER" \
ADAM_API_KEY="$API_KEY" ADAM_CORS_ORIGINS="https://panel.adam.silvertech.pl" \
  gunicorn adam_modules.api.app:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8787
```

- Dokumentacja interaktywna: `GET /docs` (Swagger UI), `GET /openapi.json`.
- Health-check: `GET /health`.

## Zmienne środowiskowe

| Zmienna | Opis | Domyślnie |
|---------|------|-----------|
| `ADAM_DATABASE_URL` | URL bazy (PG w produkcji) | `sqlite:///:memory:` |
| `ADAM_PII_KEY` | Klucz szyfrowania PII (Fernet) | dev-insecure |
| `ADAM_PII_PEPPER` | Pieprz do blind index | `adam-pepper` |
| `ADAM_API_KEY` | Klucz API (nagłówek `X-API-Key`); pusty = otwarte (dev) | — |
| `ADAM_CORS_ORIGINS` | Dozwolone originy CORS (CSV) | `localhost:3000,localhost:5173` |
| `ADAM_JWT_SECRET` | Sekret podpisu JWT HS256 (**wymagany w prod**) | dev-insecure |
| `ADAM_JWT_ACCESS_TTL` | Ważność access-tokenu (s) | `900` (15 min) |
| `ADAM_JWT_REFRESH_TTL` | Ważność refresh-tokenu (s) | `1209600` (14 dni) |
| `ADAM_AUTH_USERS` | Użytkownicy dev: `email:hasło:rola[:sid1\|sid2],…` | demo (3 role) |
| `ADAM_NOTIFY_PROVIDER` | Adaptery notyfikacji: `memory` / `null` / `live` | `memory` |
| `ADAM_TWILIO_SID/TOKEN/FROM` | SMS (provider `live`) | — |
| `ADAM_SENDGRID_KEY/FROM` | E-mail (provider `live`) | — |
| `ADAM_FCM_KEY` | Push FCM (provider `live`) | — |
| `ADAM_RATE_LIMIT` | Pojemność rate-limit (żądań/okno) | `120` |
| `ADAM_RATE_WINDOW` | Okno rate-limit (s) | `60` |
| `ADAM_RATE_ENABLED` | `0` wyłącza rate-limit | `1` |
| `ADAM_LOG_LEVEL` | Poziom logów strukturalnych | `INFO` |

> Uwaga SQLite: dla `:memory:` API używa `StaticPool` (współdzielone połączenie),
> bo każde żądanie otwiera nową sesję. Produkcja to PostgreSQL — bez tego zastrzeżenia.

## Mapa endpointów (41)

### System
- `GET /health`, `GET /`, `GET /docs`, `GET /openapi.json`, `GET /metrics`

### Auth (ETAP 11) `/api/auth`
| Metoda | Ścieżka | Opis |
|--------|---------|------|
| POST | `/api/auth/login` | email+hasło → para JWT (access/refresh) + rola |
| POST | `/api/auth/refresh` | refresh-token → nowa para JWT |
| GET | `/api/auth/me` | profil zalogowanego (z access-tokenu; `Bearer`) |

### F1 — Seniorzy `/api/seniors`
| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET | `/api/seniors` | lista + paginacja (`active`, `district`, `limit`, `offset`) |
| POST | `/api/seniors` | utwórz (walidacja PESEL/telefon → 422) |
| GET | `/api/seniors/{id}` | szczegóły (PII maskowane) |
| GET | `/api/seniors/by-external/{external_id}` | po external_id |
| PATCH | `/api/seniors/{id}` | aktualizacja |
| DELETE | `/api/seniors/{id}` | soft-delete (dezaktywacja) |

### F3/F4/F8 — Bezpieczeństwo `/api/safety`
| POST | `/api/safety/analyze` | detekcja (tekst+vitals) → klasyfikacja + guardrails + plan eskalacji; opcjonalnie `apply_to_senior_id` |
| POST | `/api/safety/seniors/{id}/resolve` | jawne rozwiązanie (semafor → zielony) |
| GET | `/api/safety/seniors/{id}/history` | historia zdarzeń semafora |

### F6 — Leki `/api/seniors/{id}/medications`
| GET | `…/medications` | lista leków |
| POST | `…/medications` | dodaj lek + harmonogram |
| GET | `…/medications/adherence?days=30` | raport przyjmowania |

### F10 — Wearables `/api/seniors/{id}/wearables`
| GET/POST | `…/devices` | urządzenia (Xiaomi/Apple/Garmin/Fitbit) |
| POST | `…/readings` | ingest pomiaru (audyt SHA-256 + breach) |
| GET | `…/latest/{vital_type}` | najnowszy pomiar |
| GET | `…/breaches` | przekroczenia progów |

### F9 — Rodzina/notyfikacje `/api/seniors/{id}/family`
| GET/POST | `…/members` | opiekunowie + role |
| POST | `…/dispatch` | fan-out wg poziomu (digest/immediate/bypass-DND) |
| GET | `…/feed` | strumień powiadomień |
| GET | `…/events` | **SSE** (`text/event-stream`) dla dashboardu |

### F11 — Marketplace `/api/marketplace`
| GET | `/api/marketplace/services` | katalog (filtr kategorii) |
| POST | `/api/marketplace/orders` | zamówienie (okno anulowania 30 min) |
| GET | `/api/marketplace/seniors/{id}/orders` | zamówienia seniora |
| POST | `/api/marketplace/orders/{id}/cancel` | anulowanie (poza oknem → 422) |

### F12 — RODO `/api/seniors/{id}/rodo`
| GET | `…/rodo/export` | eksport danych (art. 15/20) |
| POST | `…/rodo/soft-delete` | dezaktywacja |
| POST | `…/rodo/erase` | prawo do zapomnienia (art. 17) |
| GET | `…/rodo/audit` | rejestr czynności (art. 30) |

### F13/F14/F15/F16/F17 — Compliance `/api/compliance`
| GET | `…/system-register` | rejestr systemu AI (AI Act art. 11) |
| POST | `…/disclosures` | log ujawnienia natury AI (art. 50) |
| GET | `…/disclosures/{ref}/asserted` | czy rozmowa miała ujawnienie |
| POST | `…/qa/evaluate` | QA rozmowy (score 0-100 + flagi) |
| POST | `…/consensus/decide` | multi-model consensus (fail-safe) |
| POST | `…/emergency/{id}/payload?reason=…` | payload 112 |
| POST | `…/speech/profile` | profil mowy senioralnej (F14) |

### Voice (ETAP 12) `/api/voice`
| Metoda | Ścieżka | Opis |
|--------|---------|------|
| POST | `/api/voice/simulate-call` | symulacja pełnej rozmowy tura-po-turze (FakeChannel + RuleLLM): ujawnienie AI → Q&A → ew. eskalacja; zwraca transkrypcję, poziom semafora, `rate_wpm`/`volume_db` profilu mowy |

> **Warstwa głosowa (F5+F14+F3):** `DialogEngine` to czysta maszyna stanów
> (`INIT → DISCLOSED → ACTIVE → ESCALATING → CLOSED`), integrująca System Prompt
> (F5) + obowiązkowe ujawnienie natury AI (AI Act art. 50), profil mowy
> senioralnej (F14 → parametry TTS) oraz detekcję kryzysu (F3) na każdej
> wypowiedzi seniora. Poziom PURPLE/RED przerywa Q&A i przechodzi do eskalacji.
> Porty ASR/LLM/TTS oraz kanał `AriChannel` to `Protocol` — w dev/test używane
> są implementacje bez sieci (EchoASR/RuleLLM/TextTTS/FakeChannel), produkcyjnie
> (Frankfurt DC) podmieniane na realne (Whisper/GPT/ElevenLabs + Asterisk ARI).
> `POST /simulate-call` pozwala panelowi/testom przejść cały tor bez telefonii.

> **Konsensus kryzysowy (ETAP 17, F16 w torze głosowym):** dla każdej wypowiedzi
> `DialogEngine` łączy dwa niezależne głosy — detektor regułowy (F3, deterministyczny,
> audytowalny) + klasyfikator LLM (`LLMPort.classify`) — przez `ConsensusEngine`.
> Reguła fail-safe: przy rozbieżności wybierany jest **wyższy** poziom i ustawiane
> `needs_review`. LLM może *podnieść* czujność (złapać niuans, którego reguła nie ma
> dosłownie w słowniku), ale nie *obniży* twardego sygnału detektora. Awaria LLM →
> zostaje sam detektor (nadal fail-safe). Wyłącznik: `DialogEngine(..., use_consensus=False)`.
> Adapter produkcyjny `AsteriskAriChannel` (httpx, fail-safe, no-op bez `ASTERISK_ARI_URL`)
> implementuje `AriChannel` przez Asterisk REST Interface.

## Bezpieczeństwo

- **PII maskowane** w odpowiedziach (`SeniorOut.from_model`): PESEL/telefon nigdy nie wracają jawnie.
- **Guardrails (F4)** walidują klasyfikację przed eskalacją — PURPLE wymaga twardego sygnału.
- **`X-API-Key`** wymagany, gdy ustawiono `ADAM_API_KEY` (produkcja).
- **CORS** zawężony do originów panelu.
- Błędy walidacji domenowej (zły PESEL/NIP, poza oknem anulowania) → `422`.

### Uwierzytelnianie i RBAC (ETAP 11)

- **JWT HS256** (stdlib, bez pyjwt): access (15 min) + refresh (14 dni), podpis `ADAM_JWT_SECRET`.
- **Hasła**: PBKDF2-HMAC-SHA256 (200k rund, sól per-hasło), porównanie w stałym czasie.
- **Role (hierarchia)**: `family < coordinator < admin`. Zależność `require_role(Role.X)` → `403`
  gdy rola za niska; `get_current_user` → `401` przy braku/wygaśnięciu tokenu.
- **Dostęp do seniora**: `family` widzi tylko przypisanych (`senior_ids` w tokenie),
  `coordinator`/`admin` — wszystkich (`CurrentUser.can_access_senior`).
- Błędy uwierzytelniania (złe hasło / token) → `401` (`TokenError`, spójny komunikat — brak enumeracji).
- Prod: `ADAM_JWT_SECRET` obowiązkowy; login można podmienić na OIDC (kontrakt `TokenOut` bez zmian).

### Powiadomienia rodzinne (ETAP 13)

- Adaptery za `Protocol` (`NotificationAdapter`), selekcja `build_adapters()` wg `ADAM_NOTIFY_PROVIDER`:
  `memory` (dev/test), `null` (cisza), `live` (Twilio SMS / SendGrid e-mail / FCM push — httpx).
- **Fail-safe**: kanał `live` bez sekretu zwraca `DeliveryResult(ok=False)` zamiast rzucać wyjątkiem.
- Kanał `call` = warstwa ARI/telefonia (poza tym pakietem) — Null/Memory.

### Obserwowalność i hardening (ETAP 14)

- **Request-ID** (`X-Request-ID`, propagowany z żądania lub generowany) + **czas odpowiedzi** (`X-Response-Time-ms`).
- **Log strukturalny** (`adam.api`): metoda, ścieżka, status, req_id, czas.
- **Rate-limit** token-bucket per-klient (`ADAM_RATE_LIMIT`/`WINDOW`) → `429` + `Retry-After`;
  `/health`, `/metrics`, `/` wyłączone.
- **`GET /metrics`** — ekspozycja w formacie Prometheus (liczniki wg metody/kodu, średnia latencja, odrzucenia rate-limit).

### Bezpieczeństwo i rate-limit rozproszony (ETAP 16)

- **Nagłówki bezpieczeństwa** (`SecurityHeadersMiddleware`, najbardziej zewnętrzny — także na 4xx/5xx):
  `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`,
  `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'; base-uri 'none'`, `Cache-Control: no-store`.
  `HSTS` włączany dopiero za TLS przez `ADAM_HSTS=1`; wyłącznik całości: `ADAM_SECURITY_HEADERS=0`.
- **Rate-limit z pluggable backendem**: domyślnie in-memory (per-worker); gdy ustawiono `ADAM_REDIS_URL` —
  globalny limit w Redis (fixed-window `INCR`/`EXPIRE`, współdzielony przez workery gunicorn).
- **Fail-open**: każdy błąd Redisa (brak połączenia/timeout) → żądanie dopuszczone + log ostrzeżenia.
  Dostępność > twardy limit; awaria cache nigdy nie blokuje ruchu.

| Zmienna | Opis | Domyślnie |
|---|---|---|
| `ADAM_REDIS_URL` | globalny rate-limit w Redis (pusty = in-memory) | — |
| `ADAM_HSTS` | `1` → dołącz `Strict-Transport-Security` (za TLS) | `0` |
| `ADAM_SECURITY_HEADERS` | `0` → wyłącz nagłówki bezpieczeństwa | `1` |

## Testy

```bash
cd agent
python3 -m pytest adam_modules/tests/test_api.py -q          # 23 testy API (F1–F18)
python3 -m pytest adam_modules/tests/test_auth.py -q         # 19 testów auth/RBAC (ETAP 11)
python3 -m pytest adam_modules/tests/test_notify_adapters.py -q  # 7 testów adapterów (ETAP 13)
python3 -m pytest adam_modules/tests/test_middleware.py -q   # 7 testów obserwowalności (ETAP 14)
python3 -m pytest adam_modules/tests/test_voice.py -q        # 19 testów warstwy głosowej (ETAP 12)
python3 -m pytest adam_modules/tests/test_security.py -q     # 12 testów bezpieczeństwa/rate-limit (ETAP 16)
python3 -m pytest adam_modules/tests/test_voice_prod.py -q   # 15 testów konsensusu + ARI (ETAP 17)
python3 -m pytest adam_modules/tests/ -q                     # 292 testów (F1–F18 + API + 11/12/13/14/16/17)
```

## Integracja z frontendem (ETAP 10)

Panel opiekuna (`frontend/`) konsumuje to API przez **adapter** (`src/lib/api/realApi.ts`),
który mapuje kontrakt FastAPI na typy domenowe frontendu (`Senior`, `SeniorDetail`, `Order`,
`MoodPoint`). Fasada `src/lib/api/client.ts` przełącza mock⇄live na podstawie `VITE_API_URL`.

### Przełącznik mock / live

| `VITE_API_URL` | Tryb | Zachowanie |
|---|---|---|
| puste | **mock** (`USE_MOCK=true`) | dane w pamięci (`mockApi.ts`) — dev bez backendu |
| ustawione | **live** | adapter `realApi` → prawdziwe endpointy FastAPI |

Konfiguracja: skopiuj `frontend/.env.example` → `frontend/.env.local`:

```
VITE_API_URL=http://localhost:8787   # bazowy URL backendu
VITE_API_KEY=                        # trafia do nagłówka X-API-Key (= ADAM_API_KEY)
```

### Mapowanie kontraktu (adapter)

| Frontend (domain) | Backend (FastAPI) | Uwagi |
|---|---|---|
| `getMySeniors()` | `GET /api/seniors?limit=200` | `{ items,total }` → `{ seniors,total }` |
| `getSenior(extId)` | `GET /api/seniors/by-external/{extId}` + `GET /api/seniors/{id}/medications/adherence?days=30` | `adherence30d` z F6; tolerancja 404 → 0 |
| `getMood(extId)` | `GET /api/seniors/by-external/{extId}` | backend nie trzyma serii nastroju — trend 7-dniowy wyliczany deterministycznie z semafora |
| `listOrders()` | `GET /api/seniors?limit=200` + `GET /api/marketplace/seniors/{id}/orders` | agregacja po seniorach |
| `cancelOrder(id)` | `POST /api/marketplace/orders/{id}/cancel` | ValueError (poza oknem) → 422 |
| `createOrder(...)` | `POST /api/marketplace/orders` | `{ senior_id, service_id }` |

Backend jest **węższy** niż model frontendu (brak per-punkt `mood`/`adherence`), więc adapter
**wzbogaca**: `mood` z heurystyki semafora (green 0.82 / yellow 0.58 / red 0.34 / purple 0.18),
`adherence30d` z `/medications/adherence`, deterministyczny trend nastroju 7-dniowy.

### Smoke test (live)

```bash
# 1. backend
cd agent
ADAM_DATABASE_URL="sqlite:////tmp/adam_live.db" \
  ADAM_PII_KEY=dev ADAM_PII_PEPPER=dev \
  uvicorn adam_modules.api.app:app --port 8787

# 2. frontend — testy adaptera + build
cd frontend
npx vitest run src/lib/api/realApi.test.ts   # 17 testów adaptera
npm run build                                 # tsc -b && vite build (weryfikacja typów)
```
