# Adam · Instrukcja Wdrożenia Design System

**Dla:** GenSpark AI Developer / zespół frontend
**Kierunek:** Nordic humanism × Medical-premium
**Stack:** React 18 + TypeScript + Vite + Tailwind + Capacitor

---

## Spis treści

1. [Przygotowanie środowiska](#1-przygotowanie-środowiska)
2. [Faza 1 — Design System + Landing (Tydzień 1–2)](#faza-1--design-system--landing)
3. [Faza 2 — Panel Opiekuna (Tydzień 3–5)](#faza-2--panel-opiekuna)
4. [Faza 3 — Capacitor iOS + Android (Tydzień 6–7)](#faza-3--capacitor-ios--android)
5. [Faza 4 — Panel Admina (Tydzień 8–10)](#faza-4--panel-admina)
6. [Testing i acceptance criteria](#testing-i-acceptance-criteria)
7. [Wdrożenie na produkcję](#wdrożenie-na-produkcję)

---

## 1. Przygotowanie środowiska

### 1.1 Zainstaluj Node.js 20+ i pnpm

```bash
node --version   # v20.x wymagane
pnpm --version   # 9.x preferowane
```

### 1.2 Struktura projektu (docelowa)

```
adam-frontend/
├── src/
│   ├── styles/
│   │   ├── tokens.css              ← Z 01-design-system/tokens.css
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/                     ← Bazowe (Button, Card, Input, Badge)
│   │   ├── senior/                 ← Adam-specific (SeniorCard, MoodChart, SemaphoreBadge)
│   │   ├── layout/                 ← AppShell, Sidebar, Topbar
│   │   └── forms/                  ← TweaksPanel, form components
│   ├── pages/
│   │   ├── landing/                ← Landing (Wariant B)
│   │   ├── caregiver/              ← Panel Opiekuna (8 ekranów)
│   │   └── admin/                  ← Panel Admina (20 ekranów)
│   ├── hooks/
│   ├── lib/
│   │   ├── api/                    ← Fetch wrappers, kontrakty
│   │   ├── auth/
│   │   └── semaphore/              ← Logika escalation ladder
│   └── main.tsx
├── public/
│   ├── fonts/                      ← Fraunces + Geist (opcjonalnie self-hosted)
│   └── assets/
├── tailwind.config.ts              ← Z 01-design-system/tailwind.config.example.js
├── vite.config.ts                  ← + vite-plugin-pwa
├── capacitor.config.ts             ← Dodane w Fazie 3
├── package.json
└── README.md
```

### 1.3 Package.json — baseline

```jsonc
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.22.0",
    "@radix-ui/react-dialog": "^1.1.0",
    "@radix-ui/react-dropdown-menu": "^2.1.0",
    "@radix-ui/react-select": "^2.1.0",
    "@radix-ui/react-tabs": "^1.1.0",
    "@radix-ui/react-tooltip": "^1.1.0",
    "@radix-ui/react-switch": "^1.1.0",
    "axios": "^1.7.0",
    "date-fns": "^3.6.0",
    "lucide-react": "^0.400.0",
    "recharts": "^2.12.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.3.0",
    "framer-motion": "^11.2.0",
    "sonner": "^1.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.4.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "vite": "^5.3.0",
    "vite-plugin-pwa": "^0.20.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0"
  }
}
```

### 1.4 Zainstaluj i skonfiguruj Tailwind

```bash
pnpm add -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Zastąp `tailwind.config.ts`** zawartością z `01-design-system/tailwind.config.example.js`.

### 1.5 Zainstaluj fonty

**Opcja A: Google Fonts CDN (najprostsze)**

W `index.html`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,ital,wght@9..144,0,300;9..144,0,400;9..144,0,500;9..144,0,600;9..144,0,700;9..144,1,400;9..144,1,500&family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

**Opcja B: Self-hosted (dla PWA offline)**

Pobierz z:
- Fraunces: https://fonts.google.com/specimen/Fraunces
- Geist: https://vercel.com/font (lub npm `@vercel/font-geist`)

Umieść w `public/fonts/`, dodaj `@font-face` w `src/styles/globals.css`.

---

## Faza 1 — Design System + Landing

**Czas:** 10–14 dni · **Zespół:** 1 frontend dev + 1 designer weryfikator

### 1.1 Skopiuj tokens

```bash
cp 01-design-system/tokens.css src/styles/tokens.css
```

Zaimportuj w `src/main.tsx`:

```typescript
import './styles/tokens.css'
import './styles/globals.css'
```

**Weryfikacja:** otwórz `Design System.html` w przeglądarce i porównaj z tym co widzisz w swojej dev-runie. Kolory, spacing, fonts muszą być IDENTYCZNE.

### 1.2 Zbuduj bazowe komponenty (`src/components/ui/`)

| Komponent | Referencja w mockupach | Uwagi |
|-----------|------------------------|-------|
| `Button` | Design System.html · sekcja Buttons | 4 warianty: primary, accent (gold), ghost, danger + rozmiary sm/md/lg |
| `Card` | Design System.html · używane wszędzie | border 1px, radius 12px, shadow e-1 |
| `Input` | Design System.html · sekcja Form fields | focus: border granat-600 + box-shadow ring |
| `Select` | Panel Opiekuna Ustawienia | Custom appearance:none + SVG chevron |
| `Switch` | Panel Opiekuna Ustawienia (matryca semafora) | 40×22px, animacja `.2s ease-out`, green gdy checked |
| `Badge` (Pip) | Panel Admina (kolumny Semafor) | 5 wariantów: green/yellow/red/purple/info + neutral/gold |
| `Alert` (Strip) | Panel Opiekuna Dashboard | 3 warianty: red/warn/info + left border 4px |
| `Modal` | (do zbudowania) | Radix Dialog + Adam styling |
| `Tabs` | Panel Opiekuna Widok seniora | 5-8 tabów, underline złoty |
| `Table` | Panel Admina tablice | Wszystkie tabele w Panel Admina — konsystentny styl |

### 1.3 Zbuduj komponenty senioralne (`src/components/senior/`)

| Komponent | Referencja | API props |
|-----------|-----------|-----------|
| `SemaphoreBadge` | Design System.html · Semafor progresywny | `level: 'green' \| 'yellow' \| 'red' \| 'purple'`, `pulse?: boolean` |
| `SeniorCard` | Panel Opiekuna Dashboard | Cały wiersz z awatarem, pulsem, metrykami |
| `MoodChart` | Panel Opiekuna Widok seniora / Raporty | Recharts LineChart 7/14/30/90d + threshold band |
| `MedicationRing` | Panel Opiekuna Widok seniora | SVG circle progress + procent w środku |
| `AlertTimeline` | Ekrany Alertów Krytycznych | Vertical timeline z kolorowymi kropkami |
| `ConversationCard` | Panel Opiekuna Rozmowy | Transkrypt + audio player + tags |
| `HeartRateChart` | Panel Opiekuna Wearable tab | HR 24h z progami alarmowymi + peak markers |
| `SleepPhases` | Panel Opiekuna Wearable tab | Kolorowy pasek Light/Deep/REM/Awake |
| `CalibrationProgress` | Panel Admina Wearables Fleet | "Dzień 8/14" z progress bar |
| `EmergencyContactList` | Panel Opiekuna Widok seniora | Numerowana lista z prioritetami |

### 1.4 Landing Page (Wariant B Editorial)

**Rozstrzygnięty kierunek: Wariant B** (patrz `02-landing/ROZSTRZYGNIETY-KIERUNEK.md`).

Sekcje do zaimplementowania (kolejność):

1. **Nav** — sticky, backdrop-blur, logo + linki + CTA
2. **Hero editorial** — asymetryczny grid 1:1, magazynowa numeracja "Numer 01", portret placeholder z cytatem seniora, meta stats (18s/96%/2×/49zł)
3. **Signoff marquee strip** — granatowa taśma z rotacyjnymi zaletami
4. **Chapter 01: Problem** — "Dzwoniłam w niedziele...", pull quote z drop cap, 2-column narracja
5. **Chapter 02: How it works** — 3 story cuts (08:00/19:00/22:14) z meta tags
6. **Chapter 03: Features** — asymetryczny 6-card grid z ciemnym wide highlight
7. **Partners section** — "80+ zweryfikowanych partnerów Poznania" · 8 kaflów + editorial stats (64/80 · 100% OC · 4.7★)
8. **Testimonial** — big pull quote na granacie
9. **Pricing** — 3 tiers (49/79/119) z hero card middle
10. **Final CTA** — "Twój bliski zasługuje na codzienną rozmowę"
11. **Footer** — 4 kolumny + tagline serif italic

**Krytyczne detale wizualne:**
- Fraunces italic w cyfrach (nie tylko nagłówkach)
- Cytat portretowy w hero MUSI być placeholderem — do wymiany prawdziwym zdjęciem przed launch
- Zero interaktywnej mapy Poznania (świadome — brak gęstości partnerów)
- Marquee strip przewijana CSS animation, nie JS

### 1.5 Acceptance criteria Fazy 1

- [ ] Wszystkie kolory z `tokens.css` renderują się poprawnie
- [ ] Fraunces + Geist ładują się z Google Fonts (network tab)
- [ ] `SemaphoreBadge` z `level="red"` pulsuje, z `level="green"` NIE pulsuje
- [ ] Landing B mobile-responsive (test na 375px, 768px, 1440px)
- [ ] Lighthouse Performance ≥90, Accessibility ≥95
- [ ] Bazowe komponenty w Storybook (jeśli używacie)
- [ ] Wszystkie kontrasty WCAG AA (patrz `07-assets/colors.md`)

---

## Faza 2 — Panel Opiekuna

**Czas:** 15–21 dni · **Zespół:** 2 frontend devs + 1 backend integration

### 2.1 Ekrany do zbudowania

Wszystkie w jednym pliku `Panel Opiekuna.html` — analiza dokładna:

| # | Ekran | Route | Główny komponent | Dependencies |
|---|-------|-------|------------------|--------------|
| 1 | Dashboard | `/panel` | `SeniorCardGrid` + `AlertBanner` + `KPIStrip` | Faza 1 komponenty |
| 2 | Widok seniora | `/panel/senior/:id` | `SeniorDetailHead` + 8 tabów | `MoodChart`, `MedicationList` |
| 3 | Zamówienia | `/panel/orders` | `OrderCard` z 30-min countdown + `CategoryPicker` grid 10 kat. | 30-min countdown hook |
| 4 | Wiadomości | `/panel/messages` | Inbox 3-column (filter/list/thread) | React Query dla real-time |
| 5 | Raporty | `/panel/reports` | `ReportCalendar` heatmap + `FeaturedReport` + tabela | PDF viewer |
| 6 | Konto | `/panel/account` | `SubscriptionHero` + `LoyaltyCard` + `Sessions` + `Invoices` | Stripe integration |
| 7 | Ustawienia | `/panel/settings` | Sidebar sticky + **matryca semafora** | Radix Switch |
| 8 | Pomoc | `/panel/help` | `SupportStatusBar` + `EmergencyBox` + `VideoTutorials` + FAQ | Intercom lub własny chat |

### 2.2 Szczegółowe API contracts

Patrz `03-panel-opiekuna/API-CONTRACTS.md` — pełne kontrakty JSON dla endpoints.

Kluczowe:
- `GET /api/seniors/mine` — lista seniorów opiekuna
- `GET /api/seniors/:id` — full detail z mood/adherence/wearable
- `GET /api/seniors/:id/calls?limit=20` — historia rozmów
- `GET /api/seniors/:id/wearable/live` — WebSocket dla HR live
- `POST /api/orders` — złóż zamówienie (auto-confirm vs manual)
- `DELETE /api/orders/:id` — anuluj (tylko w 30-min oknie)
- `GET /api/messages?source=adam|coordinator|family|partner`
- `GET /api/reports/:id.pdf` + `/api/reports/:id.fhir`

### 2.3 30-min okno anulowania — logika

```typescript
// hooks/useOrderCancellationWindow.ts
const CANCELLATION_WINDOW_MS = 30 * 60 * 1000;

export function useOrderCancellationWindow(orderCreatedAt: string) {
  const [msLeft, setMsLeft] = useState(() => {
    const elapsed = Date.now() - new Date(orderCreatedAt).getTime();
    return Math.max(0, CANCELLATION_WINDOW_MS - elapsed);
  });

  useEffect(() => {
    if (msLeft <= 0) return;
    const t = setInterval(() => setMsLeft(m => Math.max(0, m - 1000)), 1000);
    return () => clearInterval(t);
  }, [orderCreatedAt]);

  return {
    canCancel: msLeft > 0,
    minutesLeft: Math.floor(msLeft / 60000),
    secondsLeft: Math.floor((msLeft % 60000) / 1000),
    formatted: `${Math.floor(msLeft/60000)}:${String(Math.floor((msLeft%60000)/1000)).padStart(2,'0')}`,
    progressPct: (msLeft / CANCELLATION_WINDOW_MS) * 100,
  };
}
```

### 2.4 Semafor — komponenty

```tsx
// components/senior/SemaphoreBadge.tsx
type SemaphoreLevel = 'green' | 'yellow' | 'red' | 'purple';

interface SemaphoreBadgeProps {
  level: SemaphoreLevel;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

// KRYTYCZNE: pulsowanie TYLKO dla red i purple
export function SemaphoreBadge({ level, label, size = 'md' }: SemaphoreBadgeProps) {
  const shouldPulse = level === 'red' || level === 'purple';
  return (
    <span className={cn('pip', `pip-${level}`)}>
      <span className={cn('pip-dot', shouldPulse && 'animate-pulse')} />
      {label || levelLabels[level]}
    </span>
  );
}
```

### 2.5 Acceptance criteria Fazy 2

- [ ] 8 ekranów działa, każdy odpowiada mockupowi w `Panel Opiekuna.html`
- [ ] `SemaphoreBadge` pulsuje TYLKO dla red/purple (weryfikacja wizualna)
- [ ] 30-min countdown anulowania działa poprawnie
- [ ] Matryca semafora × kanał (Push/SMS/Email/Phone) — poprawne switch behavior
- [ ] Purple w matrycy MUSI być zablokowany (`disabled` + `checked`)
- [ ] Historia mood 90d renderuje bez lagów (Recharts)
- [ ] Wszystkie widoki responsywne mobile (Capacitor gotowość)

---

## Faza 3 — Capacitor iOS + Android

**Czas:** 10–14 dni · **Zespół:** 1 mobile-savvy frontend + 1 native ops

### 3.1 PWA-first setup

```bash
pnpm add -D vite-plugin-pwa
```

W `vite.config.ts`:

```typescript
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Adam · Panel Opiekuna',
        short_name: 'Adam',
        description: 'Cyfrowy opiekun rodzinny SilverTech',
        theme_color: '#1a2744',   // granat-700
        background_color: '#fbfaf7', // paper
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/panel',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: '/icons/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        runtimeCaching: [
          { urlPattern: /^https:\/\/fonts\.(googleapis|gstatic)\.com/, handler: 'CacheFirst' },
          { urlPattern: /\/api\/seniors\/.+/, handler: 'NetworkFirst' },
        ],
      },
    }),
  ],
});
```

### 3.2 Capacitor init

```bash
pnpm add @capacitor/core @capacitor/cli @capacitor/ios @capacitor/android
pnpm add @capacitor/push-notifications @capacitor/local-notifications
pnpm add @capacitor/haptics @capacitor/status-bar @capacitor/splash-screen
pnpm add @capacitor-mlkit/face-detection # dla Face ID przez Face detection API
npx cap init "Adam" "pl.silvertech.adam"
npx cap add ios
npx cap add android
```

### 3.3 Capacitor config

```typescript
// capacitor.config.ts
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'pl.silvertech.adam',
  appName: 'Adam',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#1a2744',  // granat-700
      androidSplashResourceName: 'splash',
      showSpinner: false,
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#1a2744',
      overlaysWebView: false,
    },
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
  },
  ios: {
    contentInset: 'automatic',
  },
  android: {
    allowMixedContent: false,
  },
};

