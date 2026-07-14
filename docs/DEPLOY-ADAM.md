# Adam API — Runbook wdrożeniowy (ETAP 15)

> **Zakres:** ten runbook opisuje wdrożenie **warstwy REST Adama** (`adam_modules/api`,
> panel opiekuna/admina/rodziny) jako osobnego, samodzielnego serwisu.
> To **inny artefakt** niż agent głosowy AVA/Asterisk opisany w
> [`BACKEND-DEPLOY.md`](./BACKEND-DEPLOY.md) — tamten dokument opisuje tor
> telefoniczny (Asterisk ARI + scheduler), a ten: API + baza + cache pod panel.
> Oba serwisy współdzielą tę samą bazę PostgreSQL (Frankfurt DC) i pakiet
> `adam_modules`.

## 1. Co jest wdrażane

| Artefakt | Plik | Rola |
|---|---|---|
| Obraz API | `agent/adam_modules/deploy/Dockerfile.adam-api` | multi-stage, non-root (uid 10001), gunicorn + uvicorn workers |
| Entrypoint | `agent/adam_modules/deploy/entrypoint.sh` | migracje Alembic (`upgrade head`) → start gunicorn |
| Compose | `agent/adam_modules/deploy/docker-compose.adam.yml` | `adam-api` + `adam-postgres` + `adam-redis` |
| Env | `agent/adam_modules/deploy/.env.adam.example` | szablon konfiguracji produkcyjnej |

Serwis nasłuchuje na **:8787**, wystawia `/health`, `/metrics`, `/docs` oraz
routery `/api/*` (seniorzy, safety, leki, wearables, rodzina, marketplace, RODO,
compliance, **auth**, **voice**).

```
   Panel / PWA (Cloudflare Pages)
            │ REST + SSE (X-API-Key / Bearer JWT)
            ▼
   ┌──────────────────────────────────────────┐
   │  adam-api  (gunicorn + UvicornWorker :8787)│
   │   RateLimit → RequestContext → CORS → app  │
   └───────────────┬───────────────┬────────────┘
                   ▼               ▼
            adam-postgres     adam-redis
            (dane, audyt)     (cache/kolejki)
```

## 2. Wymagania

- Docker 24+ oraz docker compose v2
- Lokalizacja: **UE / Frankfurt** (RODO — dane seniorów)
- Wolny port dla API (domyślnie `8787`, konfigurowalny `ADAM_API_PORT`)
- PostgreSQL 16 (dostarczany przez compose lub zewnętrzny managed PG)

## 3. Generowanie sekretów (jednorazowo, przed pierwszym startem)

```bash
cd agent/adam_modules/deploy
cp .env.adam.example .env.adam

# 1) klucz PII (Fernet) — STAŁY na zawsze (zmiana = utrata dostępu do PII)
python3 -c "from cryptography.fernet import Fernet; print('ADAM_PII_KEY='+Fernet.generate_key().decode())"

# 2) pepper blind-index — STAŁY na zawsze
python3 -c "import secrets; print('ADAM_PII_PEPPER='+secrets.token_urlsafe(32))"

# 3) sekret JWT (podpis tokenów HS256)
python3 -c "import secrets; print('ADAM_JWT_SECRET='+secrets.token_urlsafe(48))"

# 4) hasło bazy
python3 -c "import secrets; print('POSTGRES_PASSWORD='+secrets.token_urlsafe(24))"
```

Wklej wygenerowane wartości do `.env.adam`. Ustaw też `ADAM_CORS_ORIGINS`
(origin panelu, np. `https://panel.adam.silvertech.pl`) i — jeśli używasz
realnych powiadomień — `ADAM_NOTIFY_PROVIDER=live` wraz z sekretami Twilio /
SendGrid / FCM.

> ⚠️ **`ADAM_PII_KEY` i `ADAM_PII_PEPPER` są niezmienne między wdrożeniami.**
> Ich rotacja unieważnia odszyfrowanie istniejących danych osobowych.
> Przechowuj je w menedżerze sekretów (np. Vault / SOPS), nie w repo.

## 4. Uruchomienie

```bash
cd agent/adam_modules/deploy

# build + start (API zbudowane z kontekstu agent/, patrz `build.context: ../..`)
docker compose -f docker-compose.adam.yml --env-file .env.adam up -d --build

# podgląd startu (migracje + gunicorn)
docker compose -f docker-compose.adam.yml logs -f adam-api
```

Podczas startu `entrypoint.sh`:
1. uruchamia `alembic upgrade head` (łańcuch `0001 → 0007`, `env.py` czyta `ADAM_DATABASE_URL`),
2. startuje `gunicorn adam_modules.api.app:app -k uvicorn.workers.UvicornWorker -w $ADAM_API_WORKERS`.

Aby pominąć migracje (np. gdy stosujesz je z osobnego joba) ustaw
`ADAM_RUN_MIGRATIONS=0`.

## 5. Migracje bazy

Migracje wykonują się automatycznie przy starcie kontenera. Ręcznie:

```bash
# wewnątrz kontenera
docker compose -f docker-compose.adam.yml exec adam-api \
  sh -c 'cd /app/adam_modules/migrations && python -m alembic upgrade head'

# sprawdzenie aktualnej rewizji (powinno pokazać 0007 = head)
docker compose -f docker-compose.adam.yml exec adam-api \
  sh -c 'cd /app/adam_modules/migrations && python -m alembic current'
```

