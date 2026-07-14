# Adam · Components Inventory

Katalog wszystkich komponentów zdefiniowanych wizualnie w mockupach. Do zbudowania jako `.tsx` w `src/components/`.

## Struktura folderów

```
src/components/
├── ui/                    # Bazowe (shadcn-style, ale Adam-branded)
├── senior/                # Adam-specific (medycyna, opieka)
├── admin/                 # Panel Admina-specific
├── landing/               # Landing page-specific
└── layout/                # AppShell, Sidebar, Topbar
```

---

## `ui/` — Bazowe komponenty

| Komponent | Referencja | Props |
|-----------|-----------|-------|
| **Button** | Design System · sekcja Buttons | `variant: 'primary' \| 'accent' \| 'ghost' \| 'danger'`, `size: 'xs' \| 'sm' \| 'md' \| 'lg'`, `iconLeft?`, `iconRight?` |
| **Card** | Wszędzie | `variant: 'default' \| 'elevated' \| 'featured'`, `borderColor?` |
| **Input** | Design System · Form fields | `type`, `error?`, `helpText?`, `icon?` |
| **Select** | Panel Opiekuna Ustawienia | Adam-styled dropdown z custom chevron SVG |
| **Switch** | Panel Opiekuna Ustawienia matryca | Radix `<Switch />` z Adam styling · 40×22px |
| **Checkbox** | (rare) | Radix `<Checkbox />` |
| **Radio** | (rare) | Radix `<RadioGroup />` |
| **Textarea** | Notatki kontekstowe | 80px min-height, resize vertical |
| **Badge** (pip) | Wszędzie | `variant: 'green' \| 'yellow' \| 'red' \| 'purple' \| 'info' \| 'neutral' \| 'gold'`, `withDot?` |
| **AlertBanner** | Dashboard krytyczne alerty | `level: 'red' \| 'yellow' \| 'info'`, `title`, `description`, `actions?` |
| **Modal** | (do zbudowania) | Radix Dialog z Adam styling |
| **Tabs** | Widok seniora, Marketplace | Custom underline złoty for active |
| **Tooltip** | Wszędzie | Radix Tooltip |
| **Dropdown** | Actions menus | Radix DropdownMenu |
| **Progress** | Loyalty, calibration, cancellation | Linear + circular variants |
| **Skeleton** | Loading states | Shimmer animation Adam-styled |
| **Toast** | Sonner integration | Adam-styled toasts |
| **Avatar** | Wszędzie | 24/32/48/64/88px sizes, gradient bg default |
| **Icon** | lucide-react wrapper | Consistent sizing, currentColor |

---

## `senior/` — Adam-specific

| Komponent | Referencja | Props |
|-----------|-----------|-------|
| **SemaphoreBadge** | Design System | `level: SemaphoreLevel, label?, size?, pulse?` — **pulse only red/purple** |
| **SeniorCard** | Panel Opiekuna Dashboard | Full senior card z awatarem, semaforem, metrykami |
| **SeniorCardCompact** | Sidebar Konto (Twoi bliscy) | Mini variant |
| **SeniorAvatar** | Wszędzie | `initials`, `size`, `pulseSemaphore?` |
| **MoodChart** | Widok seniora + Raporty | Recharts LineChart z threshold band + alert markers |
| **MoodMiniChart** | Karta seniora | 80×32px inline sparkline |
| **MedicationList** | Widok seniora | Z rozkładem 🌅☀️🌙 |
| **MedicationRing** | Widok seniora Wearable | SVG circle progress · z procentem |
| **MedicationCalendarHeatmap** | Widok seniora Leki tab | 5×7 grid 35 dni |
| **HeartRateChart** | Wearable tab | HR 24h z threshold band + peak markers |
| **SleepPhasesBar** | Wearable tab | Kolorowy pasek Light/Deep/REM/Awake · legenda |
| **StepsWeekly** | Wearable tab | Słupki 7 dni z celem |
| **CalibrationProgress** | Wearables Fleet | "Dzień 8/14" progress bar |
| **ThresholdBadge** | Wearable | `auto` vs `manual_override` styling (złota obwódka + audit info) |
| **AlertTimeline** | Alerty tab, Ekrany krytyczne | Vertical timeline z kolorowymi kropkami · `now` variant pulsuje |
| **ConversationCard** | Widok seniora Rozmowy | Transkrypt + audio player + tools tags |
| **EmergencyContactList** | Widok seniora | Numerowana lista z prioritetami |
| **CriticalAlertBanner** | Dashboard | Full-width alert z akcjami |
| **PhoneNotificationPreview** | Ekrany krytyczne | iOS/Android push mockup — dla settings preview |

