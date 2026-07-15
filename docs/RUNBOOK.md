# Adam — RUNBOOK (staging / operacje)

> WP-5 · Instrukcja operacyjna uruchomienia backendu Adama w środowisku
> **staging** (docker-compose), seedowania danych demonstracyjnych oraz
> podstawowej diagnostyki i odzyskiwania. Backend jest **stanowy** —
> uruchamiany na maszynie/VM (Frankfurt DC), **nie** na Cloudflare.

---

## 1. Architektura stacku staging

| Usługa               | Obraz / źródło                       | Rola                                   |
|----------------------|--------------------------------------|----------------------------------------|
| `adam-postgres`      | `postgres:16-alpine`                 | Baza danych (PII szyfrowane Fernet)    |
| `adam-redis`         | `redis:7-alpine`                     | Kolejka eskalacji / rate-limit (F3.2)  |
| `adam-api`           | build `Dockerfile.adam-api`          | FastAPI + gunicorn (F1–F18), port 8788 |
| `adam-seed`          | ten sam obraz (profil `seed`)        | Jednorazowy seed danych demo           |

Pliki: `agent/adam_modules/deploy/`
- `docker-compose.staging.yml` — stack staging (samowystarczalny, dev-defaults)
- `docker-compose.adam.yml` — stack **produkcyjny** (wymaga `.env.adam`)
- `Dockerfile.adam-api`, `entrypoint.sh` — obraz API (migracje Alembic → gunicorn)
- `seed_staging.py` — seed seniorów (PII-safe, przez `SeniorService`)
- `seed.sql` — dane referencyjne bez PII (kategorie marketplace)

---

## 2. Uruchomienie (staging)

Z katalogu `agent/`:

```bash
# 1) Zbuduj i podnieś stack (api czeka na zdrowe postgres + redis)
docker compose -f adam_modules/deploy/docker-compose.staging.yml up -d --build

# 2) Migracje Alembic wykonuje entrypoint kontenera automatycznie
#    (ADAM_RUN_MIGRATIONS=1). Zweryfikuj log:
docker compose -f adam_modules/deploy/docker-compose.staging.yml logs adam-api | grep -i migrations

# 3) Seed danych demonstracyjnych (profil „seed”, jednorazowo)
docker compose -f adam_modules/deploy/docker-compose.staging.yml \
  run --rm adam-seed

# 4) (opcjonalnie) dane referencyjne bez PII
docker compose -f adam_modules/deploy/docker-compose.staging.yml \
  exec adam-postgres psql -U adam -d adam \
  -f - < adam_modules/deploy/seed.sql
```

### Walidacja konfiguracji bez uruchamiania (dry-run)
```bash
docker compose -f adam_modules/deploy/docker-compose.staging.yml config
```
> W środowisku bez Dockera składnię YAML można sprawdzić:
> `python -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" <plik>`

---

## 3. Weryfikacja zdrowia (smoke test)

```bash
# Liveness — czy proces żyje (używany przez healthcheck compose / k8s)
curl -fsS http://localhost:8788/health/live        # {"status":"ok"}

# Readiness — czy baza/zależności odpowiadają (503 gdy nie)
curl -fsS http://localhost:8788/health/ready        # {"status":"ready", ...}

# Ogólny health + wersja
curl -fsS http://localhost:8788/health

# Dokumentacja OpenAPI (Swagger UI)
open http://localhost:8788/docs
```

Kryterium „staging OK”: `/health/ready` zwraca `200` i `status: ready`,
a `adam-seed` wypisał `utworzono=4`.

---

## 4. Zmienne środowiskowe (staging vs produkcja)

Staging używa **wartości testowych wbudowanych** w `docker-compose.staging.yml`
(anchor `x-staging-secrets`). **Produkcja** wymaga realnych sekretów w `.env.adam`
(patrz `.env.adam.example`):

| Zmienna              | Staging (default)      | Produkcja (obowiązkowe)                    |
|----------------------|------------------------|--------------------------------------------|
| `ADAM_PII_KEY`       | testowy Fernet         | `Fernet.generate_key()`                    |
| `ADAM_PII_PEPPER`    | testowy pepper         | losowy sekret (blind index)                |
| `ADAM_JWT_SECRET`    | testowy                | `secrets.token_urlsafe(48)`                |
| `ADAM_DATABASE_URL`  | postgres w compose     | PostgreSQL DC                              |
| `ADAM_NOTIFY_PROVIDER`| `memory`              | `live` (Twilio/SendGrid/FCM)               |
| `ADAM_CORS_ORIGINS`  | `*`                    | `https://panel.adam.silvertech.pl`         |

> ⚠️ **Nigdy** nie używać domyślnych sekretów staging na produkcji.

---

## 5. Operacje typowe

```bash
CF="-f adam_modules/deploy/docker-compose.staging.yml"

# Log na żywo (Ctrl-C by wyjść)
docker compose $CF logs -f adam-api

# Restart tylko API (po zmianie kodu → przebuduj)
docker compose $CF up -d --build adam-api

# Wejście do bazy
docker compose $CF exec adam-postgres psql -U adam -d adam

# Reset danych (USUWA wolumen bazy!) i ponowny seed
docker compose $CF down -v
docker compose $CF up -d --build
docker compose $CF run --rm adam-seed

# Zatrzymanie bez utraty danych
docker compose $CF stop
```

---

## 6. Diagnostyka (troubleshooting)

| Objaw                                   | Prawdopodobna przyczyna / działanie                          |
|-----------------------------------------|--------------------------------------------------------------|
| `adam-api` restartuje się w pętli       | Migracje padły → `logs adam-api`; sprawdź `ADAM_DATABASE_URL` |
| `/health/ready` = 503                    | Postgres/Redis nie „healthy” → `docker compose ps`           |
| `seed` kończy `utworzono=0`              | Dane już istnieją (idempotencja) — OK; reset: `down -v`      |
| Błąd Fernet / PII przy starcie          | Brak `ADAM_PII_KEY`/`ADAM_PII_PEPPER`                        |
| Port 8788 zajęty                         | Zmień mapowanie `ports:` lub zwolnij port                    |

Migracje ręcznie (gdy `ADAM_RUN_MIGRATIONS=0`):
```bash
docker compose $CF exec adam-api sh -c \
  "cd /app/adam_modules/migrations && python -m alembic upgrade head"
```

---

## 7. Rollback

```bash
# Cofnięcie ostatniej migracji o jeden krok
docker compose $CF exec adam-api sh -c \
  "cd /app/adam_modules/migrations && python -m alembic downgrade -1"

# Powrót do wcześniejszego obrazu API (jeśli tagowany)
docker compose $CF up -d adam-api   # po git checkout <poprzedni tag> i --build
```

---

## 8. Powiązane dokumenty
- `docs/PROJECT-STATUS.md` — pełny status i mapa modułów F1–F18
- `docs/SANDBOX-WORKPLAN.md` — pakiety WP-1…WP-6 i symulacja postępu
- `docs/CAPACITOR-BUILD.md` — build aplikacji mobilnych (WP-6)
- `ci-templates/adam-ci.yml` — pipeline CI (backend cov gate, frontend, E2E)
