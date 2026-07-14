# Adam · SilverTech — Design System Handoff Package

**Wersja:** 1.0
**Data:** Lipiec 2026
**Odbiorca:** GenSpark AI Developer (frontend team)
**Autor designu:** Design Team · SilverTech
**Kierunek wizualny:** Nordic humanism × Medical-premium
**Stack docelowy:** React 18 + TypeScript + Vite + Tailwind CSS + Capacitor (iOS + Android)

---

## 📦 Co jest w tej paczce

Kompletna specyfikacja wizualna systemu Adam (agent głosowy dla seniorów SilverTech) — gotowa do wdrożenia w kodzie produkcyjnym.

```
adam-design-system-2026-07/
├── README.md                       ← Zaczynasz tutaj
├── INSTRUKCJA-WDROZENIA.md         ← Plan 4-fazowy wdrożenia (must-read)
├── DEVELOPER-HANDOFF.md            ← Handoff techniczny + kontrakty
├── CHANGELOG.md                    ← Wersjonowanie designu
├── index.html                      ← Landing z nawigacją po wszystkich mockupach
│
├── 01-design-system/               ← Fundament wizualny
│   ├── Design System.html          ← Live tokens + komponenty
│   ├── tokens.css                  ← CSS variables (do produkcji)
│   ├── tokens.json                 ← JSON dla tooling
│   └── tailwind.config.example.js  ← Gotowa konfiguracja Tailwind
│
├── 02-landing/                     ← Marketing site (2 warianty)
├── 03-panel-opiekuna/              ← B2C · rodzina seniora
├── 04-panel-admina/                ← B2B · koordynator SilverTech
├── 05-krytyczne/                   ← Semafor L3+L4 (RED/PURPLE)
├── 06-deck/                        ← 14-slide strategia wizualna
└── 07-assets/                      ← Kolory, typografia, ikony, komponenty
```

---

## 🚀 Start w 5 minut

1. **Otwórz `index.html`** — nawigacja po wszystkich mockupach
2. **Przeczytaj `INSTRUKCJA-WDROZENIA.md`** — dokładny plan wdrożenia
3. **Skopiuj `01-design-system/tokens.css`** do swojego `src/styles/tokens.css`
4. **Zastąp `tailwind.config.js`** przez `01-design-system/tailwind.config.example.js`
5. **Zainstaluj fonty** — Fraunces + Geist (patrz `07-assets/typography.md`)
6. **Zacznij od Fazy 1** — Design System + Landing (Wariant B)

---

## 🎨 Kluczowe decyzje wizualne (do wdrożenia bez zmian)

| Element | Wartość | Uzasadnienie |
|---|---|---|
| **Primary kolor** | Granat `#1a2744` | Sunk cost w Capacitor splash + status bars |
| **Accent kolor** | Złoto matowe `#c8963e` | Nigdy jako gradient bling — 1px linia, cyfry KPI, hover |
| **Font nagłówki** | Fraunces (Google Fonts, darmowy) | Serif w nagłówkach = podpis Fortune-tier |
| **Font body** | Geist (darmowy, Vercel) | Neo-grotesk, nowoczesny, **nie AI-slop** (nie Inter/Roboto) |
| **Semafor** | 4-kolorowy PROGRESYWNY | Green/Yellow ambient · Red/Purple pulsujący (zapobiega alarm fatigue) |
| **Density** | Balanced (Opiekun) + Data-dense (Admin) | Rodzina potrzebuje powietrza, koordynator potrzebuje danych |
| **Fotografia** | Editorial TYLKO landing · brak w produkcie | Produkt = typografia + data-viz (unika stock-slopu) |
| **Wariant landingu** | **B Editorial** (rozstrzygnięty) | Nordic humanism full · Airbnb + Apple Health warmth |

---

## 📋 Roadmap wdrożenia (skrót)

| Faza | Zakres | Czas | Zależności |
|------|--------|------|-----------|
| **Faza 1** · Design System + Landing | tokens.css, komponenty bazowe, Landing B (editorial) | Tydzień 1–2 | Fonty, hosting |
| **Faza 2** · Panel Opiekuna (React) | Dashboard, Senior detail, Zamówienia, Wiadomości, Raporty, Konto, Ustawienia, Pomoc | Tydzień 3–5 | Faza 1 · API contracts |
| **Faza 3** · Capacitor iOS + Android | PWA manifest + Capacitor wrap + Face ID + Push | Tydzień 6–7 | Faza 2 · App Store / Play konta |
| **Faza 4** · Panel Admina | Migracja z shadcn na Adam DS, dark mode dla Admina | Tydzień 8–10 | Wszystkie powyższe |

**Pełne szczegóły w `INSTRUKCJA-WDROZENIA.md`.**

---

## 🎯 Krytyczne zasady projektowe (nie do złamania)

1. **Semafor progresywny** — Green/Yellow nigdy nie pulsują. Red/Purple zawsze pulsują + banner + SMS. Zapobiega alarm fatigue.
2. **Purple zawsze bypass DND** — na iOS/Android push level `critical` dla Purple, `default` dla Red, `passive` dla Yellow/Green.
3. **Adam ma 1 numer telefonu** — nie osobny "concierge number". Senior mentalnie nie zapamięta drugiego.
4. **Opiekun NIE edytuje progów medycznych wearables** — tylko koordynator SilverTech / lekarz przez FHIR. Opiekun dodaje "notatki kontekstowe" (soft context) nie parametry.
5. **Marketplace hybrid confirmation** — auto (taxi/apteka/spożywcze) vs manual (lekarz/pielęgniarka/naprawy). Kolumny widoczne w Admin panelu.
6. **RODO wykluczenia z MVP** — opłata rachunków, przelewy finansowe = wektor oszustw. Faza 3+.
7. **Fraunces w cyfrach KPI, nie w Geist** — to sygnatura Fortune-tier (FT/NYT-like).
8. **Złoto nigdy jako gradient** — matowe 1px linie, cyfry, akcenty. Nigdy jako "casino gold".

---

## 📞 Kontakt

- **Design lead:** design@silvertech.pl
- **Product lead:** product@silvertech.pl
- **Tech lead:** tech@silvertech.pl
- **Slack channel:** `#adam-frontend`
- **Figma (jeśli będzie):** patrz `INSTRUKCJA-WDROZENIA.md` sekcja "Design ops"

---

## 📝 Licencje

- Fonty: **Fraunces + Geist Mono** — SIL OFL (darmowe komercyjne)
- **Geist Sans** — SIL OFL (Vercel)
- Design tokens + komponenty: proprietary SilverTech (do wewnętrznego użycia)

---

**Ostatnie kluczowe zdanie:** *Adam nie jest aplikacją. Jest codzienną praktyką opieki. Interfejs ma to wspierać, nie zastępować.*