export default config;
```

### 3.4 Push notifications per poziom semafora

```typescript
// lib/semaphore/push-config.ts
export const PUSH_LEVEL_CONFIG = {
  green: {
    priority: 'low',
    sound: null,
    vibration: null,
    bypassDND: false,
    channel: 'adam-reports', // Android channel
  },
  yellow: {
    priority: 'normal',
    sound: 'default',
    vibration: [200],
    bypassDND: false,
    channel: 'adam-attention',
  },
  red: {
    priority: 'high',
    sound: 'alarm.wav',
    vibration: [500, 300, 500, 300, 500],
    bypassDND: 'IF_CRITICAL_ALERTS_ENABLED', // iOS: użytkownik musi włączyć w Settings
    channel: 'adam-alert',
  },
  purple: {
    priority: 'max',
    sound: 'critical-alarm.wav',
    vibration: [1000, 200, 1000, 200, 1000],
    bypassDND: 'ALWAYS', // iOS: użyj CriticalAlert entitlement (wymaga Apple approval)
    channel: 'adam-critical',
    repeatUntilAcknowledged: true,
    repeatIntervalMs: 30000,
  },
};
```

**⚠ Wymaga:**
- **iOS Critical Alert entitlement** — trzeba złożyć wniosek do Apple (uzasadnienie: opieka medyczna nad seniorami)
- **Android** — kanały notyfikacji zgodne z Android 8+ NotificationChannel

### 3.5 Face ID / Biometric login

```typescript
import { Capacitor } from '@capacitor/core';
import { NativeBiometric } from '@capgo/capacitor-native-biometric';

