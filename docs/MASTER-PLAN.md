# ADAM-2027 · MASTER PLAN wykonawczy

> Szczegółowe rozbicie WSZYSTKICH zadań na etapy i podetapy.
> Każdy etap zamyka się działającym buildem + commitem/pushem do GitHub.
> Legenda wykonalności: 🟢 pełne w sandboxie · 🟡 kod tu, uruchomienie = infra · 🔴 wymaga kont/urządzeń zewnętrznych.
>
> **Uwaga o „500 zadań na etap":** poniżej rozpisuję realne, atomowe zadania (setki pozycji).
> Nie rozdrabniam sztucznie w nieskończoność — każda pozycja to konkretny plik/komponent/funkcja,
> którą da się zbudować i zweryfikować. Numeracja `E{etap}.{podetap}.{zadanie}`.

---

## Legenda statusów
- `[x]` ukończone i wypchnięte
- `[~]` w toku
- `[ ]` do zrobienia

---

## ETAP 0 — Fundament (✅ UKOŃCZONE, commit e7f5784)
- [x] E0.1 Rozpakowanie AVA + design-system
- [x] E0.2 Konwersja 13 .docx → Markdown
- [x] E0.3 RAG: chunking (505) + embeddingi (505×384) + CLI query
- [x] E0.4 Krytyczna analiza + ROADMAP.md
- [x] E0.5 Repo GitHub ADAM-2027 + push 868 plików (w tym pełny agent/ AVA)

## ETAP 1 — Design System w React (✅ UKOŃCZONE, commit 2639bfe)
- [x] E1.1 Scaffold frontend/ (React18+TS+Vite+Tailwind)
- [x] E1.2 tokens.css + tailwind.config (granat/złoto/semafor) + Fraunces/Geist
- [x] E1.3 ui/: SemaphoreBadge, Button, Card, Badge, Avatar, Stat, RadialGauge, Sparkline
- [x] E1.4 senior/: SeniorCard, MoodChart, MedicationList, WearableWidget
- [x] E1.5 DesignSystemPage (demo)

## ETAP 2 — Landing Page Wariant B (✅ UKOŃCZONE, commit 78530d1)
- [x] E2.1–E2.11 Nav, Hero, Signoff, 3 rozdziały, Partnerzy, Testimonial, Cennik, FinalCTA, Footer + routing

## ETAP 3 — Kontrakty + mock API + RBAC (✅ UKOŃCZONE, commit e45a5b0)
- [x] E3.1 types/domain.ts
- [x] E3.2 mockApi.ts + client.ts (przełącznik mock/real)
- [x] E3.3 rbac.ts (admin/caregiver/family_member + permissions)
- [x] E3.4 AuthContext + RequireAuth + LoginPage (konta demo)

---

## ETAP 4 — Panel Opiekuna (8 ekranów) ✅ (commit 22e3636)

### 4.1 Fundament panelu (✅ część 1, commit 979ab3c)
- [x] E4.1.1 PanelLayout (sidebar 240px + topbar + mobile bottom nav + drawer)
- [x] E4.1.2 PageHead
- [x] E4.1.3 CriticalAlertBanner
- [x] E4.1.4 DashboardPage (KPI strip + lista SeniorCard)

### 4.2 Ekran 2: Widok seniora + 8 tabów (`/panel/senior/:id`)
- [x] E4.2.1 SeniorDetailHead (avatar 88px, semafor, 5 quick stats, akcje: Zadzwoń/Notatka/Kontakt)
- [x] E4.2.2 Tabs (komponent ui/ z 8 zakładkami, deep-link `?tab=`)
- [x] E4.2.3 Tab Przegląd: MoodChart 14d + RecentCalls(3) + MedList summary + AI Observations + EmergencyContacts
- [x] E4.2.4 Tab Rozmowy: tabela transkryptów + tools + audio playback (mock)
- [x] E4.2.5 Tab Leki: harmonogram rano/południe/wieczór + heatmap adherence 30d (7×5)
- [x] E4.2.6 Tab Wearable: live vitals 4× + HR chart 24h (threshold band) + sleep phases + steps 7d + progi READ-ONLY + notatki kontekstowe
- [x] E4.2.7 Tab Alerty: timeline historii z poziomami semafora
- [x] E4.2.8 Tab Raporty: karty tygodniowy/miesięczny PDF
- [x] E4.2.9 Tab Rodzina (RBAC): kontakty alarmowe z rolami (Opiekun Główny/Opiekun/Lekarz/112)
- [x] E4.2.10 Tab RODO: zgody + retencja + prawo do usunięcia