Łańcuch: `0001` seniorzy · `0002` scheduler · `0003` semaphore · `0004` leki ·
`0005` pamięć · `0006` rodzina/wearables/marketplace/RODO · `0007` disclosure_logs.

## 6. Weryfikacja po wdrożeniu (smoke test)

```bash
BASE=http://localhost:8787

# 1) health — 200 {"status":"ok"}
curl -fsS $BASE/health

# 2) metryki Prometheus
curl -fsS $BASE/metrics | head

# 3) logowanie (demo user) → token
curl -fsS -X POST $BASE/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@silvertech.pl","password":"admin123"}'

# 4) /me z Bearerem (podstaw <ACCESS>)
curl -fsS $BASE/api/auth/me -H "Authorization: Bearer <ACCESS>"
```

> Konta demonstracyjne (`_demo_store`) są tylko dla dev/UAT. W produkcji ustaw
> `ADAM_AUTH_USERS` (format `email:hasło:rola:senior_ids;...`) lub podłącz
> właściwy magazyn użytkowników.

## 7. Skalowanie (gunicorn workers)

Liczbę procesów roboczych ustawia `ADAM_API_WORKERS` (domyślnie 4).
Reguła startowa: `workers = 2 × rdzenie + 1`.

```bash
# przykład: 8 workerów, restart bez przestoju obrazu
ADAM_API_WORKERS=8 docker compose -f docker-compose.adam.yml \
  --env-file .env.adam up -d
```

- CPU-bound? zwiększaj workery ostrożnie i obserwuj `adam_request_latency`.
- I/O-bound (większość ruchu to zapytania do PG)? UvicornWorker (async) dobrze
  znosi współbieżność — profiluj zanim dołożysz workery.
- Skalowanie poziome: uruchom wiele instancji `adam-api` za reverse-proxy
  (np. Traefik/nginx). Stan jest w PG/Redis, API jest bezstanowe.

## 8. Monitoring

### `/metrics` (Prometheus, format tekstowy)
Wystawiane liczniki (rejestr `MetricsRegistry`, middleware `RequestContext`):
- `adam_requests_total{method,path,status}` — liczba żądań,
- `adam_request_latency_ms` — histogram/statystyki opóźnień,
- `adam_rate_limited_total` — odrzucenia przez limiter (429).

Przykładowy scrape (prometheus.yml):
```yaml
scrape_configs:
  - job_name: adam-api
    metrics_path: /metrics
    static_configs:
      - targets: ["adam-api:8787"]
```

### Nagłówki diagnostyczne
Każda odpowiedź niesie `X-Request-ID` (korelacja logów) i
`X-Response-Time-ms`. Logi są strukturalne (logger `adam.api`) — zbieraj je
np. przez Loki/ELK i koreluj po `X-Request-ID`.

### Rate limiting
Token-bucket per-klient: `ADAM_RATE_LIMIT` żądań / `ADAM_RATE_WINDOW` s
(domyślnie 120/60). Ścieżki `/health`, `/metrics`, `/` są zwolnione, żeby
scrape i healthcheck nigdy nie były throttlowane. Przekroczenie → `429` +
`Retry-After`. Wyłączenie: `ADAM_RATE_LIMIT_ENABLED=0`.

### Healthcheck
Obraz ma wbudowany `HEALTHCHECK` (`curl /health` co 30 s). W compose
`adam-api` zależy od zdrowego `adam-postgres` (`pg_isready`). Stan:
```bash
docker compose -f docker-compose.adam.yml ps
```

## 9. Kopie i odtwarzanie bazy

```bash
# backup
docker compose -f docker-compose.adam.yml exec adam-postgres \
  pg_dump -U adam adam > adam_backup_$(date +%F).sql

# restore
cat adam_backup_YYYY-MM-DD.sql | docker compose -f docker-compose.adam.yml \
  exec -T adam-postgres psql -U adam adam
```

Wolumen danych: `adam-pgdata` (nazwany wolumen). Backupuj również sekrety PII
(bez nich zrzut bazy jest bezużyteczny — PII jest zaszyfrowane Fernetem).

## 10. Aktualizacja (redeploy)

```bash
cd agent && git pull
cd adam_modules/deploy
docker compose -f docker-compose.adam.yml --env-file .env.adam up -d --build
# nowe migracje zastosują się automatycznie przy starcie (upgrade head)
```

Rollback: wdróż poprzedni tag obrazu; jeśli migracja wprowadziła zmianę
schematu, cofnij ją świadomie `alembic downgrade <rev>` (weryfikuj zgodność
danych — downgrade bywa stratny).

## 11. Bezpieczeństwo produkcyjne (checklista)

- [ ] `ADAM_PII_KEY` / `ADAM_PII_PEPPER` z menedżera sekretów, nie w repo.
- [ ] `ADAM_JWT_SECRET` losowy, ≥ 48 znaków, rotowalny (rotacja unieważnia sesje).
- [ ] `ADAM_API_KEY` ustawiony, jeśli panel korzysta z nagłówka `X-API-Key`.
- [ ] `ADAM_CORS_ORIGINS` = wyłącznie origin panelu (bez `*`).
- [ ] PostgreSQL bez portów wystawionych na zewnątrz (compose już tego nie robi).
- [ ] TLS terminowany na reverse-proxy przed `adam-api`.
- [ ] Konta demo wyłączone; `ADAM_AUTH_USERS` lub realny IdP.
- [ ] Retencja i prawo do zapomnienia (RODO F12) skonfigurowane.
```