async function loginWithBiometric() {
  const result = await NativeBiometric.isAvailable();
  if (!result.isAvailable) return null;

  try {
    await NativeBiometric.verifyIdentity({
      reason: 'Zaloguj się do Adam',
      title: 'Weryfikacja tożsamości',
      subtitle: 'Panel Opiekuna',
      description: 'Użyj Face ID lub Touch ID',
    });
    const creds = await NativeBiometric.getCredentials({ server: 'adam.silvertech.pl' });
    return creds;
  } catch (e) {
    return null;
  }
}
```

### 3.6 Acceptance criteria Fazy 3

- [ ] PWA installable na iOS + Android (test "Add to Home Screen")
- [ ] Aplikacja natywna Capacitor buduje się i uruchamia na simulatorze iOS/Android
- [ ] Push notifications działają — GREEN/YELLOW/RED/PURPLE z odmiennymi zachowaniami
- [ ] Face ID login działa (iPhone)
- [ ] Splash screen granatowy `#1a2744` — matchuje token
- [ ] Statusbar granatowy — nie flashuje białym przy przejściach
- [ ] Zaakceptowanie do App Store i Google Play (patrz sekcja "Wdrożenie")

---

## Faza 4 — Panel Admina

**Czas:** 15–21 dni · **Zespół:** 2 frontend devs

