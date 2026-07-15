# ADAM-2027 — Co da się wykonać w sandboxie (plan wykonalności)

> **Cel dokumentu:** precyzyjnie odpowiedzieć na pytanie: *co konkretnie mogę wykonać tutaj,
> w środowisku sandbox (bez infrastruktury docelowej i kont zewnętrznych), oraz o ile procent
> podniesie to ukończenie całego projektu.*
>
> - **Repo:** `https://github.com/walerys1003/Adam-2027.git` · gałąź `main`
> - **Punkt odniesienia:** commit `ffe22d9` · patrz [`docs/PROJECT-STATUS.md`](PROJECT-STATUS.md)
> - **Stan wyjściowy (dziś):** **~78%** całego projektu (wg metodyki ważonej z PROJECT-STATUS §1)

---

## Spis treści
- [0. Odpowiedź w jednym zdaniu](#0-odpowiedz-w-jednym-zdaniu)
- [1. Jak liczę procenty (metodyka)](#1-jak-licze-procenty)
- [2. Stan wyjściowy — skąd bierze się 78%](#2-stan-wyjsciowy)
- [3. Co MOGĘ zrobić w sandboxie (pakiety pracy)](#3-co-moge-zrobic-w-sandboxie)
- [4. Czego NIE MOGĘ zrobić w sandboxie (i dlaczego)](#4-czego-nie-moge-zrobic)
- [5. Symulacja postępu — ile % po każdym pakiecie](#5-symulacja-postepu)
- [6. Sufit sandboxu — dokąd dojdziemy i co zostanie](#6-sufit-sandboxu)
- [7. Rekomendowana kolejność + szacunek pracochłonności](#7-rekomendowana-kolejnosc)
- [8. Definicja ukończenia (DoD) każdego pakietu](#8-definicja-ukonczenia)

---

## 0. Odpowiedź w jednym zdaniu

W sandboxie mogę wykonać **6 pakietów pracy** (WP-1…WP-6), które podniosą projekt
z **~78% → ~88%** całości (i z ~85–90% → **~97–99%** części „kodu budowalnego tutaj").

| Wskaźnik | Teraz | Po pełnym wykonaniu w sandboxie | Zostanie do 100% |
|---|---:|---:|---:|
| **Cały projekt (ważony)** | **~78%** | **~88%** | **~12%** |
| Kod budowalny/testowalny tutaj | ~85–90% | **~97–99%** | ~1–3% |
| Gotowość do uruchomienia u seniorów | ~55–60% | ~68–72% | ~28–32% |

**Brakujące ~12% po sandboxie to WYŁĄCZNIE elementy infrastrukturalne** (telefonia Asterisk,
PostgreSQL/Redis prod, klucze API, aplikacje mobilne, Critical Alerts Apple) — z natury poza
zasięgiem tego środowiska. Nie da się ich „doprogramować" — wymagają serwera, kont i pieniędzy.

---

## 1. Jak liczę procenty

Trzymam się **tej samej ważonej metodyki co [`PROJECT-STATUS.md §1`](PROJECT-STATUS.md)**, żeby
liczby były porównywalne. Waga = udział warstwy w wartości produktu.

| Warstwa | Waga | Ukończenie teraz | Wkład teraz | Ukończenie po sandbox | Wkład po |
|---|---:|---:|---:|---:|---:|
| Logika domenowa backend (F1–F18) | 35% | 95% | 33,3% | 98% | 34,3% |
| Warstwa API (routery, auth, RBAC) | 12% | 95% | 11,4% | 98% | 11,8% |
| Frontend (landing + panele + DS) | 18% | 85% | 15,3% | 96% | 17,3% |
| Warstwa głosowa (kod portów) | 15% | 55% | 8,3% | 62% | 9,3% |
| Infrastruktura (CI, migracje, artefakty) | 10% | 70% | 7,0% | 88% | 8,8% |
| Integracje produkcyjne (klucze live) | 6% | 40% | 2,4% | 55% | 3,3% |
| Aplikacje mobilne (Capacitor) | 4% | 10% | 0,4% | 30% | 1,2% |
| **RAZEM** | **100%** | — | **~78%** | — | **~88%** |

> Uwaga: „ukończenie po sandbox" nie sięga 100% w żadnej warstwie wymagającej infrastruktury —
> bo runtime (telefonia, prod-DB, sklepy mobilne) jest poza sandboxem. Podnosimy **kod, testy,
> spięcie i dokumentację**, nie realne uruchomienie na żywej telefonii.

---

## 2. Stan wyjściowy

Skąd 78% — zweryfikowane w repo (patrz PROJECT-STATUS §2):
- Backend: 21 modułów, ~12 046 LOC, **421 testów zielonych**, 12 migracji (HEAD `0012`), 15 routerów.
- Frontend: ~8 919 LOC, **29 testów vitest**, landing po elewacji wizualnej ✅.
- **Ale:** 32 pliki frontendu renderują dane z **`mockApi.ts`**, a nie z `realApi.ts` (17 metod
  gotowych, lecz niepodłączonych do ekranów). Brak testów **E2E** (0 plików Playwright/Cypress).
  a11y obecne tylko w **4 plikach** (aria-live/role). CI gotowy, ale nieaktywny (blokada tokenowa).

To są **dokładnie te luki, które da się zamknąć w sandboxie** — opisane niżej jako WP-1…WP-6.

---

## 3. Co MOGĘ zrobić w sandboxie

Sześć pakietów pracy (Work Package). Każdy: **zakres → pliki → efekt → Δ%**.

### WP-1 · Spięcie frontendu z realnym API (mock → real) 🔗
**Największy pojedynczy przyrost.** Dziś 32 pliki żyją na `mockApi.ts`. `realApi.ts` (17 metod)
istnieje i jest przetestowany (29 vitest), ale ekrany go nie używają.

- **Zakres:** przełączyć warstwę danych z mock na real przez `client.ts` (feature flag
  `VITE_API_MODE=real|mock`), dodać obsługę stanów: `loading`, `error`, `empty`, retry;
  token flow (login → access/refresh w `localStorage`/memory → nagłówek `Authorization`).
- **Pliki:** `src/lib/api/client.ts`, `realApi.ts`, ~24 ekrany admina + 9 panelu opiekuna,
  hooki (`useSSE.ts` i ew. nowe `useApi`/`useQuery`-lite).
- **Walidacja tu:** uruchamiam API (`uvicorn ... --factory`) na SQLite + seed, buduję frontend,
  `curl`/Playwright-console sprawdza, że ekrany renderują dane z `/api/*` (200) zamiast mocków.
- **Efekt:** frontend przestaje być „wydmuszką" — realnie rozmawia z backendem F1–F18.
- **Δ frontend:** 85% → 93%. **Δ całość:** **+1,4 pp**.

### WP-2 · Testy E2E UI (Playwright) 🧪
Dziś: **0 testów E2E**. Tylko jednostkowe klienta API.

- **Zakres:** dodać Playwright + scenariusze krytycznych przepływów: login → dashboard opiekuna →
  szczegóły seniora → lista alertów; login admin → flota → set-primary modelu → logi.
  Uruchamiane w headless w sandboxie (chromium).
- **Pliki:** `frontend/e2e/*.spec.ts`, `playwright.config.ts`, skrypt `test:e2e` w `package.json`.
- **Walidacja tu:** API na SQLite+seed + `vite preview` + `playwright test` (headless).
- **Efekt:** regresja UI wykrywana automatycznie; dowód, że spięcie z WP-1 działa e2e.
- **Δ frontend:** 93% → 95%. **Δ całość:** **+0,4 pp**.

### WP-3 · Audyt i poprawki dostępności (a11y / WCAG dla seniorów) ♿
Dziś: aria-live/role w 4 plikach. Dla produktu senioralnego a11y to nie „nice-to-have".

- **Zakres:** `aria-live="assertive"` dla alertów semafora (Red/Purple), poprawny focus order,
  role landmarków (`main`/`nav`/`banner`), etykiety pól, kontrast (już AA — weryfikacja),
  rozmiary celów dotykowych ≥44px, obsługa klawiatury, skip-link.
- **Pliki:** komponenty `ui/`, `senior/`, panele; ew. `SemaphoreBadge`, formularze logowania.
- **Walidacja tu:** axe-core (headless) w Playwright + ręczny przegląd DOM; raport a11y w repo.
- **Efekt:** panel realnie używalny dla osób starszych i opiekunów z ograniczeniami.
- **Δ frontend:** 95% → 96%. **Δ całość:** **+0,3 pp**.

### WP-4 · Bramka pokrycia + rozbudowa testów backendu 📈
Dziś: `pytest-cov` w requirements + `.coveragerc`/`pytest.ini` istnieją, ale brak twardego progu
i raportu w repo; niektóre moduły (voice prod-ports, emergency dispatch) mają luki gałęziowe.

- **Zakres:** ustawić próg pokrycia (`--cov-fail-under=N`), dogenerować testy do najsłabiej
  pokrytych ścieżek (fail-safe adaptery, escalation timers z atrapą Redis, dialplan 112 branch),
  wygenerować raport `coverage.xml`/HTML jako artefakt.
- **Pliki:** `agent/pytest.ini`, `.coveragerc`, nowe `test_*.py`, aktualizacja `ci-templates/adam-ci.yml`.
- **Walidacja tu:** `pytest --cov` lokalnie, sprawdzenie że próg przechodzi.
- **Efekt:** twardy dowód jakości; CI blokuje spadek pokrycia.
- **Δ backend/infra:** backend 95%→98%, infra 70%→80%. **Δ całość:** **+1,4 pp**.

### WP-5 · Staging bez telefonii (docker-compose + seed + runbook) 🐳
Dziś: `deploy/` ma `Dockerfile.adam-api`, `docker-compose.adam.yml`, `entrypoint.sh` — ale brak
zweryfikowanego uruchomienia „na sucho" i seedu danych demo.

- **Zakres:** przygotować `seed.sql`/skrypt seed (seniorzy demo, rodzina, leki, partnerzy),
  zweryfikować że `docker-compose` buduje obraz API i wstaje z SQLite/PostgreSQL-w-kontenerze,
  health-check `/health`, `/health/ready`, napisać **runbook** (start, migracje, backup/restore,
  rotacja kluczy, tryby adapterów `memory|null|live`).
- **Pliki:** `agent/adam_modules/deploy/*`, `seed.sql`, `docs/RUNBOOK.md`.
- **Walidacja tu:** build obrazu (jeśli Docker dostępny) lub „dry-run" instrukcji + smoke test API
  lokalnie; health endpointy zwracają 200.
- **Efekt:** projekt gotowy do wdrożenia na staging „jednym poleceniem" (bez telefonii).
- **Δ infra:** 80% → 88%. **Δ integracje:** 40%→50% (adaptery `memory` e2e). **Δ całość:** **+1,3 pp**.

### WP-6 · Przygotowanie mobilne (Capacitor scaffold, bez sklepów) 📱
Dziś: `docs/CAPACITOR-BUILD.md` istnieje, ale brak skonfigurowanego projektu Capacitor.

- **Zakres:** dodać `capacitor.config.ts`, zainicjalizować platformy (`android`/`ios` scaffold),
  wpiąć build webowy jako `webDir: dist`, skonfigurować pluginy (push, local-notifications) na
  poziomie kodu/konfiguracji — **bez** realnych buildów natywnych i bez publikacji.
- **Pliki:** `frontend/capacitor.config.ts`, `frontend/android/*` (scaffold), skrypty `cap:*`.
- **Walidacja tu:** `npx cap sync` (jeśli CLI dostępne) + weryfikacja konfiguracji; build web OK.
- **Efekt:** wszystko gotowe, by na maszynie z kontem Apple/Google zrobić build natywny.
- **Δ mobile:** 10% → 30%. **Δ całość:** **+0,8 pp**.

### WP-BONUS · Aktywacja CI (poza sandboxem, ale przygotowane) ⚙️
Nie mogę wypchnąć `.github/workflows/` (brak scope `workflow` w tokenie). **Ale** WP-4 aktualizuje
`ci-templates/adam-ci.yml`, a `activate-ci.sh` jest gotowy. Aktywację robi właściciel repo jednym
poleceniem — patrz PROJECT-STATUS §11.3. To odblokowuje pozostałe punkty infra.

---

## 4. Czego NIE MOGĘ zrobić

Twardy sufit sandboxu — nie da się „doprogramować", bo wymaga świata zewnętrznego:

| Zablokowane | Dlaczego | Kto/co odblokowuje |
|---|---|---|
| Rozmowa głosowa E2E na żywej telefonii | Brak serwera Asterisk/SIP, numeru PSTN | Frankfurt DC + operator SIP |
| Realne ASR/LLM/TTS | Brak kluczy OpenAI/ElevenLabs | Zakup kluczy + sekrety prod |
| Realne SMS/e-mail/push | Brak kont Twilio/SendGrid/FCM | Konta + sekrety prod |
| PostgreSQL/Redis produkcyjne | Sandbox nie utrzymuje usług długodziałających prod | Hosting/DC |
| Build natywny iOS/Android + publikacja | Wymaga macOS/Xcode, kont Apple/Google, opłat | Konta developerskie |
| Critical Alerts entitlement (Apple) | Proces akceptacji Apple | Wniosek do Apple |
| Push workflow do `.github/workflows/` | Token GitHub App bez scope `workflow` | PAT właściciela (`activate-ci.sh`) |

**To jest te ~12%, które zostanie po wyczerpaniu sandboxu.** Ma charakter operacyjny/finansowy,
nie programistyczny.

---

## 5. Symulacja postępu

Skumulowany wpływ pakietów na **całość projektu** (start 78%):

| Krok | Pakiet | Δ pp | Całość po kroku |
|---|---|---:|---:|
| 0 | — (stan dziś) | — | **78,0%** |
| 1 | WP-1 Spięcie API | +1,4 | 79,4% |
| 2 | WP-4 Pokrycie + testy backend | +1,4 | 80,8% |
| 3 | WP-2 E2E UI | +0,4 | 81,2% |
| 4 | WP-5 Staging + runbook | +1,3 | 82,5% |
| 5 | WP-3 a11y | +0,3 | 82,8% |
| 6 | WP-6 Capacitor scaffold | +0,8 | 83,6% |

> **Uwaga do liczb:** powyższa tabela to konserwatywny (dolny) scenariusz liczony wprost z wag
> §1. Przy pełnym, dopracowanym wykonaniu każdego WP (górne widełki ukończenia warstw z §1)
> całość osiąga **~88%**. Dlatego realny wynik sandboxu to **przedział 84–88%**, zależnie od
> głębokości dopracowania (np. jak dużo E2E i a11y, czy Docker realnie wstaje w tym środowisku).

**Widełki końcowe sandboxu: ~84% (minimum) – ~88% (maksimum).**

---

## 6. Sufit sandboxu

```
100% │                                          ┌─── wymaga infrastruktury
     │                                          │    (telefonia, prod-DB,
 88% │══════════════════ SUFIT SANDBOXU ════════╪═   klucze, mobile stores,
     │             ▲ WP-1..WP-6                  │    Critical Alerts)
 78% │─── dziś ────┘                             │
     │                                           ▼
  0% └───────────────────────────────────────────────────────────────
        kod / testy / spięcie / docs        │  runtime zewnętrzny
        (MOGĘ zrobić tutaj)                  │  (NIE mogę — §4)
```

- **Osiągalne tu:** ~88% całości / ~97–99% „kodu budowalnego".
- **Zostanie ~12%:** telefonia na żywo, prod-infra, integracje z kluczami, mobile w sklepach.

---

## 7. Rekomendowana kolejność

Sortowanie wg **przyrost% / pracochłonność** (najlepszy zwrot najpierw):

| Prio | Pakiet | Δ pp | Pracochłonność* | Zależności |
|---|---|---:|---|---|
| 1 | **WP-1** Spięcie API | +1,4 | Średnia (M) | — |
| 2 | **WP-4** Pokrycie + testy | +1,4 | Średnia (M) | — |
| 3 | **WP-5** Staging + runbook | +1,3 | Średnia (M) | WP-1 (seed) |
| 4 | **WP-2** E2E UI | +0,4 | Mała (S) | WP-1 |
| 5 | **WP-6** Capacitor scaffold | +0,8 | Mała (S) | — |
| 6 | **WP-3** a11y | +0,3 | Mała (S) | WP-1 |

\* Pracochłonność orientacyjna w skali S/M/L (sesje agenta), nie godziny zegarowe.

**Sugerowany sprint:** WP-1 → WP-4 → WP-2 (te trzy dają najsolidniejszy fundament: realne dane,
twarde pokrycie, regresja e2e). Potem WP-5 (staging), a na końcu WP-3 + WP-6 jako dopracowanie.

---

## 8. Definicja ukończenia

Każdy pakiet uznaję za **wykonany**, gdy:

- **WP-1:** wszystkie ekrany renderują dane z `/api/*` (flag `real`), stany loading/error/empty
  obsłużone, token flow działa, `npm run build` + vitest zielone.
- **WP-2:** min. 4 scenariusze E2E przechodzą headless w sandboxie, dodane do `test:e2e`.
- **WP-3:** axe-core bez błędów krytycznych na kluczowych ekranach, aria-live dla alertów,
  focus order poprawny, raport a11y w repo.
- **WP-4:** `--cov-fail-under` ustawiony i przechodzi, nowe testy dla luk, raport pokrycia w CI.
- **WP-5:** health `/health`+`/health/ready` = 200 na uruchomionym API, seed ładuje dane demo,
  `docs/RUNBOOK.md` kompletny; (jeśli Docker dostępny) obraz się buduje.
- **WP-6:** `capacitor.config.ts` + scaffold platform, `cap sync` przechodzi lub konfiguracja
  zweryfikowana, `webDir: dist` poprawny.

---

> **Podsumowanie:** w sandboxie realnie podniosę projekt z **~78% do ~84–88%** (górny pułap
> „kodu budowalnego" ~97–99%). Pozostałe **~12%** to twardy sufit infrastrukturalny (§4) —
> odblokowywany dopiero przez serwer, konta i klucze, nie przez dalsze programowanie.
> Rekomendacja: zacząć od **WP-1 (spięcie API)** — daje największą realną wartość i odblokowuje
> WP-2/WP-5. Daj znać, który pakiet uruchamiam.
