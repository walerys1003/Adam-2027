# ADAM-2027 — CHECKLISTA WDROŻENIOWA (ETAP 23)

> Praktyczna checklista „od zera do live" spinająca cały system. Uzupełnia
> runbooki: [`DEPLOY-ADAM.md`](./DEPLOY-ADAM.md) (API + panel), [`BACKEND-DEPLOY.md`](./BACKEND-DEPLOY.md)
> (tor głosowy Asterisk), [`CAPACITOR-BUILD.md`](./CAPACITOR-BUILD.md) (mobile).
> Stan projektu i procenty: [`AUDIT.md`](./AUDIT.md).
>
> Legenda: ⬜ do zrobienia · 🔧 po stronie SilverTech (infra/konta) · 💻 po stronie kodu (gotowe)

---

## 0. Wymagania wstępne (creditycjale i konta) — 🔧 SilverTech

Zbierz WSZYSTKIE przed startem. Bez nich system nie połączy się spójnie.

### 0.1. Infrastruktura (Frankfurt DC)
- ⬜ 🔧 Serwer/host dla `adam-api` (Docker) + tor głosowy
- ⬜ 🔧 **PostgreSQL** — `ADAM_DATABASE_URL` (np. `postgresql+psycopg://user:pass@host:5432/adam`)
- ⬜ 🔧 **Redis** — `ADAM_REDIS_URL` (np. `redis://adam-redis:6379/0`)
- ⬜ 🔧 **Asterisk ARI** — `ASTERISK_ARI_URL`, `ASTERISK_ARI_USER`, `ASTERISK_ARI_PASS`

### 0.2. Sekrety bezpieczeństwa (wygeneruj — NIE z przykładu)
- ⬜ 🔧 `ADAM_API_KEY` — klucz X-API-Key (frontend ↔ backend)
- ⬜ 🔧 `ADAM_JWT_SECRET` — sekret podpisu JWT (długi, losowy)
- ⬜ 🔧 `ADAM_PII_KEY`, `ADAM_PII_PEPPER` — szyfrowanie/hash PII (RODO)
- ⬜ 🔧 `ADAM_AUTH_USERS` — konta panelu (email:hasło:rola)
- ⬜ 🔧 `ADAM_HSTS=1` (za terminacją TLS)

### 0.3. Dostawcy zewnętrzni (konta + klucze)
- ⬜ 🔧 **Twilio** (SMS): `ADAM_TWILIO_SID`, `ADAM_TWILIO_TOKEN`, `ADAM_TWILIO_FROM`
- ⬜ 🔧 **SendGrid** (email): `ADAM_SENDGRID_KEY`, `ADAM_SENDGRID_FROM`
- ⬜ 🔧 **FCM** (push): `ADAM_FCM_KEY`
- ⬜ 🔧 **OpenAI** (Whisper STT + LLM): `OPENAI_API_KEY`
- ⬜ 🔧 **ElevenLabs** lub OpenAI TTS: `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`

### 0.4. Frontend / mobile
- ⬜ 🔧 **Cloudflare** — token API do Pages (publikacja panelu/PWA)
- ⬜ 🔧 **Apple Developer** ($99/rok) + macOS/Xcode → `.ipa`
- ⬜ 🔧 **Google Play** ($25) → `.aab`

> Pełna tabela zmiennych: `agent/adam_modules/deploy/.env.adam.example`.

---

## 1. Backend API + baza — 💻 kod gotowy / 🔧 uruchomienie

- ⬜ Skopiuj `.env.adam.example` → `.env.adam`, uzupełnij sekcje 0.1–0.3
- ⬜ 🔧 Zbuduj obraz: `docker compose -f agent/adam_modules/deploy/docker-compose.adam.yml build`
- ⬜ 🔧 Start: `docker compose ... up -d` (entrypoint robi `alembic upgrade head`)
- ⬜ **Weryfikacja migracji:** `wrangler`/`alembic current` = `0007` (7 migracji)
- ⬜ **Health (liveness):** `curl http://HOST:8787/health` → `{"status":"ok"}`
- ⬜ **Readiness (DB):** `curl http://HOST:8787/health/ready` → `200` + `"database":"ok"`
      (503 = baza nieosiągalna → sprawdź `ADAM_DATABASE_URL`)
