# ADAM-2027 — AUDYT LUK I PLAN ROZBUDOWY
### Ultraszczegółowe porównanie: SPECYFIKACJA ŹRÓDŁOWA (RAG) vs REALNY KOD

> **Metoda audytu:** przeanalizowałem ponownie **wszystkie 13 dokumentów źródłowych**
> z `docs/source-md/` (łącznie ~14 000 linii, zaindeksowane w RAG jako **505 chunków**)
> oraz **cały kod** repozytorium (backend, frontend, testy, migracje). Każda funkcja
> została zweryfikowana „w kodzie", nie z pamięci. Poniżej: co jest zrobione w pełni,
> co częściowo, a czego brakuje względem oryginalnej specyfikacji.
>
> **Data:** 2026-07 · **Weryfikowany commit:** `main` (HEAD) · **Autor:** audyt automatyczny

---

## ⚠️ NAJWAŻNIEJSZE USTALENIE NA WSTĘPIE — rozjazd numeracji F

**To kluczowe dla zrozumienia całego audytu.** Dokumenty źródłowe i mój kod używają
**różnej numeracji funkcji F**. W trakcie implementacji doszło do przenumerowania,
przez co „F14" w kodzie znaczy co innego niż „F14" w specyfikacji. Oto mapowanie:

| Nr | Specyfikacja źródłowa (dokumenty) | Mój kod (`adam_modules/`) |
|----|-----------------------------------|---------------------------|
| F0–F5 | Analiza AVA, Profile, Scheduler, Semafor, Guardrails, Prompt | `seniors`, `scheduler`, `semaphore`, `guardrails`, `prompt` ✅ |
| F6 | Medication Tracker | `medication/` ✅ |
| F7 | Vector Memory (RAG/semantyczna) | `memory/` ⚠️ (uproszczona) |
| F8 | Crisis Detection | `semaphore/detector.py` ✅ |
| F9 | Family Dashboard | `family/` ✅ |
| F10 | Wearables | `wearables/` ✅ |
| F11 | Marketplace | `marketplace/` ✅ |
| F12 | RODO / AI Act (Consent Manager, Right-to-Forget) | `rodo/` + `compliance/` ⚠️ |
| **F13 (spec)** | **Senior Speech Adaptation** (DSP audio + słownik 380 terminów) | `speech/profile.py` ❌ **tylko namiastka** |
| **F14 (spec)** | **Multi-Model Consensus** (5 voterów, 4 decyzje) | `consensus/` ⚠️ **uproszczony** |
| **F15 (spec)** | **112 Emergency Calling** (+ emergency_audio, dialplan) | `emergency/payload.py` ⚠️ **bez audio/dialplan** |
| **F16 (spec)** | **Quality Assurance** (quality + manual_audit + improvement_loop, 3 tabele) | `qa/metrics.py` ⚠️ **tylko scoring** |
| **F17 (spec)** | **Integration/Stress Tests** (senior_simulator, manipulacja, halucynacja) | `tests/` ⚠️ **brak stress-suite** |
| **F18 (spec)** | Dokumentacja + Deploy | `docs/` + deploy ✅ |

> **Wniosek:** funkcje „polish + QA" ze specyfikacji (F13–F17 wg dokumentów) są
> zaimplementowane **w formie uproszczonej** lub **częściowo**. To główny obszar luk.
> Nazwałem w kodzie niektóre z nich innymi numerami (np. mój „F16 konsensus" = spec „F14"),
> co maskowało brakujące elementy. Ten audyt prostuje obraz.

---

## 0. STRESZCZENIE ZARZĄDCZE — realny stan

### Ogólna gotowość kodu: **~78%** (nie 89% — po uwzględnieniu luk F13–F17 spec)

| Warstwa | % ukończenia | Ocena |
|---|---|---|
| **Backend (logika F1–F12)** | **90%** | Kompletny rdzeń senior-care; drobne uproszczenia w F7/F12 |
| **Backend (F13–F17 spec: audio/consensus/112/QA/stress)** | **45%** | Główny obszar luk — namiastki zamiast pełnych modułów |
| **API (REST)** | **88%** | 51 endpointów; brak części dla QA/audio/emergency-audio |
| **Baza danych** | **80%** | 18 tabel; brakuje tabel QA (3), emergency_calls, sentiment |
| **Frontend (UI)** | **95%** | Wszystkie ekrany panelu (8/8) + admin (~25); light-only |
| **Frontend (integracja z żywym API)** | **60%** | Auth+seniorzy+konto na żywo; reszta na mocku/heurystyce |
| **Integracje realne (AI/telefonia/powiadomienia)** | **40%** | Adaptery gotowe, brak kluczy/infra + realnego audio DSP |
| **Warstwa głosowa (produkcyjna, pełna)** | **55%** | Dialog/detektor OK; brak preprocessingu audio + multi-STT |
| **Mobile (Capacitor)** | **80%** | Kod gotowy; brak realnego buildu/publikacji |
| **CI/CD** | **50%** | Workflow gotowy, nieaktywny (brak uprawnienia `workflows`) |
| **Testy** | **75%** | 295 backend + 29 frontend; brak stress/e2e wg spec |

