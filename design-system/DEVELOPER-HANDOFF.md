# Adam · Developer Handoff · Specyfikacja techniczna

**Odbiorca:** Frontend team · GenSpark AI Developer
**Wersja:** 1.0 · Lipiec 2026

---

## Overview architektury

```
┌─────────────────────────────────────────────────────────┐
│  Adam Frontend (React 18 + TS + Vite + Tailwind)        │
│  ├── Landing (Wariant B Editorial)                      │
│  ├── Panel Opiekuna (8 ekranów) — B2C                   │
│  ├── Panel Admina (20 ekranów) — B2B internal           │
│  └── Ekrany alertów krytycznych (RED / PURPLE flows)    │
└──────────────┬──────────────────────────────────────────┘
               │ HTTPS + WSS
               ▼
┌─────────────────────────────────────────────────────────┐
│  Adam AI Engine (Python · rozszerzony AVA v7.3.2)       │
│  ├── ARI (Asterisk REST Interface)                      │
│  ├── AI providers: OpenAI + Anthropic + ElevenLabs      │
│  ├── Semafor state machine (Green→Yellow→Red→Purple)    │
│  └── Marketplace + Wearables APIs                       │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│  PostgreSQL 16 · Redis · MinIO (audio) · Frankfurt DC   │
└─────────────────────────────────────────────────────────┘
```

**Kanały mobile:**
- PWA (Progressive Web App) — działa offline, installable
- Capacitor iOS App (Face ID + Critical Alerts + HealthKit)
- Capacitor Android App (biometric + Data Safety compliance)

---

## Design Tokens — jak używać

### Import w projekcie React

```tsx
// src/main.tsx
import './styles/tokens.css'    // Design tokens (CSS variables)
import './styles/globals.css'   // Reset + typography defaults
import App from './App';

// Fonts w index.html (Google Fonts CDN)
```

### Użycie w komponentach

**Preferowany sposób: Tailwind utilities** (skonfigurowane w `tailwind.config.example.js`):

```tsx
<button className="bg-granat-700 text-white hover:bg-granat-800 rounded-lg px-4 py-2">
  Zadzwoń teraz
</button>

<div className="text-sem-red border-l-4 border-sem-red bg-sem-red-bg p-4">
  Alert!
</div>
```

**Bezpośrednio przez CSS variables** (dla dynamic/inline):

```tsx
<div style={{ background: 'var(--granat-700)', color: 'var(--paper)' }}>
  Custom styling
</div>
```

**Dostępne tokens** — patrz `01-design-system/tokens.json` dla pełnej listy.

---

## Komponenty senioralne — API contracts

### `<SemaphoreBadge />`

Sygnał 4-poziomowy z progresywną intensywnością wizualną.

```typescript
interface SemaphoreBadgeProps {
  level: 'green' | 'yellow' | 'red' | 'purple';
  label?: string;              // Custom label, np. "Alarm — upadek"
  size?: 'xs' | 'sm' | 'md' | 'lg';
  showLabel?: boolean;         // default true
  ariaLive?: 'off' | 'polite' | 'assertive'; // A11y — polite dla yellow, assertive dla red/purple
}
```

**Regułą krytyczną:** pulsowanie TYLKO dla `red` i `purple`. Green/Yellow są ambient (statyczne).

---

### `<SeniorCard />`

Karta seniora w liście dashboardu.

```typescript
interface SeniorCardProps {
  senior: Senior;
  variant?: 'compact' | 'full';
  onClick?: (senior: Senior) => void;
  showActions?: boolean;   // "Zadzwoń", "Otwórz szczegóły"
}

interface Senior {
  id: string;                            // np. "HW-01247"
  firstName: string;
  lastName: string;
  age: number;
  district: string;                      // Wilda, Grunwald, Jeżyce, Stare Miasto, Winogrady, Nowe Miasto
  address?: string;
  package: 'basic' | 'family' | 'premium';
  semaphore: SemaphoreLevel;
  semaphoreReason?: string;              // "Wykryto upadek · Xiaomi Band 8"
  mood: number;                          // 0.0 – 1.0
  moodTrend7d: number[];                 // 7 samples
  adherence30d: number;                  // 0 – 100
  heartRate?: number;                    // Latest bpm
  spo2?: number;                         // Latest %
  wearable?: WearableInfo;
  lastCall: {
    timestamp: string;                   // ISO 8601
    duration: number;                    // seconds
    agent: string;                       // e.g. "welfare-morning v7.4.2"
  };
  coordinator?: {
    id: string;
    name: string;
  } | null; // null = auto/none
  pulseAvatar?: boolean;                 // Only for RED/PURPLE
}
```

---

### `<MoodChart />`

Wykres nastroju z threshold band + markerami alertów.

```typescript
interface MoodChartProps {
  seniorId: string;
  range: '7d' | '14d' | '30d' | '90d';
  showThresholds?: boolean;              // Yellow zone 0.5, alarm zone 0.3
  markers?: AlertMarker[];               // Wykresie kropki na alertach
  onRangeChange?: (range: string) => void;
}

interface AlertMarker {
  timestamp: string;
  level: SemaphoreLevel;
  reason: string;
}
```