### 4.1 Zakres

**Panel Admina — Complete.html** to 20 ekranów w architekturze router-based (single-page z sidebar-switcherem). Do produkcji zaimplementować jako React Router:

```
/admin
├── /dashboard                     ← Overview KPI + topology
├── /seniors                       ← Lista 1247 z filtrami
├── /seniors/:id                   ← Detail koordynatora (koordynator view)
├── /calls                         ← Call History (18.4K)
├── /scheduling                    ← Cron rules + heatmap
├── /alerts                        ← Escalation ladder + historia
├── /marketplace                   ← Orders/Catalog/Partners/Gaps (4 tabs)
├── /wizard                        ← 5-step setup
├── /agents                        ← 12 agents + prompt editor detail
├── /agents/:id                    ← Prompt YAML editor + A/B testing
├── /providers                     ← 7 providers + edit form
├── /pipelines                     ← STT→LLM→TTS visual routing
├── /contexts                      ← Legacy (z migracji banner)
├── /profiles                      ← Audio profiles (senior-optimized)
├── /tools                         ← 47 tools w 4 fazach
├── /mcp                           ← Model Context Protocol servers
├── /wearables                     ← Wearables Fleet + kalibracja + override
├── /env                           ← .env variables editor
├── /docker                        ← Kontenery + images + volumes
├── /asterisk                      ← ARI status + modules
├── /models                        ← STT/TTS/LLM catalog
├── /logs                          ← Live logs streaming (WebSocket)
└── /terminal                      ← Web CLI
```