---

## `admin/` — Panel Admina-specific

| Komponent | Referencja | Props |
|-----------|-----------|-------|
| **LiveTopology** | Dashboard | 4 nodes (ai_engine, asterisk, local_ai_server, admin_ui) · SSE stream |
| **LogsStream** | Live Logs | WebSocket streaming · filtry level×category · regex search |
| **PromptEditor** | Agent detail | Monaco-like YAML z color-coded syntax + diff view |
| **MarketplaceOrderQueue** | Marketplace | Split akcyjne vs informacyjne · partner card · transcript |
| **ServiceCategoryCard** | Marketplace Katalog | Risk badge (auto/manual/hybrid) · orders 24h |
| **PartnerCard** | Marketplace Partnerzy | NIP + OC verified + rating + skargi + Local Poznań ★ |
| **ServiceGapCard** | Marketplace Service Gaps | Kategoria × dzielnica · count · recommendation |
| **WearablesFleet Table** | Wearables Fleet | 941 devices · kalibracja status · manual override highlight |
| **WearableThresholdOverride** | Wearables detail | Ręczne nadpisanie z audit trail SHA-256 |
| **ProvidersHealthChart** | Providers | Latency p50/p95 real-time · status pip |
| **CostTrackingChart** | Providers | Line chart · margin brutto · budżet |
| **AgentCard** | Agents list | Version, model, voice, calls, rating, deploy history |
| **DockerContainerTile** | Docker | Container status · CPU/RAM · restart/stop actions |
| **EnvVarRow** | Environment | Editable input · type badge · modified state · secret masking |
| **AsteriskStatusCard** | Asterisk | ARI connection, modules, application registration |
| **TerminalPane** | Terminal | Web CLI z komendami `adam ...` · history · autocomplete |

---

## `landing/` — Landing page

| Komponent | Zastosowanie |
|-----------|-------------|
| **HeroEditorial** | Section 1 — asymetryczna typografia + portret + cytat |
| **SignoffMarquee** | Rotujący pasek granatowy z zaletami |
| **ChapterHeader** | "Rozdział 01/02/03" numeracja magazynowa |
| **PullQuote** | Cytaty z drop-cap serifowym |
| **StoryCut** | 08:00/19:00/22:14 story cuts How it works |
| **FeatureCollageCard** | 6-card asymetryczny grid Features |
| **TestimonialQuoteBlock** | Big pull quote na granacie |
| **PricingTierCard** | 3 pricing tiers z hero card middle |
| **PartnerLogoCard** | Partner card w Poznań ecosystem |
| **FinalCTABlock** | "Twój bliski zasługuje na codzienną rozmowę" |
| **FooterMagazine** | 4 kolumny + tagline serif italic |

---

## `layout/` — Layout components

| Komponent | Zastosowanie |
|-----------|-------------|
| **AppShell** | Root layout z sidebar + topbar + main |
| **Sidebar (Opiekun)** | 240px, granat-900 bg, złote akcenty aktywnych, badges |
| **Sidebar (Admin)** | 240px, granat-900 bg, sekcje Overview/Core Config/System, env badge |
| **Topbar** | Search + breadcrumb + actions + notifications |
| **Breadcrumb** | Mono, `/` separator, current bold |
| **SidebarSection** | Header + navigation items |
| **NavItem** | Icon + label + optional badge (count/red for alerts) |
| **MobileBottomNav** | Dla Capacitor iOS/Android — 4 tabs bottom |
| **PageHeader** | H1 + subtitle + actions |
| **SectionHeader** | H2 + link/tabs |

---

## Suma: ~85 komponentów do zbudowania

Rekomendacja podziału pracy:
- **Faza 1 (tydzień 1–2):** Fundament — Design System (`ui/`) + Landing (`landing/`) — ~30 komponentów
- **Faza 2 (tydzień 3–5):** Panel Opiekuna — `senior/` + `layout/` — ~25 komponentów
- **Faza 4 (tydzień 8–10):** Panel Admina — `admin/` + dark mode — ~30 komponentów

Storybook rekomendowany dla `ui/` i `senior/` (najczęściej reużywane).
