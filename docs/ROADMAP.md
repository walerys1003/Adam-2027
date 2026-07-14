# ADAM-2027 · Roadmapa wdrożeń + krytyczna analiza

> **Cel projektu:** Przekształcenie open-source'owego voice-agenta AVA (v7.3.2, MIT)
> w wyspecjalizowanego agenta konwersacyjnego **Adam** dla seniorów (SilverTech, Poznań),
> wraz z trzema warstwami interfejsu (Landing / Panel Opiekuna / Panel Admina),
> wdrożeniem Design Systemu i konwersją panelu opiekuna do aplikacji mobilnej (Capacitor).

**Data analizy:** 2026-07-14
**Baza kodu:** AVA-AI-Voice-Agent-for-Asterisk (Python backend + React/TS admin_ui)
**Design:** `design-system/` (Nordic humanism × Medical-premium, gotowy handoff)

---

## 0. Stan zastany (co JUŻ mamy w repo)

| Warstwa | Element | Stan | Lokalizacja |
|---|---|---|---|
| **Backend (voice)** | Telefonia Asterisk ARI, multi-agent, tool-calling, call history, STT/TTS, providerzy AI | ✅ dojrzały (AVA v7.3.2) | `agent/src/` |
| **Admin UI (operator)** | Dashboard, Agents, Call History, Providers, System, YAML editor, live-status SSE | ✅ działa | `agent/admin_ui/` |
| **Design System** | Tokeny (granat/złoto), 8 komponentów senioralnych, mockupy HTML 4 paneli, kontrakty API | ✅ gotowy handoff | `design-system/` |
| **Dokumentacja wdrożeniowa** | Plan F0–F18, spec RBAC/paneli, plan mobile (PWA→Capacitor) | ✅ kompletna | `docs/source-md/` |
| **Baza wiedzy RAG** | 505 chunków + embeddingi, CLI wyszukiwania | ✅ zbudowana | `rag/` |
| **Panel Opiekuna (B2C)** | — | ❌ nie istnieje | do zbudowania |
| **Panel Admina (redesign)** | — | ❌ tylko surowy AVA UI | do redesignu |
| **Landing Page** | — | ❌ nie istnieje | do zbudowania |
| **RBAC (role admin/opiekun/rodzina)** | — | ❌ AVA ma tylko jednego admina | do zbudowania |
| **Moduły domenowe (semafor, meds, wearables…)** | — | ❌ brak | plan F1–F18 |

---

## 1. KRYTYCZNA ANALIZA — zanim napiszemy pierwszą linię kodu

To jest sekcja, którą prosiłaś, żebym przemyślał krytycznie. Poniżej ryzyka,
niespójności w dokumentacji i rekomendacje, które **realnie wpłyną na kolejność prac**.

### 1.1 Największe ryzyko: to NIE jest projekt Cloudflare Pages
Środowisko GenSpark AI Developer jest zoptymalizowane pod lekkie aplikacje
Hono/Cloudflare Pages. **Adam tego nie jest.** To:
- Python backend (FastAPI-style) + Asterisk + PostgreSQL + Redis + kontenery Docker,
- osobny frontend React/Vite (SPA), później owinięty w Capacitor (iOS/Android).

**Konsekwencja:** części głosowej (Asterisk/ARI, scheduler, kontenery) **nie da się
uruchomić ani wdrożyć** w tym sandboxie ani na Cloudflare Pages. To repozytorium
pełni tu rolę **monorepo źródłowego + środowiska pracy nad frontendem i dokumentacją**.
Realne uruchomienie backendu głosowego wymaga docelowego serwera (Frankfurt DC wg handoffu)
z Dockerem i Asteriskiem. **Będę jasno oddzielał to, co mogę tu zbudować/przetestować,
od tego, co wymaga infrastruktury docelowej.**

