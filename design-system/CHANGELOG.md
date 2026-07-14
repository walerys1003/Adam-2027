# Adam Design System — Changelog

## [1.0.0] — 2026-07-13

### 🎉 Initial release — pełny design system + wszystkie mockupy

**Kierunek wizualny:** Nordic humanism × Medical-premium
**Rozstrzygnięty wariant Landing:** Wariant B Editorial

### Dodane
- **Design System** — pełny system tokens (kolor, typografia, spacing, elevation, motion)
- **Landing Page** — 2 warianty (A Instytucjonalny, B Editorial · zwycięski)
- **Panel Opiekuna** — 8 ekranów:
  - Dashboard z alertami krytycznymi + KPI + lista bliskich
  - Widok szczegółowy seniora (8 tabów: Przegląd, Rozmowy 147, Leki 4, Wearable, Alerty 3, Raporty, Rodzina/RBAC, RODO)
  - **Zamówienia** — z 30-min oknem anulowania + kanał (Adam-call vs Opiekun)
  - **Wiadomości** — inbox 3-kolumny (Adam / Koordynator / Rodzina / Partnerzy)
  - **Raporty** — trend 90d + featured weekly + calendar heatmap 6 mies. + FHIR export
  - **Konto** — subscription hero + loyalty progress + referral + 3 sessions + faktury
  - **Ustawienia** — matryca semafora 5×5 + godziny ciszy + bezpieczeństwo + RODO
  - **Pomoc** — status SLA + emergency box + 3 support channels + wideoporadniki + FAQ
- **Panel Admina — Complete** — 20 ekranów w architekturze router-based:
  - Overview: Dashboard, Seniorzy 1247, Call History 18.4K, Call Scheduling, Alerty 3, Marketplace, Setup Wizard
  - Core Config: Agenci 12, Providers 7, Pipelines, Contexts (legacy), Audio Profiles, Tools 47, MCP, Wearables Fleet
  - System: Environment 78 vars, Docker 4 kontenery, Asterisk ARI, Models, Live Logs, Terminal
- **Marketplace** (Panel Admina) — 4 taby:
  - Zamówienia split (koordynator manual vs auto-confirmed)
  - Katalog 10 kategorii MVP z tagami AUTO/MANUAL/HYBRID
  - Partnerzy 80 z NIP/OC/rating/skargi + Local Poznań priority
  - Service Gaps — plan ekspansji
- **Wearables Fleet** (Panel Admina) — 4 marki × 941 devices:
  - Xiaomi Band 8/9 · Apple Watch · Garmin · Fitbit
  - Kalibracja adaptacyjna 14 dni (widoczny progress bar)
  - Manual override progów (audit trail z SHA-256)
  - Notatki kontekstowe opiekunów (soft context, nie edytują parametrów)
- **Ekrany Alertów Krytycznych** — dedykowany artefakt:
  - RED escalation flow (upadek Xiaomi Band → 3 próby → SMS rodzina)
  - PURPLE flow (auto-dial 112 z adresem + wiekiem + lekami)
  - Phone push mockups iOS z 4 poziomami intensywności
- **Strategy Deck** — 14 slajdów strategii wizualnej dla zarządu

### Zdefiniowane komponenty senioralne
- `SemaphoreBadge` — sygnał 4-poziomowy z progresywną intensywnością
- `SeniorCard` — karta seniora z pulsem awatara dla Red/Purple
- `MoodChart` — Recharts 7/14/30/90d z threshold band + markery alertów
- `MedicationList` — z adherence per lek + rozkład dobowy
- `WearableWidget` — live HR/SpO₂/sen/kroki + kalibracja + progi
- `AlertTimeline` — chronologia alertów z kolorowymi kropkami
- `ConversationCard` — transkrypt + audio player + tags
- `EmergencyContactList` — prioritetyzowana lista

### Kluczowe decyzje wizualne
- Granat #1a2744 zachowany (sunk cost w Capacitor splash)
- Złoto matowe #c8963e — nigdy jako gradient
- **Fraunces + Geist** (darmowe, nie Inter/Roboto — anti-AI-slop)
- Semafor progresywny (pulse tylko dla Red/Purple)
- Dwie gęstości: Balanced (Opiekun) vs Data-dense (Admin)
- Fotografia editorial TYLKO landing, brak w produkcie
- 30-min okno anulowania zamówień jako audyt dla rodziny
- Marketplace hybrid confirmation (auto vs manual)
- Opiekun NIE edytuje progów medycznych wearables (tylko soft context)

### Dokumentacja
- `README.md` — brief startowy
- `INSTRUKCJA-WDROZENIA.md` — 4-fazowa roadmap wdrożenia
- `DEVELOPER-HANDOFF.md` — pełne API contracts + komponenty
- Extract tokens: `tokens.css` + `tokens.json` + `tailwind.config.example.js`
- Documenty specjalistyczne: SCREENS-MAP × 2, API-CONTRACTS, ESCALATION-LADDER, colors.md, typography.md, icons-inventory.md, components-inventory.md

### Wykluczenia z MVP (świadome)
- Opłata rachunków (wektor oszustw na seniorach)
- Przelewy finansowe
- Fryzjer domowy, catering, stomatolog, optyk, pranie, pedicure, wyjście z psem, kultura — Faza 2/3
- Custom SilverTech Band OEM (osobny biznes sprzętowy, decyzja na później)
- Withings ScanWatch, Samsung Galaxy Watch, Oura Ring (mała baza użytkowników 70+)

---

## Wersje przyszłe (planowane)

### [1.1.0] — Q4 2026 (planowane)
- Aplikacja Capacitor iOS + Android (Faza 3 wdrożenia)
- Voice UI dla opiekuna ("Hey Adam, jak mama?")
- Wykorzystanie HealthKit iOS dla Apple Watch integracji
- Push notifications critical alert dla iOS (wniosek Apple)

### [1.2.0] — Q1 2027 (planowane)
- Panel Admina full dark mode
- Rozszerzenie Marketplace o kolejne kategorie (fryzjer, catering, pedicure)
- Integracja z lekarzem POZ przez FHIR API (progi wearable z historii medycznej)
- Withings ScanWatch integration (medyczna klasa EKG)

### [2.0.0] — Q2 2027 (rozważane)
- Multi-language support (English, Ukrainian, German)
- Ekspansja poza Poznań (Warszawa, Kraków, Wrocław, Trójmiasto)
- Adam Voice Marketplace API (opłata rachunków z 2FA + biometrią)