### 4.3 Ekran 3: Zamówienia (`/panel/orders`)
- [x] E4.3.1 Info banner „30-min okno anulowania"
- [x] E4.3.2 OrderCard + useCancellationCountdown (countdown 27:00)
- [x] E4.3.3 Sekcje: aktywne (złoty/zielony/żółty pasek), historia 30d
- [x] E4.3.4 CategoryPicker (10 kategorii AUTO/HYBRID/MANUAL) + createOrder/cancelOrder

### 4.4 Ekran 4: Wiadomości (`/panel/messages`)
- [x] E4.4.1 3-kolumnowy inbox: InboxFilters (Adam/Koordynator/Rodzina/Partnerzy)
- [x] E4.4.2 MessageList (avatary, preview, badges)
- [x] E4.4.3 MessageThread (header + body + reply box + audio)

### 4.5 Ekran 5: Raporty (`/panel/reports`)
- [x] E4.5.1 5 KPI + ReportsTrendChart 90d (mood+adherence overlay + markery)
- [x] E4.5.2 FeaturedReport (4 sparkline + timeline 7 dni + akcje PDF/Share/Lekarz)
- [x] E4.5.3 ReportsCalendarHeatmap (26 tygodni) + FHIRExportInfo + retencja

### 4.6 Ekran 6: Konto (`/panel/account`)
- [x] E4.6.1 SubscriptionHero (Rodzinny 79zł + CTA Upgrade)
- [x] E4.6.2 LoyaltyProgress + ReferralCard
- [x] E4.6.3 Banner roli + dane osobowe + „Twoi bliscy 1/5"
- [x] E4.6.4 SessionCard (3 urządzenia) + InvoiceTable

### 4.7 Ekran 7: Ustawienia (`/panel/settings`)
- [x] E4.7.1 Sticky sidebar 6 sekcji + status „12/12"
- [x] E4.7.2 NotificationMatrix 5×4 (Push/SMS/Email/Telefon × Green/Yellow/Red/Purple), Purple×Telefon locked
- [x] E4.7.3 QuietHours + Language + Security(2FA) + GDPR(4 karty)

### 4.8 Ekran 8: Pomoc (`/panel/help`)
- [x] E4.8.1 SupportStatusBar (4 KPI) + EmergencyBox (24/7)
- [x] E4.8.2 3 kanały (Chat/Telefon/Email) + VideoTutorial×4
- [x] E4.8.3 FAQAccordion(6) + kontakt zespół + społeczność

### 4.9 Domknięcie
- [x] E4.9.1 Routing wszystkich 8 ekranów + guards
- [x] E4.9.2 useSSE hook (mock event stream alertów)
- [x] E4.9.3 Build + Playwright weryfikacja + commit/push

---

## ETAP 5 — Panel Admina (23 ekrany) ✅