- ⬜ **OpenAPI:** `curl http://HOST:8787/openapi.json` → 51 endpointów, 12 routerów

## 2. Integracje (powiadomienia + głos) — 💻 adaptery gotowe / 🔧 klucze

- ⬜ 🔧 Ustaw klucze Twilio/SendGrid/FCM → test `POST /api/family/dispatch`
- ⬜ 🔧 Ustaw `OPENAI_API_KEY` (+ ElevenLabs) → produkcyjne porty głosu aktywne
      (bez kluczy działają fail-safe/no-op — patrz `voice/prod_ports.py`)
- ⬜ 🔧 Podłącz Asterisk ARI → webhook `POST /api/voice/call-start` inicjuje połączenie
- ⬜ 🔧 Osadź `StasisApp` w procesie Stasis (WebSocket ARI) — patrz `voice/stasis.py`

## 3. Frontend (panel + PWA) — 💻 gotowe / 🔧 publikacja

- ⬜ Ustaw `VITE_API_URL` = adres backendu, `VITE_API_KEY` = `ADAM_API_KEY`
      (bez `VITE_API_URL` frontend działa na mockach — `USE_MOCK`)
- ⬜ Build: `cd frontend && npm ci && npm run build`
- ⬜ 🔧 Publikacja na Cloudflare Pages (`dist/`)
- ⬜ **Weryfikacja live:** logowanie (`/api/auth/login`), lista seniorów,
      Wiadomości (`/api/account/threads`), Konto (`/api/account/invoices`, `/sessions`)
      działają na żywym API (nie mock)
- ⬜ Ustaw CORS backendu na domenę frontendu (`ADAM_CORS_ORIGINS` / konfiguracja)

## 4. CI/CD — 💻 gotowe / 🔧 aktywacja

- ⬜ 🔧 Skopiuj `agent/deploy/ci.yml.ready` → `.github/workflows/ci.yml` i wypchnij
      (wymaga uprawnienia `workflows` — instrukcja: `agent/deploy/CI-ACTIVATION.md`)
- ⬜ Potwierdź zielony bieg: backend (pytest + gate ≥85%) + frontend (typecheck/vitest/build)

## 5. Mobile (opcjonalnie, po panelu) — 🔧 SilverTech

- ⬜ 🔧 `npx cap sync` → build `.ipa` (Xcode) / `.aab` (Android Studio)
- ⬜ 🔧 Publikacja w App Store / Google Play — patrz `CAPACITOR-BUILD.md`

---

## 6. Smoke-test po wdrożeniu (kolejność)

```bash
# 1. liveness + readiness
curl -s $API/health           # {"status":"ok"}
curl -s $API/health/ready      # {"status":"ready","checks":{"database":"ok"}}

# 2. auth (zwraca parę JWT)
curl -s -X POST $API/api/auth/login -H 'content-type: application/json' \
  -d '{"email":"admin@silvertech.pl","password":"***"}'

# 3. zasób chroniony (X-API-Key + Bearer)
curl -s $API/api/seniors -H "X-API-Key: $ADAM_API_KEY" -H "Authorization: Bearer $TOKEN"

# 4. wiadomości / konto (ETAP 22)
curl -s $API/api/account/threads  -H "X-API-Key: $ADAM_API_KEY"
curl -s $API/api/account/invoices -H "X-API-Key: $ADAM_API_KEY"
```

---

## 7. Definicja „gotowe do produkcji" (Definition of Done)

- ✅ `/health/ready` = 200 (DB podłączona, migracje `0007`)
- ✅ Logowanie panelu działa na żywym API (JWT), wszystkie panele bez mocków
- ✅ Powiadomienia (SMS/email/push) wychodzą przez realnych dostawców
- ✅ Tor głosowy: `call-start` inicjuje połączenie, Stasis prowadzi rozmowę,
     konsensus kryzysowy aktywny (detektor F3 + LLM)
- ✅ CI zielone na `main`
- ✅ Frontend opublikowany na Cloudflare Pages z poprawnym `VITE_API_URL`

> **Stan kodu:** wszystkie pozycje 💻 są zrealizowane i przetestowane
> (backend: 295 testów; frontend: 29 testów api). Pozostają pozycje 🔧
> (infrastruktura, konta, klucze) — po stronie SilverTech.