### 4.2 Migracja z shadcn/ui (obecny AVA) na Adam Design System

**Krok po kroku:**

1. **Zamień** `tailwind.config.js` na Adam wersję
2. **Zamień** `src/index.css` `--primary` (240 5.9% 10%) → `#1a2744`
3. **Refactor** wszystkich stron `pages/*.tsx` — przenieś do `pages/admin/*.tsx`
4. **Podmień komponenty shadcn na Adam:**
   - shadcn `Button` → Adam `Button` (nowa paleta granat/gold)
   - shadcn `Card` → Adam `Card` (border warm, radius 12)
   - shadcn `Badge` → Adam `Pip` + `Badge`
   - shadcn `Table` → Adam `Table` (paper-2 header, monospaced numbers)
   - shadcn `Dialog` → Adam `Modal` (Fraunces title)
5. **Dodaj dark mode** dla Panel Admina (opcja użytkownika — koordynator pracuje 12h dyżurów)

### 4.3 Krytyczne komponenty Panel Admina

| Komponent | Uwagi |
|-----------|-------|
| `LiveTopology` | 4 nodes (ai_engine, asterisk, local_ai_server, admin_ui) + SSE stream |
| `LogsStream` | Filtry: level × category (troubleshoot mode + raw) + regex search |
| `PromptEditor` | Monaco-like YAML z color-coded syntax + diff view + hot-reload deploy |
| `MarketplaceOrderQueue` | Split akcyjne (manual) vs informacyjne (auto) + partner card + transcript |
| `WearablesFleet` | Tabela 941 devices + kalibracja progress + manual override badge |
| `ProvidersHealthChart` | Latency p50/p95 real-time + status pip |
| `CostTracking` | Line chart + margin brutto + budżet miesięczny |
| `ServiceGaps` | Wyzwanie ekspansji · kategoria × dzielnica × count |