### 5.1 Fundament admin
- [x] E5.1.1 AdminLayout (sidebar 3 sekcje: Overview/Core config/System) + topbar (BEZ ThemeToggle — light-only wg dyrektywy)
- [~] E5.1.2 Dark mode — POMINIĘTE świadomie (dyrektywa użytkownika: „nie rób dark mode, wszystko zgodnie z design system adam", light-only)
- [x] E5.1.3 Mock danych admina (SENIORS 1247, AGENTS 12, ORDERS, PARTNERS 80, DEVICES 941, ENV 78…)

### 5.2 Sekcja OVERVIEW (8 ekranów)
- [x] E5.2.1 Dashboard (metryki systemowe + seniorzy z alertami)
- [x] E5.2.2 Seniorzy (lista 1247 + filtry + paginacja)
- [x] E5.2.3 Senior detail (DETAIL_RENDERERS.senior)
- [x] E5.2.4 Call History (18.4K, tabela + filtry + wyszukiwanie transkryptów)
- [x] E5.2.5 Call Scheduling (4 kampanie + heatmap 24×7)
- [x] E5.2.6 Alerty (aktywne + escalation ladder + historia)
- [x] E5.2.7 Marketplace 4 taby (Zamówienia/Katalog/Partnerzy/Service Gaps) ← NOWE
- [x] E5.2.8 Setup Wizard (5 kroków)

### 5.3 Sekcja CORE CONFIG (9 ekranów)
- [x] E5.3.1 Agenci (12) + detail (7 tabów: Prompt YAML/Tools/Voice/Guardrails/A-B/Metryki/Deploy)
- [x] E5.3.2 Providers (7 kart + edit)
- [x] E5.3.3 Pipelines (4 STT→LLM→TTS routing)
- [x] E5.3.4 Contexts (legacy + migracja banner)
- [x] E5.3.5 Audio Profiles (3 + skuteczność F13)
- [x] E5.3.6 Tools (47, 4 fazy)
- [x] E5.3.7 MCP Servers (3 + katalog 6)
- [x] E5.3.8 Wearables Fleet (4 providery + tabela 941 + detail z audit trail) ← NOWE

### 5.4 Sekcja SYSTEM (6 ekranów)
- [x] E5.4.1 Environment (78 vars + kategorie + modified badge)
- [x] E5.4.2 Docker Services (4 kontenery + Images + Volumes)
- [x] E5.4.3 Asterisk (ARI status + moduły + dialplan)
- [x] E5.4.4 Models (STT/TTS/LLM catalog)
- [x] E5.4.5 Live Logs (Troubleshoot/Raw + streaming mock)
- [x] E5.4.6 Terminal (Web CLI `adam ...`)

### 5.5 Domknięcie
- [x] E5.5.1 Routing 23 ekranów + RBAC (permission panel:admin)
- [~] E5.5.2 localStorage persistence sidebar (theme pominięty — light-only)
- [x] E5.5.3 Build + weryfikacja + commit/push

---

## ETAP 6 — PWA ✅
- [x] E6.1 vite-plugin-pwa + manifest („Adam — Panel Opiekuna", theme #1a2744, start_url /panel, standalone, ikony 192/512/maskable + apple-touch)
- [x] E6.2 Service Worker (Workbox generateSW, autoUpdate): precache 15 wpisów + CacheFirst Google Fonts + navigateFallback /index.html
- [x] E6.3 InstallPrompt (banner A2HS beforeinstallprompt + localStorage dismiss) + toast aktualizacji SW + offline-ready (light, wg Adam DS)
- [x] E6.4 Ikony brandowe wygenerowane (granat + złoty monogram A) + iOS meta tags + build weryfikacja (manifest.webmanifest + sw.js OK) + commit/push

---

## ETAP 7 — Capacitor iOS+Android ✅ (kod tu, build u SilverTech)
- [x] E7.1 capacitor.config.ts (appId pl.silvertech.adam.caregiver, appName Adam, webDir dist, splash granat/złoto)
- [x] E7.2 Platformy ios/ + android/ dodane (npx cap add) — struktura wersjonowana, artefakty w .gitignore
- [x] E7.3 Wtyczki: push-notifications, local-notifications, splash-screen, share, capacitor-native-biometric (Face ID/Touch ID/odcisk)
- [x] E7.4 Warstwa natywna src/lib/native/: NotificationService (kanał krytyczny RED/PURPLE + push), BiometricGate (Face ID), initNativeShell (no-op w web)
- [x] E7.5 Splash #1a2744 + spinner złoto, kanały powiadomień + placeholdery APNs/FCM udokumentowane
- [x] E7.6 docs/CAPACITOR-BUILD.md (instrukcja .ipa/.aab, Critical Alerts entitlement, placeholdery kluczy) + commit/push

---

## ETAP 8+ — Backend F1–F18 (Python) ✅ (kod tu, uruchomienie = Frankfurt DC)

Struktura: `agent/adam_modules/` (nowy pakiet obok AVA src/), FastAPI-style routery + SQLAlchemy modele + serwisy + Alembic migracje + testy pytest.

### 8.1 F1 — Profile seniorów (fundament) ✅
- [x] E8.1.1 Model Senior (SQLAlchemy 2.0) + PII szyfrowane (PESEL/telefon Fernet AES + blind index)
- [x] E8.1.2 Migracja Alembic 0001_seniors (autogen + upgrade zweryfikowany)
- [x] E8.1.3 SeniorService CRUD + Pydantic schemas (walidacja PESEL/telefon, maskowanie PII w SeniorOut)
- [x] E8.1.4 FieldCipher (Fernet + blind index) + 13 testów pytest (100% pass)

### 8.2 F2 — Scheduler welfare-check ✅
- [x] E8.2.1 Modele Campaign + CallAttempt (CampaignKind, CallStatus, retry config) + migracja 0002
- [x] E8.2.2 WelfareScheduler (APScheduler cron per kampania, Europe/Warsaw) + AriOriginator wrapper (NullOriginator do testów)
- [x] E8.2.3 run_with_retries (3×/20s, każda próba osobny rekord audytu, exhausted→eskalacja) + SchedulerService + 7 testów

### 8.3 F3+F4+F5 — Semafor + Guardrails + System Prompt (bezpieczeństwo razem) ✅
- [x] E8.3.1 SemaphoreEngine (TRIGGERS→level, state machine) + tabela semaphore_events (migracja 0003)
- [x] E8.3.2 EscalationLadder (RED: retry→SMS→koordynator→PURPLE→112) + timery (offsety)
- [x] E8.3.3 Guardrails (walidacja klasyfikacji, anty-halucynacja)
- [x] E8.3.4 System Prompt Adama + AI Act disclosure (przedstawia się jako AI)
- [x] E8.3.5 Testy jednostkowe wszystkich triggerów + progów (26 testów, 46 total ✅)

### 8.4 F6 — Medication tracker ✅
- [x] E8.4.1 Modele medications + medication_schedules + dose_logs + MedGuard flag (migracja 0004)
- [x] E8.4.2 Serwis harmonogramu (days_mask) + generowanie dawek + sweep_missed + liczenie adherence + 11 testów

### 8.5 F7 — Pamięć semantyczna (RAG rozmów) ✅
- [x] E8.5.1 MemoryChunk (embedding JSON) + pluggable Embedder + context injection do promptu (F5) (migracja 0005)
- [x] E8.5.2 retrieve() (cosine top-k, filtr kind, scope per senior) + build_context() + forget_senior (RODO) + 13 testów

### 8.6 F8 — Crisis detection ✅
- [x] E8.6.1 CrisisDetector: 15 triggerów z fraz PL + vitals (HR/SpO2/BP) → mapowanie na semafor + to_classification (przez Guardrails)
- [x] E8.6.2 Testy scenariuszy kryzysowych (12 testów, integracja z Guardrails)

### 8.7 F9 — Dashboard rodzinny + notyfikacje ✅
- [x] E8.7.1 FamilyMember + adaptery SMS/email/push (pluggable) + feed() dla SSE /api/events
- [x] E8.7.2 Digest yellow / immediate red / bypass-DND purple + logika DND (role krytyczne) + 9 testów

### 8.8 F10 — Wearables ✅
- [x] E8.8.1 Adaptery: Xiaomi Zepp / Apple HealthKit / Garmin / Fitbit (normalizacja do wspólnego formatu)
- [x] E8.8.2 Threshold engine (auto DEFAULT + manual override) + audit SHA-256 (verify_integrity) + 9 testów

### 8.9 F11 — Marketplace ✅
- [x] E8.9.1 Partner/Service/Order + 10 kategorii + OC_REQUIRED (anty-fraud) + fraud_flags→suspend
- [x] E8.9.2 Zamówienia + okno anulowania 30min + weryfikacja NIP (suma kontrolna)/OC + 15 testów

### 8.10 F12 — RODO ✅
- [x] E8.10.1 Retencja (nagrania 30d/transkrypty 365d/raporty 730d) + soft-delete + DataProcessingLog (art.30)
- [x] E8.10.2 Export danych (art.15/20) + prawo do zapomnienia (art.17, erase cross-module + anonimizacja) + 8 testów

### 8.11 F13–F18 ✅
- [x] E8.11.1 F13 AI Act compliance (SYSTEM_REGISTER + DisclosureLog, migracja 0007, 5 testów)
- [x] E8.11.2 F14 Optymalizacja mowy senioralnej (build_speech_profile: niedosłuch/tempo/wiek → parametry TTS, 6 testów)
- [x] E8.11.3 F15 QA (QAEvaluator: score 0-100 + flagi + needs_human_review, 6 testów)
- [x] E8.11.4 F16 Multi-model consensus (fail-safe: wyższy poziom przy rozbieżności, MIN 2 źródła dla krytycznych, 6 testów)
- [x] E8.11.5 F17 Integracja 112 (EmergencyService: payload adres/wiek/leki/vitals + dispatch_summary, 5 testów)
- [x] E8.11.6 F18 Testy E2E (pełny flow kryzys→112, rutyna, state machine, 3 testy) — 154 testy total

### 8.12 Domknięcie backendu ✅
- [x] E8.12.1 requirements.txt modułów (F1–F18: rdzeń + prod PG/Redis + adaptery opcjonalne)
- [x] E8.12.2 docs/BACKEND-DEPLOY.md (Frankfurt DC, Asterisk ARI, PostgreSQL, Redis, docker-compose, adaptery prod)

---

## ETAP 9 — Warstwa API (FastAPI) ✅ (kod tu, uruchomienie = Frankfurt DC)

Warstwa `adam_modules/api` wystawia funkcje F1–F18 przez REST/JSON, by frontend
(panel opiekuna/admina) mógł połączyć się z prawdziwym backendem zamiast mocka.

### 9.1 Szkielet aplikacji ✅
- [x] E9.1.1 Fabryka `create_app()` + `app` (FastAPI, tytuł/opis/wersja, OpenAPI `/docs`)
- [x] E9.1.2 DI sesji per-request (`deps.get_db`, commit/rollback) + guard `X-API-Key` (`require_api_key`)
- [x] E9.1.3 CORS (ADAM_CORS_ORIGINS) + handler `ValueError`→422 + `/health`, `/`
- [x] E9.1.4 SQLite in-memory: `StaticPool` w `common/db.py` (współdzielone połączenie dla wielu sesji)

### 9.2 Router seniorów (F1) ✅
- [x] E9.2.1 CRUD (`GET/POST/PATCH/DELETE`) + lista/paginacja + by-external + maskowanie PII

### 9.3 Router bezpieczeństwa (F3/F4/F8) ✅
- [x] E9.3.1 `/analyze` (detekcja tekst+vitals → klasyfikacja → guardrails → plan eskalacji, opcj. apply)
- [x] E9.3.2 `/resolve` + `/history`

### 9.4 Routery leki (F6) + wearables (F10) ✅
- [x] E9.4.1 Leki: lista/dodawanie + adherence
- [x] E9.4.2 Wearables: urządzenia + ingest (audyt SHA-256) + latest + breaches

### 9.5 Router rodzina/notyfikacje (F9) ✅
- [x] E9.5.1 Opiekunowie + dispatch wg poziomu + feed + **SSE `/events`**

### 9.6 Routery marketplace (F11) + RODO (F12) ✅
- [x] E9.6.1 Marketplace: katalog + zamówienia + anulowanie (okno 30 min → 422 poza oknem)
- [x] E9.6.2 RODO: export (art.15/20) + soft-delete + erase (art.17) + audit (art.30)

### 9.7 Router compliance (F13/F14/F15/F16/F17) ✅
- [x] E9.7.1 System register + disclosures (AI Act) + QA + consensus + payload 112 + profil mowy

### 9.8 Domknięcie API ✅
- [x] E9.8.1 33 endpointy, OpenAPI zweryfikowany (uvicorn boot + curl /health,/docs)
- [x] E9.8.2 docs/API.md (mapa endpointów, env, bezpieczeństwo) + requirements (fastapi/uvicorn/httpx)
- [x] E9.8.3 23 testy API (TestClient) — **177 testów total** — build/commit/push

---

## Zasada realizacji
Koduję etap po etapie. Po każdym **podetapie** — build/test; po każdym **etapie** — commit + push do
`walerys1003/Adam-2027`. Nie proszę o zgodę między etapami. Statusy `[ ]→[x]` aktualizuję w tym pliku.