**Skrót:** *rdzeń opieki (F1–F12) jest solidny i produkcyjny. Warstwa „dopieszczenia
i bezpieczeństwa krytycznego" (F13–F17 wg specyfikacji) — audio senioralne, pełny
konsensus 5-głosowy, realne 112 z audio, pętla poprawy jakości, testy odpornościowe —
jest zaimplementowana pobieżnie i wymaga rozbudowy.*

---

## 1. ANALIZA FUNKCJA-PO-FUNKCJI (spec vs kod)

Dla każdej funkcji: **co mówiła specyfikacja**, **co jest w kodzie**, **czego brakuje**.

### ✅ F1 — Profile seniorów + szyfrowanie PII — **95% (KOMPLETNE)**
- **Spec:** baza profili, szyfrowanie PII (AES-256), maskowanie w odpowiedziach.
- **Kod:** `seniors/models.py` + `common/crypto.py` (Fernet + blind index), maskowanie
  w `SeniorOut.from_model`. 13 testów.
- **Braki:** drobne — brak pól typu „adres do 112 w ustrukturyzowanej formie" (jest
  w payloadzie, ale nie jako osobne, walidowane pola geolokalizacyjne).

### ✅ F2 — Scheduler welfare-check — **90% (KOMPLETNE)**
- **Spec:** kontener `adam_scheduler`, APScheduler, sprawdzanie co 60 s tabeli
  `call_schedules`, retry wg `max_retries`/`retry_interval`, aktualizacja
  `next_call_at`/`last_called_at`.
- **Kod:** `scheduler/service.py` — logika kampanii, `run_with_retries`, statusy,
  `CallAttempt`. 7 testów.
- **Braki:** ⚠️ **logika jest, ale nie działa jako żywy proces (cron/APScheduler
  daemon)** — brak realnego „co 60 s". W produkcji trzeba uruchomić APScheduler
  lub systemowy cron wołający tę logikę. To warstwa runtime/infra, nie kod domenowy.

### ✅ F3 — Semafor bezpieczeństwa — **100% (WZORCOWE)**
- **Spec:** 4 poziomy, state-machine (nie gaśnie sam), drabina eskalacji, zapis zdarzeń.
- **Kod:** `semaphore/engine.py` + `escalation.py` — wszystko zgodnie, max_level,
  `allow_downgrade=False`, `SemaphoreEvent`, drabiny RED/PURPLE z offsetami czasowymi.
  20 testów. **Najlepiej wykonany moduł.**
- **Braki:** brak — poza tym, że wykonanie kroków drabiny (timery) wymaga runtime.

### ⚠️ F4 — Guardrails — **60% (ISTOTNA LUKA)**
- **Spec:** guardrails PRE-LLM (walidacja WEJŚCIA seniora — blokada prompt-injection,
  „ignoruj instrukcje", „udawaj lekarza", tematy poza zakresem: polityka/religia)
  ORAZ POST-LLM (blokada porad medycznych, zmian dawek, obietnic, halucynacji).
- **Kod:** `semaphore/guardrails.py` — **tylko walidacja klasyfikacji** (czy PURPLE
  ma twardy sygnał). Zasady „nie udawaj lekarza / nie diagnozuj" istnieją **wyłącznie
  w treści system-promptu** (miękko), nie jako twardy filtr wejścia/wyjścia.
