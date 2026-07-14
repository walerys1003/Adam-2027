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

> Uwaga SQLite: dla `:memory:` API używa `StaticPool` (współdzielone połączenie),
> bo każde żądanie otwiera nową sesję. Produkcja to PostgreSQL — bez tego zastrzeżenia.

## Mapa endpointów (33)

### System
- `GET /health`, `GET /`, `GET /docs`, `GET /openapi.json`

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

## Bezpieczeństwo

- **PII maskowane** w odpowiedziach (`SeniorOut.from_model`): PESEL/telefon nigdy nie wracają jawnie.
- **Guardrails (F4)** walidują klasyfikację przed eskalacją — PURPLE wymaga twardego sygnału.
- **`X-API-Key`** wymagany, gdy ustawiono `ADAM_API_KEY` (produkcja).
- **CORS** zawężony do originów panelu.
- Błędy walidacji domenowej (zły PESEL/NIP, poza oknem anulowania) → `422`.

## Testy

```bash
cd agent
python3 -m pytest adam_modules/tests/test_api.py -q   # 23 testy API
python3 -m pytest adam_modules/tests/ -q               # 177 testów (F1–F18 + API)
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