### 4.4 Acceptance criteria Fazy 4

- [ ] Wszystkie 20 ekranów działa, sidebar switcher persistuje w localStorage
- [ ] Dark mode dla admina — pełny wsparcie (patrz `Panel Admina.html` — stara wersja dark ma benchmark)
- [ ] Live logs streaming WebSocket bez lagów (10k events buffer, auto-scroll)
- [ ] Prompt editor działa z hot-reload (deploy → agent v.X+1)
- [ ] Marketplace: split akcyjne (koordynator klika Potwierdź) vs informacyjne (auto-confirmed)
- [ ] Wearables Fleet: manual override widoczny ze złotą obwódką + audit log

---

## Testing i acceptance criteria

### 5.1 Testy komponentów

```typescript
// components/senior/__tests__/SemaphoreBadge.test.tsx
describe('SemaphoreBadge', () => {
  it.each([
    ['green', false],
    ['yellow', false],
    ['red', true],
    ['purple', true],
  ])('level=%s → pulse=%s', (level, shouldPulse) => {
    const { container } = render(<SemaphoreBadge level={level} />);
    const dot = container.querySelector('.pip-dot');
    expect(dot?.classList.contains('animate-pulse')).toBe(shouldPulse);
  });
});
```

### 5.2 Accessibility

