# Adam — Wdrożenie backendu (Frankfurt DC)

> Backend Adama (`agent/adam_modules/`) NIE działa na Cloudflare. To usługa
> Pythona (Asterisk ARI + PostgreSQL + Redis) hostowana w europejskim centrum
> danych (Frankfurt) ze względu na RODO i integrację telefoniczną. Frontend
> (panel, PWA) pozostaje na Cloudflare Pages i komunikuje się z backendem po REST/SSE.

## 1. Architektura produkcyjna

```
                    ┌─────────────────────────────────────────┐
   Senior ──tel──►  │  Asterisk PBX (SIP/PSTN)                 │
                    │     │ ARI (REST/WebSocket)                │
                    │     ▼                                     │
                    │  Adam Agent (Python, adam_modules)        │
                    │   F2 scheduler · F3 semafor · F8 detektor │
                    │   F16 consensus · F9 notyfikacje          │
                    │     │                    │                │
                    │     ▼                    ▼                │
                    │  PostgreSQL 16       Redis 7              │
                    │  (dane, audyt)       (timery eskalacji,   │
                    │                       kolejka powiadomień)│
                    └───────────────┬───────────────────────────┘
                                    │ REST + SSE
                          Cloudflare Pages (frontend/PWA)
                                    │
                          Rodzina / Koordynator
```

## 2. Wymagania środowiska

- Python 3.11+
- PostgreSQL 16 (dane produkcyjne — Frankfurt)
- Redis 7 (timery eskalacji F3.2, kolejka powiadomień F9)
- Asterisk 20+ z włączonym ARI
- Lokalizacja danych: UE (Frankfurt) — wymóg RODO

## 3. Zmienne środowiskowe

| Zmienna | Opis | Przykład |
|---|---|---|
| `ADAM_DATABASE_URL` | URL PostgreSQL (nadpisuje sqlalchemy.url) | `postgresql+psycopg://adam:***@db:5432/adam` |
| `ADAM_PII_KEY` | Klucz Fernet do szyfrowania PII (F1) | `<base64 32B>` |
| `ADAM_PII_PEPPER` | Pieprz do blind index | `<losowy sekret>` |
| `REDIS_URL` | URL Redis | `redis://redis:6379/0` |
| `ASTERISK_ARI_URL` | Endpoint ARI | `http://asterisk:8088/ari` |
| `ASTERISK_ARI_USER` / `ASTERISK_ARI_PASS` | Poświadczenia ARI | — |

> `ADAM_PII_KEY` i `ADAM_PII_PEPPER` MUSZĄ być stałe między wdrożeniami —
> ich zmiana uniemożliwi odszyfrowanie istniejących PII.

## 4. Migracje bazy

```bash
cd agent/adam_modules/migrations
export ADAM_DATABASE_URL="postgresql+psycopg://adam:***@db:5432/adam"
alembic upgrade head        # stosuje 0001 → 0007
alembic current             # powinno pokazać 0007 (head)
```

Łańcuch migracji:
- `0001` seniorzy (PII szyfrowane)
- `0002` scheduler (kampanie + próby połączeń)
- `0003` semaphore_events
- `0004` medication tracker
- `0005` memory_chunks (pamięć semantyczna)
- `0006` family / wearables / marketplace / rodo (9 tabel)
- `0007` disclosure_logs (AI Act)

## 5. Uruchomienie (docker-compose docelowy)

```yaml
# szkic — do uzupełnienia obrazami produkcyjnymi
services:
  db:
    image: postgres:16
    environment: { POSTGRES_DB: adam, POSTGRES_USER: adam, POSTGRES_PASSWORD: ${DB_PASS} }
    volumes: [ "pgdata:/var/lib/postgresql/data" ]
  redis:
    image: redis:7
  asterisk:
    image: andrius/asterisk:20        # obraz przykładowy
    ports: [ "5060:5060/udp", "8088:8088" ]
  adam-agent:
    build: ./agent
    environment:
      ADAM_DATABASE_URL: postgresql+psycopg://adam:${DB_PASS}@db:5432/adam
      REDIS_URL: redis://redis:6379/0
      ASTERISK_ARI_URL: http://asterisk:8088/ari
    depends_on: [ db, redis, asterisk ]
volumes: { pgdata: {} }
```

## 6. Adaptery produkcyjne (podmiana implementacji)

Moduły są napisane z pluggable adapterami — w dev działają offline, w produkcji
podmienia się je bez zmiany logiki:

| Funkcja | Interfejs (dev) | Produkcja |
|---|---|---|
| F7 pamięć | `HashingEmbedder` | `sentence-transformers` lub OpenAI embeddings |
| F9 SMS/email | `MemoryAdapter` | Twilio / SendGrid |
| F10 wearables | adaptery na słownikach | REST/OAuth: Fitbit, Garmin, Zepp, HealthKit |
| F16 consensus | głosy `ModelVote` | 2+ realne modele LLM |

## 7. Bezpieczeństwo i zgodność

- **PII**: wyłącznie zaszyfrowane (Fernet) + blind index do wyszukiwania (F1).
- **AI Act**: `DisclosureLog` (F13) — dowód ujawnienia natury AI w każdej rozmowie.
- **RODO**: retencja + prawo do zapomnienia (F12), `DataProcessingLog` (art. 30).
- **Audyt danych zdrowotnych**: SHA-256 na pomiarach wearables (F10).
- **Fail-safe**: twarde sygnały kryzysowe wykrywane regułowo (F8), consensus
  przy poziomach krytycznych (F16), eskalacja PURPLE zawsze zaczyna od 112 (F17).

## 8. Testy

```bash
cd agent
python3 -m pytest adam_modules/tests/ -q     # 154 testy, w tym E2E (F18)
```
