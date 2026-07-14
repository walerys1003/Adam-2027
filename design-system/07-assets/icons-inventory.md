# Adam · Icons Inventory

**Biblioteka:** [`lucide-react`](https://lucide.dev/) (pnpm add lucide-react)
**Alternatywa:** Ręczne inline SVG (jak w mockupach) — nie zalecane w produkcji.

## Semantyka ikon

| Kontekst | Ikona lucide | Import |
|----------|-------------|--------|
| **Dashboard** | `LayoutDashboard` | `import { LayoutDashboard } from 'lucide-react'` |
| **Bliscy / Seniorzy** | `Users` |  |
| **Zamówienia (marketplace)** | `ShoppingBag` |  |
| **Wiadomości** | `Mail` |  |
| **Raporty** | `FileBarChart` |  |
| **Konto** | `UserCircle` |  |
| **Ustawienia** | `Settings` |  |
| **Pomoc** | `HelpCircle` |  |
| **Alerty** | `AlertTriangle` |  |
| **Emergency 112** | `Siren` |  |
| **Semafor GREEN** | `CheckCircle2` |  |
| **Semafor YELLOW** | `AlertCircle` |  |
| **Semafor RED** | `AlertTriangle` |  |
| **Semafor PURPLE** | `Siren` lub custom |  |
| **Telefon / dzwoni** | `Phone` |  |
| **Wearable / opaska** | `Watch` |  |
| **Serce / HR** | `HeartPulse` |  |
| **Leki** | `Pill` |  |
| **MoodChart** | `LineChart` |  |
| **Sen** | `Moon` |  |
| **Kroki / aktywność** | `Activity` lub `Footprints` |  |
| **RODO / prywatność** | `ShieldCheck` |  |
| **2FA / bezpieczeństwo** | `KeyRound` |  |
| **Anuluj / usuń** | `X` / `Trash2` |  |
| **Edytuj** | `Pencil` |  |
| **Pobierz PDF** | `Download` |  |
| **Share link** | `Link2` |  |
| **FHIR / medycyna** | `Star` (dla wysłano lekarzowi) |  |

## Marketplace category icons

| Kategoria | Emoji (mockup) | Alternatywa lucide |
|-----------|----------------|-------------------|
| Leki | 💊 | `Pill` |
| Zakupy | 🛒 | `ShoppingCart` |
| Taxi | 🚕 | `Car` |
| Lekarz | 👨‍⚕️ | `Stethoscope` |
| Pielęgniarka | 🧑‍⚕️ | `Syringe` |
| Sprzątanie | 🧹 | `Sparkles` |
| Rehabilitant | 💪 | `Dumbbell` |
| Naprawy | 🔧 | `Wrench` |
| Umów wizytę | 🗓️ | `CalendarClock` |
| Psycholog | 💬 | `MessageCircleHeart` |

**Rekomendacja:** w mockupach użyto emoji dla szybkiego rozpoznania kolorystycznego. W produkcji **wybierz jedną konwencję** dla całego panelu — emoji lub lucide. Miks wygląda nieprofesjonalnie.

**Preferencja produktowa:** lucide-react (spójne, monochrome, łatwe do stylizacji). Emoji mogą pozostać w opinach użytkowników / notatkach kontekstowych opiekuna (ma naturalny UX).

## Rozmiary standardowe

```tsx
<Icon size={12} />  {/* xs — inline z labelami */}
<Icon size={14} />  {/* sm — sidebar nav */}
<Icon size={16} />  {/* md — default buttons */}
<Icon size={18} />  {/* lg — topbar actions */}
<Icon size={22} />  {/* xl — feature cards */}
<Icon size={28} />  {/* 2xl — big empty states */}
```

## Stylizacja

```tsx
// Kolor: dziedziczy z rodzica (currentColor)
<div className="text-granat-700">
  <Phone /> {/* będzie granat-700 */}
</div>

// Stroke width: default 1.5 dla Adam (bardziej editorialne niż default 2)
<Phone strokeWidth={1.5} />
```

## Custom SVG (dla logo Adam)

Logo Adam używa custom SVG (nie lucide):

```html
<!-- Logo mark 32×32 -->
<svg viewBox="0 0 32 32" width="32" height="32">
  <rect width="32" height="32" rx="7" fill="#1a2744"/>
  <rect x="4" y="4" width="24" height="24" rx="4" fill="none" stroke="#c8963e" stroke-width="1"/>
  <text x="16" y="22" font-family="Fraunces" font-size="16" font-weight="500"
        fill="#c8963e" text-anchor="middle" letter-spacing="-0.02em">A</text>
</svg>
```

Zapisz w `public/logo/logo-mark.svg` i `public/logo/logo-full.svg` (mark + wordmark).