### 1.2 Niespójność Design System vs stara dokumentacja
- Stare dokumenty (`GENSPARK DESING PROMPT`) mówią: **Inter + Lato**, kolory `#e6a817` (yellow), `#c1121f` (red).
- Aktualny Design System mówi: **Fraunces + Geist**, semafor **przyciemniony** dla WCAG AA
  (`#b8830d` yellow, `#a5121a` red), off-white `#fbfaf7` zamiast czystej bieli.

**Decyzja:** Design System (`design-system/`) jest **źródłem prawdy**. Stare prompty
traktuję jako kontekst historyczny. Wdrażam tokeny z `design-system/01-design-system/tokens.css`.

### 1.3 Dwie identyczne specyfikacje RBAC (myślnik `-` vs `—`)
Pliki `KOMPLETNA SPECYFIKACJA - PANEL…` i `… — PANEL…` to praktycznie ten sam dokument
(RAG wykrył 183 duplikaty). Używam nowszej/pełniejszej wersji, drugą trzymam tylko w archiwum.

### 1.4 Bezpieczeństwo i zgodność — to NIE jest zwykła aplikacja CRUD
Adam dotyka danych medycznych seniorów, dzwoni na 112 i wykrywa myśli samobójcze.
To rodzi twarde wymagania, które muszą być wpięte **od początku**, nie „na końcu":
- **RODO/GDPR:** szyfrowanie PESEL/telefonów (AES-256), retencja nagrań 30 dni, prawo do bycia zapomnianym (F12).
- **AI Act:** Adam MUSI się przedstawić jako AI w pierwszym zdaniu (F5, „limited risk" art. 50).
- **Semafor krytyczny (F3):** błąd klasyfikacji = realne zagrożenie życia. Wymaga guardrails (F4),
  multi-model consensus (F16) i audytu (F15) — nie wolno tego pominąć dla „szybkiego demo".
- **iOS Critical Alerts (Purple):** wymaga osobnego entitlement od Apple (wniosek składa SilverTech, nie deweloper).

**Rekomendacja:** guardrails (F4) i disclosure AI (F5) wdrażać **razem z** semaforem (F3),
a nie po nim. Bezpieczeństwo to nie osobna faza — to warstwa przecinająca wszystko.

### 1.5 Kolejność: „fundament danych" przed „efektowną warstwą"
Kuszące jest zacząć od ładnego Landing Page (bo widać efekt). Ale każdy panel i moduł
opiera się o **model danych seniora (F1)** i **RBAC**. Dlatego kolejność techniczna:
kontrakty danych → RBAC → komponenty DS → panele → moduły domenowe → mobile.
Landing Page (czysto marketingowy, bez zależności od API) można robić **równolegle**.

### 1.6 „95% reuse kodu w Capacitor" — prawda z gwiazdką
Dokument mobile słusznie rekomenduje PWA→Capacitor. Ale reuse jest wysoki **tylko jeśli
frontend od początku pisany jest mobile-first i bez zależności od API przeglądarki,
których WebView nie ma.** Dlatego responsywność i `MobileBottomNav` planuję od Fazy paneli,
nie doklejam ich później.

---

## 2. ROADMAPA — etapy realizacji

Etapy uporządkowane tak, by **każdy kończył się czymś testowalnym**. Oznaczenia:
🟢 = mogę w pełni zrealizować i przetestować tutaj · 🟡 = mogę zbudować kod, test wymaga infra ·
🔴 = wymaga infrastruktury/kont zewnętrznych (poza sandboxem).

### ETAP 0 — Fundament repo *(ten etap — w toku)* 🟢
- [x] Rozpakowanie i inwentaryzacja kodu AVA + Design System
- [x] Konwersja 13 dokumentów `.docx` → Markdown (`docs/source-md/`)
- [x] Budowa bazy wiedzy RAG (chunking + embeddingi + CLI)
- [x] Krytyczna analiza + roadmapa (ten dokument)
- [ ] Utworzenie repo **ADAM-2027** na GitHub i push monorepo
- **Rezultat:** uporządkowane, przeszukiwalne repozytorium gotowe do pracy zespołowej.

### ETAP 1 — Design System jako kod (React) 🟢
Fundament wizualny wspólny dla wszystkich paneli (Faza 1 z `INSTRUKCJA-WDROZENIA.md`).
- Scaffold `frontend/` (React 18 + TS + Vite + Tailwind), tokeny z `tokens.css`.
- Fonty Fraunces + Geist, `tailwind.config` z paletą granat/złoto/semafor.
- Komponenty bazowe (`ui/`): Button, Card, Input, Select, Switch, Badge, Alert, Modal, Tabs, Table.
- Komponenty senioralne (`senior/`): **SemaphoreBadge** (pulse tylko red/purple), SeniorCard,
  MoodChart (Recharts), MedicationRing, AlertTimeline, WearableWidget.
- Storybook-like strona demo komponentów (weryfikacja 1:1 z `Design System.html`).
- **Rezultat:** biblioteka komponentów uruchamiana lokalnie, zgodna z handoffem.

### ETAP 2 — Landing Page (Wariant B Editorial) 🟢
Niezależny od API — można robić równolegle z Etapem 1.
- 11 sekcji wg `INSTRUKCJA-WDROZENIA.md` (Hero editorial → Footer).
- Fraunces italic w KPI, złoto jako 1px akcenty (nie gradient), off-white tło.
- Responsywny, dostępny (WCAG AA), placeholdery zdjęć oznaczone do wymiany.
- **Rezultat:** wdrażalny statycznie landing marketingowy SilverTech/Adam.

### ETAP 3 — Kontrakty danych + mock API + RBAC 🟢
Warstwa danych, o którą oprą się panele. Bez backendu głosowego — na mockach.
- Typy TS z `DEVELOPER-HANDOFF.md` (Senior, Medication, WearableInfo, Alert, Order…).
- `apiClient` z interceptorem JWT, `AuthContext`, `AuthGuard`, `RoleGuard`.
- Role: `admin` / `caregiver` / `family_member` + mapa uprawnień (`config/roles.ts`).
- Mock server (MSW lub prosty json-server) zwracający dane wg kontraktów API.
- **Rezultat:** panele można budować i testować end-to-end na realistycznych danych.

### ETAP 4 — Panel Opiekuna (B2C, 8 ekranów) 🟢
Serce produktu dla rodziny (Faza 2 handoffu). Mobile-first od startu.
- Dashboard (KPI strip + lista SeniorCard + banner alertu krytycznego).
- Widok seniora z 8 zakładkami (Przegląd / Rozmowy / Leki / Wearable / Alerty / Raporty / …).
- Zamówienia (marketplace), Wiadomości, Raporty, Konto, Ustawienia (matryca powiadomień), Pomoc.
- `MobileBottomNav`, responsywność, SSE dla alertów (na mocku).
- **Rezultat:** kompletny, klikalny panel opiekuna na danych mockowych.

### ETAP 5 — Panel Admina (redesign AVA + nowe zakładki) 🟡
Migracja istniejącego admin_ui na Adam DS + nowe moduły (Faza 4 handoffu).
- Redesign na tokeny Adam, sidebar z logo, dark mode dla Admina (data-dense).
- Zachowanie funkcji AVA (Agents, Call History, Providers, System, YAML, Topology).
- Nowe: Seniorzy (CRUD), Opiekunowie, Marketplace, Raporty, Wearables Fleet, Scheduling.
- 🟡 Integracja z realnym backendem AVA wymaga uruchomionego `agent/` (infra docelowa).
- **Rezultat:** spójny wizualnie panel operatora; pełna integracja po podłączeniu backendu.

### ETAP 6 — PWA 🟢
Faza 3a mobile. Zerowy koszt, natychmiastowy efekt.
- `vite-plugin-pwa`, manifest („Adam – Panel Opiekuna", theme `#1a2744`), Service Worker.
- Cache-first assets / network-first API, baner „Zainstaluj", tryb standalone.
- **Rezultat:** panel opiekuna instalowalny na Androidzie i iOS (16.4+) jako PWA.

### ETAP 7 — Capacitor iOS + Android 🔴
Faza 3b mobile. Wymaga kont deweloperskich i macOS/Xcode (poza sandboxem).
- `npx cap init` (`pl.silvertech.adam.caregiver`), platformy iOS/Android.
- Pluginy: push-notifications (RED/PURPLE), local-notifications, splash-screen, share, biometrics (Face ID).
- Splash `#1a2744` + logo, konfiguracja push (APNs/FCM), Guideline 4.2 (natywne funkcje = brak rejectu).
- 🔴 Build `.ipa`/`.aab`, provisioning, publikacja — na maszynie SilverTech ($99/rok Apple, $25 Google).
- **Rezultat:** kod gotowy do buildu; publikacja po stronie SilverTech.

### ETAP 8+ — Moduły domenowe backendu (F1–F18) 🟡/🔴
Rozbudowa Python backendu wg planu F0–F18. Kod mogę pisać tu; uruchomienie = infra docelowa.
Kolejność priorytetowa (z korektą z sekcji 1.4 — bezpieczeństwo razem z semaforem):
1. **F1** Profile seniorów (DB + API + szyfrowanie PII) — fundament.
2. **F2** Scheduler welfare-check (APScheduler + ARI originate).
3. **F3 + F4 + F5** Semafor + Guardrails + System Prompt Adama (razem — warstwa bezpieczeństwa).
4. **F6** Medication tracker. **F8** Crisis detection. **F9** Dashboard rodzinny + SMS/email.
5. **F7** Pamięć semantyczna (RAG rozmów). **F10** Wearables. **F11** Marketplace.
6. **F12** RODO. **F13** AI Act. **F14** Mowa senioralna. **F15–F18** QA, consensus, 112, testy.

---

## 3. Co realizuję TERAZ vs co czeka na decyzję/infra

| Teraz (sandbox) | Wymaga Twojej decyzji / infra |
|---|---|
| Repo + RAG + roadmapa (Etap 0) | Konto GitHub (autoryzacja) → push ADAM-2027 |
| Design System w kodzie (Etap 1) | — |
| Landing Page (Etap 2) | Finalne zdjęcia editorial, treści prawne (RODO) |
| Mock API + RBAC (Etap 3) | Finalne kontrakty backendu (gdy F1 gotowe) |
| Panele Opiekuna/Admina na mockach (Etap 4–5) | Backend AVA uruchomiony (Docker + Asterisk + PG) |
| PWA (Etap 6) | — |
| Kod Capacitor (Etap 7) | Konta Apple/Google + macOS/Xcode (SilverTech) |
| Kod modułów F1–F18 (Etap 8+) | Serwer docelowy (Frankfurt DC) do uruchomienia |

---

## 4. Rekomendowana ścieżka najbliższych kroków

1. **Autoryzuj GitHub** → utworzę repo **ADAM-2027** i wypcham całe monorepo (kod + RAG + docs).
2. Zaczynamy **Etap 1 (Design System w kodzie)** — bo odblokowuje wszystkie panele.
3. Równolegle **Etap 2 (Landing)** — szybki, widoczny efekt dla interesariuszy.
4. Po zatwierdzeniu wyglądu → **Etap 3–4** (RBAC + Panel Opiekuna na mockach).

> Każdy etap zamykam działającym, testowalnym rezultatem i commitem do repo.
> Przy modułach backendu (F1–F18) będę korzystał z bazy RAG, żeby trzymać się
> dokładnych specyfikacji SilverTech (tabele, endpointy, progi semafora).