**WCAG AA compliance obowiązkowe** dla wszystkich color pairs (opiekun 60+ może być pierwszym userem panelu):

- Wszystkie tekst-tło kontrasty ≥4.5:1 (badane w `07-assets/colors.md`)
- Focus states widoczne (border granat-600 + shadow 3px)
- Wszystkie akcje z klawiatury (Tab, Enter, Escape)
- ARIA labels dla ikon-only buttonów
- Alert live regions dla dynamicznych powiadomień (`aria-live="polite"` dla YELLOW, `aria-live="assertive"` dla RED/PURPLE)

### 5.3 Performance

- Lighthouse ≥90 (Performance, Accessibility, Best Practices, SEO)
- First Contentful Paint <1.5s
- Time to Interactive <3s
- Bundle size <300KB gzipped (main chunk)

---

## Wdrożenie na produkcję

### 6.1 Hosting Frontend

**Wybór:** Vercel (proste), Cloudflare Pages (tanie), lub własny nginx/Kubernetes.

**Domena:** `adam.silvertech.pl` (produkcja) + `staging.adam.silvertech.pl`

### 6.2 SSL, CDN, security headers

```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob:; connect-src 'self' https://api.silvertech.pl wss://api.silvertech.pl
Permissions-Policy: geolocation=(self), camera=(), microphone=()
```

### 6.3 App Store submission

**iOS App Store:**
- App ID: `pl.silvertech.adam`
- Category: Medical / Health & Fitness
- Age rating: 4+
- **Screenshoty:** wygeneruj z Panel Opiekuna.html × 6 (iPhone 6.7", 6.5", 5.5" + iPad 13", 12.9")
- **App Privacy manifest** — dane zdrowotne, kontakty rodziny, lokalizacja
- **Krytyczne dla approval:**
  - Guideline 4.2 — dodać minimum 3 features natywne (Push, Face ID, Deep Linking) — CHECK
  - Guideline 5.1.1 — Privacy Policy URL i in-app privacy screen
  - HealthKit entitlement dla integracji Apple Watch

**Google Play:**
- Package: `pl.silvertech.adam`
- Category: Medical
- Content rating: PEGI 3 / Everyone
- Data safety form — pełny disclosure
- **In-app messaging** przy pierwszym Runtime dla POST_NOTIFICATIONS permission

### 6.4 Backend integration checklist

Backend ma być **osobnym projektem** (Adam AI Engine — patrz repo AVA v7.3.2 rozszerzone o Faza F0-F18). Frontend integruje przez API contracts w `03-panel-opiekuna/API-CONTRACTS.md`.

- [ ] SSE endpoint `/api/events` (Server-Sent Events dla live feed admin)
- [ ] WebSocket `/ws/wearable/:senior_id` (live HR/SpO₂)
- [ ] REST `/api/*` (CRUD)
- [ ] Auth: JWT + refresh token, 2FA obowiązkowo dla admin
- [ ] Rate limiting: 100 req/min per user, 10 req/s per IP

---

## Kontakt awaryjny podczas wdrożenia

- **Design blocker?** design@silvertech.pl (odpowiedź <4h)
- **API contract dispute?** tech@silvertech.pl
- **Production incident?** ops@silvertech.pl · dyżur 24/7 · `+48 61 22 44 000`

---

*Powodzenia. Adam ma być spokojem, który ma dowody — nie tylko pięknym designem.*
