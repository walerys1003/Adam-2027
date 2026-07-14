# Panel Admina — Mapa Ekranów (20)

**Plik referencyjny:** `Panel Admina — Complete.html`
**Route prefix:** `/admin`
**Architektura:** Router-based · sidebar switcher · localStorage persistence

---

## Sekcja OVERVIEW (7 ekranów)

| # | Ekran | Route | Screen renderer w JS |
|---|-------|-------|----------------------|
| 1 | **Dashboard** | `/admin/dashboard` | `Panel Admina Screens Overview.js` |
| 2 | **Seniorzy** (1247) | `/admin/seniors` | Overview.js — lista + filtry |
| 3 | **Seniorzy detail** | `/admin/seniors/:id` | Overview.js — `DETAIL_RENDERERS.senior` |
| 4 | **Call History** (18.4K) | `/admin/calls` | Overview.js — table + filter bar + transcript search |
| 5 | **Call Scheduling** | `/admin/scheduling` | Overview.js — 4 campaigns + weekly heatmap 24×7 |
| 6 | **Alerty** (3) | `/admin/alerts` | Overview.js — active + escalation ladder + history |
| 7 | **Marketplace** | `/admin/marketplace` | `Panel Admina Screens Marketplace.js` — 4 taby |
| 8 | **Setup Wizard** | `/admin/wizard` | Overview.js — 5-step wizard |

### Marketplace detail (4 taby):
- **Zamówienia** — split akcyjne (koordynator manual) vs informacyjne (auto-confirmed) + prawy panel z kontekstem seniora + partner card + transcript
- **Katalog usług** — 10 kategorii MVP z tagami AUTO/MANUAL/HYBRID + wykluczenia banner
- **Partnerzy** — 80 z NIP/OC/rating/skargi + Local Poznań ★ + filtry
- **Service Gaps** — plan ekspansji (kategoria × dzielnica × count)

---

## Sekcja CORE CONFIG (8 ekranów)

| # | Ekran | Route | Screen renderer |
|---|-------|-------|----------------|
| 9 | **Agenci** (12) | `/admin/agents` | `Panel Admina Screens Config.js` |
| 10 | **Agent detail** | `/admin/agents/:id` | Config.js — `DETAIL_RENDERERS.agent` (7 tabów: Prompt YAML editor / Tools / Voice / Guardrails / A/B / Metryki / Deploy history) |
| 11 | **Providers** (7) | `/admin/providers` | Config.js — 7 cards + edit form |
| 12 | **Pipelines** | `/admin/pipelines` | Config.js — 4 pipeline'y STT→LLM→TTS visual routing |
| 13 | **Contexts** (legacy) | `/admin/contexts` | Config.js — z migracji bannerem |
| 14 | **Audio Profiles** | `/admin/profiles` | Config.js — 3 profile (senior-optimized, default-adult, pstn-optimized) + skuteczność F13 |
| 15 | **Tools** (47) | `/admin/tools` | Config.js — 4 fazy (in_call/pre_call/post_call/catalog) |
| 16 | **MCP Servers** (3+cat) | `/admin/mcp` | Config.js — active + catalog 6 dostępnych |
| 17 | **Wearables Fleet** | `/admin/wearables` | `Panel Admina Screens Marketplace.js` (WEARABLES_ scope) |

### Wearables Fleet — kluczowe elementy:
- **4 provider cards** (Xiaomi Zepp Life API · Apple HealthKit · Garmin Connect · Fitbit Web API) z priorytetami P1-P4
- **Fleet table** — 941 devices z kolumnami: senior, marka, sync status, HR/SpO₂, **progi HR (auto vs ★ manual override)**, kalibracja (dzień X/14 vs stabilna), ostatnie zdarzenie
- **Detail view** — Stanisław Zieliński:
  - Baseline HR wykres 14d z threshold band manual (żółta ramka pokazująca override 120→130 przez Krzysztofa M.)
  - **Ręczne nadpisanie card** — full audit trail (kto/kiedy/dlaczego · SHA-256 verified)
  - **Notatki kontekstowe opiekunów** — soft context lista

---

## Sekcja SYSTEM (6 ekranów)

| # | Ekran | Route | Screen renderer |
|---|-------|-------|----------------|
| 18 | **Environment** (78 vars) | `/admin/env` | `Panel Admina Screens System.js` — kategorie + modified badge + restart hints |
| 19 | **Docker Services** | `/admin/docker` | System.js — 4 kontenery + Images + Volumes |
| 20 | **Asterisk** | `/admin/asterisk` | System.js — ARI status + modules + application registration + dialplan snippet |
| 21 | **Models** | `/admin/models` | System.js — STT/TTS/LLM catalog + installed + custom (Whisper senior-fine-tune) |
| 22 | **Live Logs** | `/admin/logs` | System.js — Troubleshoot/Raw modes + WebSocket streaming |
| 23 | **Terminal** | `/admin/terminal` | System.js — Web CLI z komendami `adam ...` |

---

## Sidebar navigation

**Sekcje w sidebarze (kolejność):**

```
Overview
  · Dashboard
  · Seniorzy (badge 1247)
  · Call History (badge 18.4K)
  · Call Scheduling
  · Alerty (badge red 3)
  · Marketplace (badge 7)   ← NOWE
  · Setup Wizard

Core config
  · Agenci (12)
  · Providers (7)
  · Pipelines
  · Contexts (legacy)
  · Audio Profiles
  · Tools
  · MCP Servers
  · Wearables Fleet (4)     ← NOWE

System
  · Environment
  · Docker Services
  · Asterisk
  · Models
  · Live Logs
  · Terminal
```

---

## Konwersja z demo do produkcji

Wszystkie renderery są w plikach JS (`SCREEN_RENDERERS.dashboard()`, itd.) — do produkcji **przenieś każdy do osobnego React componentu** w `src/pages/admin/`:

```tsx
// src/pages/admin/DashboardPage.tsx
export function DashboardPage() {
  const { data: metrics } = useQuery(['dashboard', 'metrics'], fetchDashboardMetrics);
  const { data: seniors } = useQuery(['seniors', 'alerts'], fetchSeniorsWithAlerts);
  // ... implementacja odpowiadająca SCREEN_RENDERERS.dashboard()
}
```

**Wszystkie mockowe dane** (`SENIORS_DATA`, `AGENTS_DATA`, `ORDERS_DATA`, `PARTNERS_DATA`, itd.) w plikach JS **zastąp real API queries**.

---

## Dark mode dla Panel Admina

Rozstrzygnięte w design: Panel Admina obsługuje **light domyślny + dark opcjonalny** (koordynator dyżuruje 12h — dark mode redukuje zmęczenie oczu).

Implementacja:
- Dodaj `<ThemeToggle />` w Topbar
- `[data-theme="dark"]` na `<html>` przełącza CSS variables
- **Nie ma tokens.css dla dark yet** — do dorobienia w Fazie 4

**Referencja dark:** `Panel Admina.html` (stara wersja dark) — użyj jako benchmark stylistyczny dla dark variables.