**Backend endpoint:** `GET /api/seniors/:id/mood?range=30d` → `{ data: MoodPoint[], markers: AlertMarker[] }`

---

### `<MedicationList />`

Lista leków + adherence per lek.

```typescript
interface MedicationListProps {
  seniorId: string;
  variant?: 'summary' | 'schedule' | 'calendar';
}

interface Medication {
  id: string;
  name: string;                          // "Metformina 500mg"
  scheduleTimes: string[];               // ["07:15", "19:15"]
  frequency: string;                     // "2×/dzień"
  notes?: string;                        // "Z posiłkiem · min. 30 min przed"
  adherence30d: number;                  // 0 – 100
  medGuardId?: string;                   // Reference to MedGuard DB
}
```

---

### `<WearableWidget />`

Live vitals z wearabla (Xiaomi Band / Apple Watch / Garmin / Fitbit).

```typescript
interface WearableWidgetProps {
  seniorId: string;
  device: WearableInfo;
  showLive?: boolean;                    // WebSocket subscription
}

interface WearableInfo {
  brand: 'xiaomi' | 'apple' | 'garmin' | 'fitbit';
  model: string;                         // "Band 8", "Watch S9", "Vivosmart 5", etc.
  pairedAt: string;
  batteryPct: number;
  syncStatus: 'ok' | 'delayed' | 'offline';
  lastSyncAt: string;
  vitals: {
    heartRate: number;
    spo2: number;
    stepsToday: number;
    sleepLastNight: SleepData;
  };
  thresholds: {
    hrLow: number;                       // e.g. 50
    hrHigh: number;                      // e.g. 110
    spo2Low: number;                     // e.g. 92
    mode: 'auto' | 'manual_override';
    overriddenBy?: {                     // If mode === 'manual_override'
      userId: string;
      userName: string;
      role: 'coordinator' | 'doctor';
      reason: string;
      overriddenAt: string;
    };
  };
  calibration: {
    status: 'calibrating' | 'stable';
    day?: number;                        // if calibrating
    totalDays?: 14;
    daysSinceStable?: number;
  };
}
```

**KRYTYCZNE:** Panel Opiekuna widok wearable tab pokazuje thresholds jako **READ ONLY**. Opiekun NIE może edytować. Może dodać `contextualNotes: string[]` (soft context — nie edytuje parametrów).

---

## API Contracts

### Auth

```http
POST /api/auth/login
Content-Type: application/json

{ "email": "anna@gmail.com", "password": "...", "otpCode": "123456" }

→ 200 OK
{ "accessToken": "...", "refreshToken": "...", "user": {...} }
```

### Seniors

```http
GET /api/seniors/mine
Authorization: Bearer ...

→ 200 OK
{ "seniors": Senior[], "total": 3 }
```

```http
GET /api/seniors/:id
→ SeniorDetail (extends Senior + calls[], meds[], alerts[], reports[])
```

```http
GET /api/seniors/:id/mood?range=30d
→ { "data": MoodPoint[], "markers": AlertMarker[] }
```

### Orders (Marketplace)

```http
POST /api/orders
Content-Type: application/json

{
  "seniorId": "HW-01247",
  "categoryId": "meds-delivery",
  "requestSource": "adam-call" | "caregiver-panel",
  "preferences": { "when": "2026-07-13T09:00:00Z", "notes": "..." }
}

→ 201 Created
{
  "orderId": "O-8472",
  "status": "auto_confirmed" | "waiting_manual_confirm",
  "cancellationWindowEndsAt": "2026-07-12T14:52:07Z",
  "partner": { "name": "DOZ...", "nip": "...", "rating": 4.8 },
  "estimatedPrice": "34 zł",
  "estimatedDelivery": "45 min"
}
```

```http
DELETE /api/orders/:id
Authorization: Bearer ...

→ 200 OK if within cancellation window (30 min)
→ 403 Forbidden if window expired
```

### Alerts + SSE

```http
GET /api/events (Server-Sent Events)

event: alert
data: {"level":"red","seniorId":"MN-02341","reason":"fall_detected","timestamp":"2026-07-12T14:22:07Z"}

event: order_status
data: {"orderId":"O-8472","status":"confirmed"}
```

### Wearables WebSocket

```
wss://api.silvertech.pl/ws/wearable/:seniorId
Authorization: token=...

← message: {"type":"vitals","hr":72,"spo2":97,"ts":"..."}
← message: {"type":"fall_detected","confidence":0.94}
← message: {"type":"battery_low","level":15}
```

### Reports

```http
GET /api/reports/:id
→ ReportSummary (JSON)

GET /api/reports/:id.pdf
→ application/pdf

GET /api/reports/:id.fhir
Accept: application/fhir+json
→ FHIR R4 Bundle
```

---

## Semafor state machine