- **BRAKI (do dorobienia):**
  - ❌ **Pre-LLM input guard** — wykrywanie i neutralizacja prób manipulacji
    (prompt-injection, jailbreak, „zignoruj zasady").
  - ❌ **Post-LLM output guard** — skan odpowiedzi Adama pod kątem zakazanych fraz
    („to może być", „prawdopodobnie masz", nazwy leków z sugestią dawki, obietnice).
  - ❌ **Out-of-scope handler** — grzeczne odbicie pytań o politykę/religię/diagnozy
    z powrotem do tematu samopoczucia.

### ✅ F5 — System Prompt Adama — **95% (KOMPLETNE)**
- **Spec:** dynamiczny prompt PL, tożsamość AI, zasady rozmowy, ujawnienie art. 50.
- **Kod:** `semaphore/prompt.py` — pełny, z wstrzykiwaniem imienia/wieku/profilu mowy.
- **Braki:** brak placeholderów `{today}`/`{current_date}` (były w AVA); brak wariantów
  promptu per typ kampanii (poranny/wieczorny welfare-check).

### ✅ F6 — Medication Tracker — **90% (KOMPLETNE)**
- **Spec:** leki, harmonogramy, dose_logs, raport adherence, przypomnienia w rozmowie.
- **Kod:** `medication/` — 3 tabele (medications, schedules, dose_logs), raport
  adherence, 11 testów.
- **Braki:** ⚠️ **przypomnienia o lekach nie są wplecione w DialogEngine** — tracker
  liczy adherence, ale Adam podczas rozmowy nie mówi automatycznie „czas na tabletkę
  na ciśnienie". Trzeba połączyć harmonogram z torem rozmowy.

### ⚠️ F7 — Pamięć semantyczna (Vector Memory) — **55% (UPROSZCZONA)**
- **Spec:** `memory_engine.py`, prawdziwa pamięć wektorowa (RAG/embeddingi),
  kontekst wcześniejszych rozmów wstrzykiwany do LLM, wyszukiwanie po znaczeniu.
- **Kod:** `memory/` — model `memory_chunks` + `embedder.py`, ale embedding jest
  **uproszczony/lokalny**, a pamięć **nie jest realnie podpięta do DialogEngine**
  (Adam nie „pamięta" poprzednich rozmów w czasie połączenia).
- **BRAKI:**
  - ❌ Realny store wektorowy (pgvector / Qdrant / Chroma) w produkcji.
  - ❌ Wstrzykiwanie kontekstu pamięci do promptu przy kolejnych rozmowach.
  - ❌ Podsumowania rozmów zapisywane po każdym połączeniu.

### ✅ F8 — Crisis Detection — **85% (DOBRE)**
- **Spec:** detektor kryzysu z tekstu + wearables, słowniki fraz, twarde sygnały.
- **Kod:** `semaphore/detector.py` — bogate słowniki PL, detekcja vitals, 12 testów.
- **Braki:** ⚠️ słowniki są solidne, ale **nie pokrywają regionalizmów wielkopolskich**
  (spec wymagał 380 terminów + regionalizmy); brak warstwy LLM-owej detekcji niuansów
  (jest w konsensusie, ale uproszczona).

### ✅ F9 — Family Dashboard + powiadomienia — **90% (KOMPLETNE)**
- **Spec:** członkowie rodziny, role, kanały (SMS/e-mail/push), fan-out wg poziomu,
  tryby (digest/immediate/bypass-DND), feed, SSE live.
- **Kod:** `family/` — pełne modele + `adapters.py` (Twilio/SendGrid/FCM, fail-safe),
  endpoint SSE `events`. 9 testów.
- **Braki:** adaptery `live` niesprawdzone z realnymi kluczami (brak kont).

### ✅ F10 — Wearables — **90% (KOMPLETNE)**
- **Spec:** urządzenia (Xiaomi/Apple/Garmin/Fitbit), odczyty, progi, fuzja sygnałów.
- **Kod:** `wearables/` — 3 tabele, `adapters.py`, progi vital, 9 testów.
- **Braki:** ⚠️ **fuzja sygnałów wearable→konsensus jest teoretyczna** — WearableVoter
  ze spec (5. głos konsensusu) nie istnieje; brak realnych integracji API producentów.

### ✅ F11 — Marketplace — **95% (KOMPLETNE)**
- **Spec:** katalog usług, partnerzy, zamówienia, okno anulowania.
- **Kod:** `marketplace/` — 3 tabele, okno anulowania 30 min, 12 testów. Solidne.
- **Braki:** brak realnej integracji płatności (Stripe/PayPre) — ale spec tego nie
  wymagał w MVP.

### ⚠️ F12 — RODO / AI Act — **75% (DOBRE, ale niepełne)**
- **Spec:** Consent Manager (`consent_manager.py`), Right-to-Forget
  (`right_to_forget.py`), AI Act compliance (`ai_act_compliance.py`), DPIA,
  okresy retencji, rejestr czynności.
- **Kod:** `rodo/` (eksport, soft-delete, erase, audyt) + `compliance/` (rejestr AI,
  disclosure_logs). 8+5 testów.
- **BRAKI:**
  - ❌ **Consent Manager** jako osobny moduł (zgody: nagrywanie, przetwarzanie,
    marketing) — spec wymagał bramki zgody (consent gate) przed rozmową.
  - ❌ **Automatyczna retencja** (auto-usuwanie nagrań po 30 dniach) — zdefiniowana
    w polityce, brak mechanizmu wykonawczego.
  - ⚠️ DPIA i pełna dokumentacja RODO — jest szkic w `docs`, brak formalnego dokumentu.

---

## 2. OBSZAR GŁÓWNYCH LUK — F13–F17 wg specyfikacji (Polish + QA)

To najważniejsza część audytu. Te funkcje ze specyfikacji są **zaimplementowane
częściowo lub jako namiastka**. Tu leży większość brakujących ~22%.

### ❌ F13 (spec) — Senior Speech Adaptation — **30% (POWAŻNA LUKA)**
- **Spec (bardzo szczegółowa):**
  - `SeniorAudioPreprocessor` — pipeline DSP PRZED STT: noise gate, AGC (-16 LUFS),
    pre-emphasis, denoise, dereverb.
  - `adaptive_vad` — dynamiczny próg ciszy (senior mówi wolniej: 95–115 słów/min;
    standardowy VAD ucina zdanie — próg 800 ms → 1800 ms).
  - `SeniorAudioPostprocessor` — obróbka po STT.
  - `speech_calibrator.py` — kalibracja parametrów pod konkretnego seniora.
  - `vocabulary_wielkopolska.txt` — **380 terminów**: ~180 regionalizmów wielkopolskich
    (tej, ino, pyrki, tytka…) + ~200 nazw handlowych leków PL.
- **Kod:** `speech/profile.py` — **tylko** deterministyczne wyliczenie parametrów TTS
  (tempo WPM, głośność dB) na podstawie poziomu słuchu/tempa. 6 testów.
- **BRAKI (do dorobienia):**
  - ❌ Cały pipeline DSP audio (noise gate/AGC/denoise/dereverb) — **nie istnieje**.
  - ❌ Adaptacyjny VAD — nie istnieje.
  - ❌ Słownik 380 terminów (regionalizmy + leki) — **nie istnieje**.
  - ❌ Post-processor STT i kalibrator mowy — nie istnieją.
- **Uwaga:** to warstwa audio niskopoziomowa; wymaga bibliotek DSP i realnego strumienia
  audio z Asteriska. Część można zrobić teraz (słownik, VAD-config), część dopiero
  na infra z realnym audio.

### ⚠️ F14 (spec) — Multi-Model Consensus — **55% (UPROSZCZONY)**
- **Spec:**
  - **5 voterów:** WhisperSafetyVoter, DeepgramSafetyVoter, LLMSafetyVoter,
    SentimentVoter (4. opcjonalny), WearableVoter (5. opcjonalny).
  - **4 decyzje:** `EXECUTE` / `DEFER` / `ESCALATE` / `ABSTAIN`.
  - **Matryca konsensusu:** 3/3→EXECUTE, 2/3→ESCALATE (lub EXECUTE gdy conf>0.9),
    1/3→DEFER, 0/3→ABSTAIN. Osobne progi dla PURPLE (call_112).
  - `human_override_required`, `dissenting_models`, `CriticalContext`.
- **Kod:** `consensus/engine.py` + `voice/consensus.py` — **tylko 2 głosy**
  (detektor regułowy + jeden LLM), zwraca poziom + `needs_review`, bez 4-stanowej
  matrycy decyzyjnej. 6 testów.
- **BRAKI:**
  - ❌ Voterzy: Deepgram (2. STT), Sentiment, Wearable — **brak** (jest tylko 1 STT + 1 LLM).
  - ❌ Decyzje EXECUTE/DEFER/ESCALATE/ABSTAIN — mam tylko „poziom + needs_review".
  - ❌ Matryca progów per PURPLE/RED (3/3 auto-112 vs 2/3 manual).
  - ❌ `human_override_required`, dwutorowa transkrypcja (dual-STT cross-check).

### ⚠️ F15 (spec) — 112 Emergency Calling — **50% (BEZ AUDIO/DIALPLAN)**
- **Spec:**
  - `emergency_service.py` — payload 112 ✅ (mam).
  - `emergency_audio.py` — **wygenerowany komunikat głosowy dla dyspozytora 112**
    (TTS: „Wzywam pomoc dla seniora, adres…, wiek…, leki…"). ❌ brak.
  - Tabela `emergency_calls` — rejestr zgłoszeń 112. ❌ brak.
  - Dialplan Asterisk do faktycznego wybrania 112. ❌ brak.
- **Kod:** `emergency/payload.py` — `EmergencyService.build_payload` (adres, wiek,
  leki, vitals) + `dispatch_summary`. 5 testów.
- **BRAKI:**
  - ❌ Generowanie komunikatu audio dla służb (emergency_audio).
  - ❌ Tabela/rejestr `emergency_calls` (audyt zgłoszeń).
  - ❌ Realny dialplan/originate do 112 przez Asterisk.

### ⚠️ F16 (spec) — Quality Assurance — **40% (TYLKO SCORING)**
- **Spec:**
  - `quality_engine.py` — automatyczna ocena rozmów (score) ✅ (mam namiastkę).
  - `manual_audit.py` — interfejs ręcznego audytu rozmów przez człowieka. ❌ brak.
  - `improvement_loop.py` — **pętla poprawy**: analiza słabych rozmów → rekomendacje
    zmian promptu/reguł. ❌ brak.
  - **3 tabele QA** (oceny, audyty, rekomendacje). ❌ brak (mam scoring w pamięci).
- **Kod:** `qa/metrics.py` — `QAEvaluator.evaluate` (score 0–100 + flagi) +
  `needs_human_review`. 6 testów.
- **BRAKI:**
  - ❌ Trwałe tabele QA + endpointy zapisu/przeglądu ocen.
  - ❌ Manualny audyt (panel admina + backend).
  - ❌ Improvement loop (analiza trendów jakości, rekomendacje).

### ⚠️ F17 (spec) — Integration + Stress Tests — **50% (BRAK STRESS-SUITE)**
- **Spec:**
  - `tests/integration/test_welfare_check_flow.py`, `test_crisis_escalation.py` —
    ⚠️ mam odpowiedniki e2e (`test_e2e.py`, `test_e2e_flow.py`), ale uboższe.
  - `tests/stress/test_manipulation_attempts.py` — próby manipulacji (ignoruj
    instrukcje, udawaj lekarza, polityka, religia). ❌ **brak**.
  - `tests/stress/test_medical_hallucination.py` — blokada diagnoz/zmian dawek. ❌ **brak**.
  - `senior_simulator.py` — symulator seniora do testów. ❌ brak.
- **Kod:** 295 testów jednostkowych/integracyjnych (bardzo dobre pokrycie modułów),
  ale **brak dedykowanej suity odpornościowej (stress/adversarial)**.
- **BRAKI:**
  - ❌ Testy prompt-injection / jailbreak / manipulacji.
  - ❌ Testy anty-halucynacji medycznej.
  - ❌ Symulator seniora (generator realistycznych wypowiedzi).

### ✅ F18 (spec) — Dokumentacja + Deploy — **85% (DOBRE)**
- **Kod:** bogata dokumentacja (`docs/`: API, AUDIT, MASTER-PLAN, ROADMAP,
  DEPLOY-CHECKLIST, AUDYT-PELNY), runbooki deploy, CLI deploy częściowo.
- **Braki:** brak diagramów architektury, część 28 dokumentów ze spec nie powstała.

---

## 3. FUNKCJE BAZOWE AVA — co przeniesione, co pominięte

Specyfikacja zakładała bazę na **AVA v7.3.2**. Warto sprawdzić, które funkcje AVA
faktycznie żyją w naszym kodzie, a które zostały pominięte (bo nasza logika jest
napisana od zera w `adam_modules`, niekoniecznie korzystając z całego AVA).

| Funkcja AVA | Potrzebna Adamowi? | Stan w naszym kodzie |
|---|---|---|
| Asterisk/ARI (telefonia) | ✅ krytyczna | ⚠️ adapter `voice/asterisk.py` + `stasis.py` — szkielet, bez realnego audio |
| 7 „złotych" konfiguracji AI | częściowo | ❌ mamy tylko OpenAI (Whisper/GPT/TTS) + ElevenLabs; brak Deepgram/Google/Grok/local |
| Modularne pipeline STT/LLM/TTS | ✅ | ⚠️ mamy porty (wymienne), ale 1 dostawca per rola |
| Multi-STT (dual transcription) | ✅ (dla konsensusu) | ❌ brak (spec chciał Whisper + Deepgram cross-check) |
| Barge-in (przerywanie agenta) | ✅ ważne dla seniorów | ❌ brak |
| Silence Watchdog (30 s → „Halo?") | ✅ ważne | ❌ brak (senior milczy → system nie reaguje) |
| Call Recordings + odtwarzanie | ✅ (audyt, QA) | ❌ brak nagrywania/odtwarzania |
| Filler audio („chwileczkę") | ⚠️ miłe | ❌ brak |
| Tool-calling (transfer, hangup, email) | częściowo | ⚠️ eskalacja jest, ale nie jako AVA-tools |
| Admin UI (YAML editor, live logs, topology) | ⚠️ | ⚠️ mamy własny Panel Admina (React), inny niż AVA |
| Prometheus /metrics + /health | ✅ | ✅ mamy (`/metrics`, `/health/*`) |
| SSE live-status | ✅ | ✅ mamy (`family/events`) |
| Docker Compose (ai_engine + admin_ui) | ✅ | ⚠️ mamy pliki deploy, ale nie pełną orkiestrację AVA |

**Wniosek:** zbudowaliśmy **własny, czysty rdzeń domenowy** zamiast rozbudowywać AVA
w miejscu. To dobra decyzja architektoniczna (testowalność, czystość), ale oznacza,
że **kilka dojrzałych funkcji AVA trzeba świadomie odtworzyć**: Silence Watchdog,
barge-in, nagrywanie rozmów, dual-STT, filler audio.

---

## 4. WARSTWA FRONTEND — szczegółowy stan

### UI: 95% — praktycznie kompletny
- **Panel Opiekuna:** wszystkie **8/8 ekranów** wg `SCREENS-MAP.md` (Dashboard,
  Senior, Zamówienia, Wiadomości, Raporty, Konto, Ustawienia, Pomoc). ✅
- **Panel Admina:** ~**25 ekranów** (Dashboard, Agents, Fleet, Models, Providers,
  Calls, Asterisk, Docker, Logs, Terminal, MCP, Pipelines, Scheduling, Marketplace,
  Alerts, Environment, Contexts, Audio, Tools, Wizard, Seniors + detale). ✅
- **Landing Page:** pełna (Hero, Problem, HowItWorks, Features, Pricing, Testimonial,
  Partners, CTA). ✅
- **Design System:** light-only zgodnie z dyrektywą, komponenty UI (Badge, Card,
  SemaphoreBadge, Sparkline, RadialGauge, Timeline, Heatmap…). ✅
- **PWA + Capacitor:** InstallPrompt, BiometricGate, NotificationService. ✅

### Integracja z żywym API: 60% — częściowa
- ✅ **Na żywo:** logowanie (login/refresh/me), seniorzy, szczegóły, zamówienia,
  wiadomości/wątki, faktury, sesje.
- ⚠️ **Heurystyka zamiast realnych danych:** wykres **nastroju** jest wyliczany
  z poziomu semafora (`moodFromSemaphore`), a nie z realnej analizy sentymentu —
  bo backend nie ma modułu sentymentu/mood-tracking.
- ⚠️ **Na mocku:** większość ekranów **Panelu Admina** działa na danych-atrapach
  (`mockAdmin.ts`) — nie ma backendu dla floty agentów, modeli, providerów, Dockera,
  logów, terminala (to w dużej mierze funkcje AVA Admin UI, których nie odtworzyliśmy
  po stronie API).
- ❌ **Brak realnego API dla:** raportów (Reports), ustawień (Settings persist),
  większości akcji admina.

**Wniosek frontend:** interfejs wygląda na „gotowy w 95%", ale **realnie zasilany
danymi jest w ~60%**. Panel Admina to w dużej części piękna makieta bez backendu.

---

## 5. WARSTWA API — szczegółowy stan (88%)

- ✅ **51 endpointów, 12 routerów** — pełne pokrycie F1–F12 + auth + account + voice.
- ❌ **Brak endpointów dla:**
  - QA (zapis ocen, manualny audyt, rekomendacje) — F16 spec.
  - Emergency calls (rejestr zgłoszeń 112) — F15 spec.
  - Consent management (zgody RODO) — F12 spec.
  - Sentiment/mood tracking (realny nastrój) — potrzebny dla wykresów.
  - Panel Admina: flota, modele, providerzy, logi, scheduling-config.
- ✅ Middleware, healthchecki, metryki, rate-limit, CORS, security headers — kompletne.

---

## 6. WARSTWA BAZY DANYCH — szczegółowy stan (80%)

- ✅ **18 tabel, 7 migracji** (0001–0007) — pełne dla F1–F12.
- ❌ **Brakujące tabele wg specyfikacji:**
  - `emergency_calls` (rejestr zgłoszeń 112) — F15.
  - 3 tabele QA (oceny / audyty / rekomendacje) — F16.
  - `consents` (zgody RODO/consent gate) — F12.
  - `conversation_summaries` / realny store wektorowy — F7.
  - `sentiment_readings` / mood — dla realnego wykresu nastroju.
- ⚠️ `memory_chunks` istnieje, ale bez realnego indeksu wektorowego (pgvector).

---

## 7. INTEGRACJE (AI / TELEFONIA / POWIADOMIENIA / URZĄDZENIA) — szczegółowy stan (~40%)

Integracje są **zaprojektowane jako porty z adapterami fail-safe**, ale w większości mają
tylko implementacje deweloperskie (Null/Memory/stub). To świadoma decyzja architektoniczna
(system działa bez kluczy), ale do produkcji brakuje realnych adapterów.

### 7.1. Powiadomienia (rodzina/opiekun) — **35%**
- ✅ Port `NotificationAdapter` + `DeliveryResult`, logika `bypass_dnd` (obejście trybu nie-przeszkadzać dla RED/PURPLE).
- ✅ `NullAdapter` (zawsze OK) i `MemoryAdapter` (symulacja, testy).
- ⚠️ `SmsAdapter`/`EmailAdapter` **dziedziczą po MemoryAdapter** — to atrapy, nie realne wysyłki.
- ❌ **Brak realnego providera:** SMS (Twilio/SMSAPI), e-mail (SendGrid/Resend), push (FCM/APNs).
- ❌ Brak kolejki ponowień (retry) i potwierdzeń doręczenia od operatora.

### 7.2. Telefonia (Asterisk/ARI) — **45%**
- ✅ Zmienne środowiskowe ARI/Asterisk w `.env.adam.example` (ETAP 19), port `call-start`.
- ✅ Warstwa AVA (baza) ma pełny stack Asterisk/ARI — dostępny technicznie.
- ❌ **Brak dialplanu 112** i realnego mostkowania połączenia alarmowego (F15).
- ❌ Brak realnego wiązania sesji głosowej Adam ↔ kanał ARI w runtime (jest port, brak pełnego pilota).

### 7.3. AI (ASR / LLM / TTS) — **50%**
- ✅ Porty ASR/LLM/TTS z wariantami dev (deterministyczne atrapy) i prod (miejsca na realnych providerów).
- ✅ Konsensus kryzysowy (rule + 1 LLM) działa na atrapach.
- ❌ **Brak realnie podpiętych providerów prod** (Whisper/Deepgram, OpenAI/Anthropic/lokalny LLM, ElevenLabs/lokalny TTS) — do produkcji trzeba dołożyć konkretne implementacje i klucze.
- ❌ Brak drugiego, niezależnego STT (dual-STT wymagany przez spec F14).

### 7.4. Urządzenia noszone (wearables) — **40%**
- ✅ Port `WearableAdapter` + `NormalizedReading` + 4 adaptery: `XiaomiZeppAdapter`, `AppleHealthAdapter`, `GarminAdapter`, `FitbitAdapter`.
- ✅ Normalizacja odczytów (HR/SpO₂) → wpięcie w `CrisisDetector.detect_vitals`.
- ❌ Adaptery to **stuby** — brak realnego OAuth/API do chmur producentów.
- ❌ Brak pollingu/websocketów odczytów w czasie rzeczywistym.

### 7.5. Marketplace (usługi partnerskie) — **80%** ✅
- ✅ Pełny CRUD: rejestracja partnera, weryfikacja, `flag_fraud`, dodawanie usług, tworzenie/anulowanie/potwierdzanie zamówień, walidacja NIP.
- ⚠️ Brak realnej integracji płatności (Stripe/Przelewy24) i realnego katalogu dostawców.

---

## 8. APLIKACJA MOBILNA (Capacitor iOS/Android) — szczegółowy stan (~80%)

- ✅ `capacitor.config.ts` skonfigurowany: `appId: pl.silvertech.adam.caregiver`, `appName: Adam`, `webDir: dist`, `backgroundColor: #fbfaf7` (spójny z light-only Design System).
- ✅ Katalogi natywne `android/` i `ios/` obecne (projekty wygenerowane).
- ✅ SplashScreen skonfigurowany (1200 ms, auto-hide), `loggingBehavior: production`.
- ✅ `docs/CAPACITOR-BUILD.md` — instrukcja budowy `.ipa`/`.aab` po stronie SilverTech.
- ⚠️ Build natywny (podpisywanie, store) wykonywany poza sandboxem — **niezweryfikowany end-to-end**.
- ❌ Brak natywnych pluginów krytycznych dla seniora: push (FCM/APNs), połączenia telefoniczne w tle, health-kit/Google-Fit (spięcie z wearables).

---

## 9. CI/CD I JAKOŚĆ INŻYNIERSKA — szczegółowy stan (~50%)

**USTALENIE KRYTYCZNE:** istniejące workflow CI (`agent/.github/workflows/`) pochodzą z bazy AVA
i **NIE uruchamiają testów Adama**.

- ✅ Bogaty zestaw workflow AVA: `ci.yml`, `codeql.yml`, `trivy.yml`, `regression-hardening.yml`, `block-dev-artifacts.yml`, `release-*.yml`, `dependabot.yml`.
- ✅ `ci.yml` robi: compileall, skan sekretów, testy `tests/` (suite AVA) + Admin UI backend, coverage.
- ❌ **Żaden workflow nie odwołuje się do `adam_modules`** — 295 testów Adama **nie jest** uruchamiane w CI.
- ❌ **Frontend panelu Adam (vitest, 29 testów) nie jest** w CI (workflow dotyczą Admin UI AVA, nie panelu Adam).
- ❌ Brak workflow buildu/deployu obrazu `adam-api` (Dockerfile istnieje, ale nie jest budowany w CI).
- ❌ Brak bramki „migracje Alembic aplikują się czysto” w CI.

---

## 10. KONKRETNY PLAN ROZBUDOWY (fazy / ETAP-y, priorytety, kolejność zależności)

Plan uwzględnia realny stan kodu i **rozjazd numeracji F**. Priorytety: 🔴 krytyczne dla
bezpieczeństwa/produkcji, 🟡 ważne funkcjonalnie, 🟢 wartość dodana.

### FAZA A — Domknięcie bezpieczeństwa i zgodności (🔴 must-have przed pilotażem)

**ETAP 24 — Guardrails F4 (pełne 3 warstwy).** *(zależność: brak; fundament)*
- Dodać **pre-LLM input guard** (sanityzacja/wykrycie prompt-injection, PII w wejściu) i **post-LLM output guard** (blokada halucynacji medycznych, weryfikacja dawek/nazw leków, zakaz porad diagnostycznych).
- Wpiąć w `DialogEngine` przed i po wywołaniu LLM.
- Testy: manipulacja, „udawaj lekarza”, wyciek danych. Szac. wysiłek: średni.

**ETAP 25 — Consent Manager F12 (bramka zgód RODO).** *(zależność: DB)*
- Tabela `consents`, serwis rejestrujący zgody (nagrywanie, przetwarzanie zdrowotne, kontakt rodziny), endpointy `/api/consents`.
- Bramka: bez ważnej zgody rozmowa nie startuje w trybie prod. Szac. wysiłek: średni.

**ETAP 26 — Emergency 112 F15 (pełny łańcuch).** *(zależność: telefonia ARI, DB)*
- `emergency_audio.py` (komunikat głosowy do dyspozytora), tabela `emergency_calls` (rejestr zgłoszeń), **dialplan 112** + mostkowanie ARI.
- Endpointy `/api/emergency/*` (podgląd/rejestr), spięcie z `EscalationLadder` PURPLE.
- Testy end-to-end eskalacji. Szac. wysiłek: wysoki.

### FAZA B — Domknięcie inteligencji rozmowy (🟡 rdzeń wartości)

**ETAP 27 — Konsensus F14 (5 głosujących + macierz 4-stanowa).** *(zależność: dual-STT, sentiment)*
- Rozszerzyć `ConsensusEngine.decide()` o głosujących: whisper, deepgram (dual-STT), llm_safety, sentiment, wearable.
- Wprowadzić `ConsensusDecision`: **EXECUTE / DEFER / ESCALATE / ABSTAIN** + macierz decyzyjną wg spec.
- Testy zgodności z macierzą. Szac. wysiłek: wysoki.

**ETAP 28 — Pamięć semantyczna F7 (realny store wektorowy).** *(zależność: DB pgvector)*
- Wektorowy store rozmów (pgvector), `conversation_summaries`, retrieval kontekstu do promptu.
- Wpięcie w `DialogEngine` (przypominanie faktów o seniorze). Szac. wysiłek: wysoki.

**ETAP 29 — Senior Audio F13 (DSP + słownik + adaptacyjny VAD).** *(zależność: AI ASR/TTS)*
- `SeniorAudioPreprocessor` (redukcja szumu, kompresja dynamiki, korekcja pod niedosłuch), **adaptive VAD** (dłuższe pauzy), `vocabulary_wielkopolska.txt` (~380 terminów/regionalizmów) + boost w ASR.
- Rozszerzyć `CrisisDetector` o regionalizmy wielkopolskie. Szac. wysiłek: wysoki.

### FAZA C — Jakość, testy i realne integracje (🟡/🟢)

**ETAP 30 — QA Loop F16 (persistencja + audyt + rekomendacje).** *(zależność: DB)*
- 3 tabele QA (oceny / manualny audyt / rekomendacje), `manual_audit`, `improvement_loop`, endpointy `/api/qa/*`, panel audytora.
- Realny nastrój/sentiment (`sentiment_readings`) zamiast heurystyki `moodFromSemaphore`. Szac. wysiłek: średni/wysoki.

**ETAP 31 — Testy integracyjne/stresowe F17.** *(zależność: F4, F14)*
- Suite: `senior_simulator`, `test_manipulation_attempts`, `test_medical_hallucination`, testy obciążeniowe. Szac. wysiłek: średni.

**ETAP 32 — Realne integracje produkcyjne.** *(zależność: klucze/konta)*
- Realny SMS/e-mail/push (Twilio/SendGrid/FCM), realni providerzy ASR/LLM/TTS prod, realny OAuth wearables.
- Kolejka ponowień powiadomień + potwierdzenia doręczenia. Szac. wysiłek: wysoki (zależny od dostawców).

### FAZA D — Funkcje bazowe AVA i operacje (🟢)

**ETAP 33 — Przywrócenie funkcji głosowych AVA.** *(zależność: telefonia)*
- Silence Watchdog, barge-in, nagrania rozmów, filler audio, dual-STT (część z F14). Szac. wysiłek: średni.

**ETAP 34 — CI/CD dla Adama.** *(zależność: brak)*
- Workflow uruchamiający **295 testów `adam_modules`** + **29 testów vitest panelu**, bramka migracji Alembic, build obrazu `adam-api`. Szac. wysiłek: niski/średni.

**ETAP 35 — Panel Admina (backend + realne dane).** *(zależność: powyższe API)*
- Endpointy: flota urządzeń, modele/providerzy, logi, konfiguracja schedulera; podpięcie panelu (dziś w większości mock). Szac. wysiłek: średni.

### Kolejność zależności (skrót)
```
A24 (guardrails) ─┐
A25 (consent)     ├─→ B27 (consensus) ─→ B28 (memory) ─→ B29 (audio)
A26 (112)         ┘        │
                           └─→ C31 (stress) ─→ C30 (QA) ─→ D33 (AVA voice)
C32 (real integr.) niezależny (zależy od kluczy)   D34 (CI) niezależny   D35 (admin) po API
```

---

## 11. REKOMENDACJE KOŃCOWE I PRIORYTETY

1. **🔴 Najpilniejsze (bezpieczeństwo/produkcja):** ETAP 24 (guardrails 3-warstwowe), ETAP 25 (consent gate RODO), ETAP 26 (pełny łańcuch 112). Bez nich system **nie powinien** iść na realnego seniora.
2. **🟡 Rdzeń wartości:** ETAP 27 (konsensus 5-głosowy + macierz 4-stanowa) i ETAP 28 (pamięć semantyczna) — to one czynią Adama „inteligentnym", a nie tylko klasyfikatorem.
3. **🟡 Zaufanie i jakość:** ETAP 29 (senior audio — realny komfort rozmowy), ETAP 30 (QA loop + realny nastrój), ETAP 31 (testy stresowe/manipulacyjne).
4. **🟢 Operacyjne:** ETAP 34 (CI dla Adama — natychmiastowa wartość, niski koszt), ETAP 32 (realne integracje, gdy będą klucze), ETAP 33/35.

### Podsumowanie liczbowe (gotowość realna)
| Warstwa | Gotowość |
|---|---|
| Backend F1–F12 (rdzeń) | **90%** |
| Backend F13–F17 (spec) | **45%** |
| API (endpointy) | **88%** |
| Baza danych | **80%** |
| Frontend UI | **95%** |
| Frontend integracja z API | **60%** |
| Integracje (AI/telefonia/powiadomienia/wearables) | **40%** |
| Warstwa głosowa (pełny łańcuch prod) | **55%** |
| Aplikacja mobilna | **80%** |
| CI/CD | **50%** |
| Testy | **75%** |
| **CAŁOŚĆ (średnia ważona)** | **~78%** |

> **Wniosek:** rdzeń (F1–F12: semafor, dialog, eskalacja, RODO-baza, marketplace, panel) jest
> dojrzały i przetestowany (295 + 29 testów). Luki koncentrują się w **zaawansowanych funkcjach
> spec F13–F17** (senior audio, konsensus 5-głosowy, pełne 112, QA-loop, testy stresowe) oraz w
> **realnych integracjach produkcyjnych**. Intuicja użytkownika była trafna: „nie wszystko zostało
> jeszcze wdrożone" — dotyczy to głównie warstwy zaawansowanej i produkcyjnej, nie fundamentu.

---

*Audyt sporządzony na podstawie: 13 dokumentów źródłowych `docs/source-md/` (~14 000 linii,
505 chunków RAG), pełnej analizy kodu (`agent/adam_modules/`, `frontend/`), schematu OpenAPI
(51 endpointów), 18 tabel/7 migracji, oraz weryfikacji testów (295 backend + 29 frontend).*