```typescript
type SemaphoreLevel = 'green' | 'yellow' | 'red' | 'purple';

// Trigger → resulting level (per Adam spec F3)
const TRIGGERS: Record<string, SemaphoreLevel> = {
  // → GREEN
  'welfare_check_ok': 'green',
  'mood_stable': 'green',
  'meds_taken': 'green',

  // → YELLOW
  'mood_below_0.5': 'yellow',
  'loneliness_verbal': 'yellow',
  'meds_missed_1': 'yellow',
  'sleep_below_6h_repeated': 'yellow',

  // → RED
  'fall_detected': 'red',
  'hr_above_140': 'red',
  'meds_missed_2plus': 'red',
  'no_answer_3_attempts': 'red',
  'chest_pain_verbal': 'red',

  // → PURPLE (life-threatening)
  'afib_detected_with_symptoms': 'purple',
  'unconscious_prolonged': 'purple',
  'suicide_ideation': 'purple',
  'red_unresolved_15min': 'purple',      // Auto-escalation
};

// Response per level (Adam spec F3)
const RESPONSES = {
  green: { log: true, panel_update: true },
  yellow: { log: true, panel_update: true, sms_family: 'digest', push: 'quiet' },
  red: {
    log: true,
    panel_update: true,
    sms_family: 'immediate',
    push_family: 'critical',
    coordinator_notify: true,
    adam_call_retry: 3,
    mtta_target_seconds: 18,
    auto_escalate_to_purple_after_seconds: 900,
  },
  purple: {
    ...RESPONSES.red,
    auto_dial_112: true,
    live_feed_admin: true,
    push_family: 'critical_bypass_dnd',
    repeat_notification_until_ack: true,
    mtta_target_seconds: 42,
  },
};
```

---

## Escalation ladder — kolejność wywołań

```
Poziom RED aktywowany
├── [0s]   Log w bazie
├── [0s]   Panel Opiekuna aktualizuje semafor (SSE push)
├── [0s]   Adam próbuje dodzwonić do seniora (1. próba)
├── [20s]  Retry #2
├── [40s]  Retry #3
├── [60s]  SMS + push do rodziny (wszyscy opiekunowie)
├── [60s]  Powiadomienie koordynatora SilverTech
├── [Krytyczne] Koordynator ma 60s na przejęcie
├── [120s] Jeśli koordynator nie potwierdza → eskalacja Purple
└── [Purple] Auto-dial 112 z adresu + wieku + chorób seniora

Poziom PURPLE aktywowany
├── [0s]   Wszystko z Red +
├── [0s]   Auto-dial 112 (dyspozytor podaje adres, wiek, medications)
├── [0s]   LIVE feed dla rodziny + koordynatora
├── [42s]  Docelowe MTTA rodziny
└── [Powtarzanie] Notification co 30s aż potwierdzone przez rodzinę
```

**KRYTYCZNE:** Purple wymaga `iOS Critical Alert entitlement` (Apple approval process, uzasadnienie: opieka medyczna nad seniorami). Wniosek składany przez SilverTech, nie deweloper.

---

## Environment variables

```bash
# .env.production
VITE_API_URL=https://api.silvertech.pl
VITE_WS_URL=wss://api.silvertech.pl
VITE_STRIPE_PUBLIC_KEY=pk_live_...
VITE_SENTRY_DSN=https://...
VITE_ADAM_VERSION=7.4.2

# .env.development
VITE_API_URL=http://localhost:3001
VITE_WS_URL=ws://localhost:3001
```

---

## Analytics

- **PostHog** dla product analytics (self-hosted, RODO friendly)
- **Sentry** dla error tracking
- **Zdarzenia do trackowania:**
  - `panel_opened` — first login
  - `senior_detail_viewed` — z senior_id
  - `alert_acknowledged` — z level i time_to_ack
  - `order_placed` / `order_cancelled_within_window`
  - `wearable_paired` — z brand
  - `report_downloaded` — pdf vs fhir
  - `push_received` — z level, tracking bypass_dnd success

---

## Security

### Autentykacja
- JWT + refresh token (15min access, 7d refresh)
- 2FA obowiązkowo dla wszystkich Panel Admina users
- 2FA opcjonalnie dla Panel Opiekuna users (silne rekomendowane)
- Rate limiting: 5 nieudanych login/godz. → captcha, 10 → blokada

### Danych medycznych
- Wszystko szyfrowane in transit (TLS 1.3) i at rest (AES-256)
- Wearable data: pseudonimizacja seniora → `senior_uuid` (nie osobowe)
- Nagrania rozmów: retention 30 dni, transkrypty 12 mies., raporty 24 mies. (RODO)
- Audit log dla każdej edycji progów wearables (compliance medyczna)

### Anti-fraud (marketplace)
- Wykluczenia z MVP (blokowane w promptzie Adama): opłata rachunków, przelewy finansowe, przekazywanie danych karty
- Cross-check partnerów: NIP + OC verification przy dodawaniu
- Wszystkie orders logged z timestampem + kanałem (adam-call vs caregiver-panel)
- Anomaly detection: senior >5 orders/dzień → koordynator flag

---

## Contact

- **Frontend lead:** frontend@silvertech.pl
- **Backend lead:** backend@silvertech.pl
- **Design ops:** design@silvertech.pl
- **Security officer:** security@silvertech.pl

*Ostatnia rewizja: Lipiec 2026 · v1.0*
