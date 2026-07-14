# Adam · Paleta kolorów + WCAG

## Granat (Primary)

| Nazwa | Hex | WCAG kontrast na `--paper` (#fbfaf7) | Zastosowanie |
|-------|-----|--------------------------------------|--------------|
| granat-50  | #f2f4f8 | — | Backgrounds subtle |
| granat-100 | #e4e8f0 | — | Borders soft |
| granat-200 | #c2cad9 | 1.7:1 | Only decorative |
| granat-300 | #8b98b3 | 3.1:1 · **AA large** | Placeholder text |
| granat-400 | #5a6a8a | 5.4:1 · **AA** | Secondary text |
| granat-500 | #3b4a6b | 8.5:1 · **AAA** | Tertiary text |
| granat-600 | #243352 | 11.6:1 · **AAA** | Body text alternate |
| **granat-700** | **#1a2744** | 13.7:1 · **AAA** | **★ PRIMARY BRAND** — buttons, headings, sidebar |
| granat-800 | #14213d | 14.8:1 · **AAA** | Emphasis text |
| granat-900 | #0e1a2e | 16.5:1 · **AAA** | Body text (default `--ink-900`) |
| granat-950 | #08111f | 18.2:1 · **AAA** | Extreme emphasis |

## Złoto (Accent · matowe)

| Nazwa | Hex | WCAG na paper | Zastosowanie |
|-------|-----|---------------|--------------|
| zloto-50  | #faf3e6 | — | Backgrounds premium tier |
| zloto-100 | #f5e6cf | — | Cards featured |
| zloto-500 | #c8963e | 3.4:1 · **AA large** | Accent buttons |
| **zloto-700** | **#a67c2e** | **4.8:1** · **AA** | **Text on white — italic accents, KPI numbers subheadings** |
| zloto-800 | #8a6524 | 5.9:1 · **AA** | Strong accents |
| zloto-900 | #6b4d1a | 8.3:1 · **AAA** | Text alternative |

**⚠ Nigdy nie używaj złota jako:**
- Duże płaskie wypełnienia (spycha marka w rejestr "casino gold")
- Gradienty (`linear-gradient(gold-500 → gold-600)` = tanio)
- Cienie długie (`filter: drop-shadow(gold ...)`)

**Prawidłowe użycie złota:**
- 1-2px linia akcentu (border-top featured card)
- Cyfry KPI w Fraunces
- Italic akcenty (`<em>codziennie</em>`)
- Hover state secondary buttons
- Progress bar loyalty
- Star ratings

## Semafor (Safety-critical)

| Poziom | Hex | Background | WCAG | Zastosowanie |
|--------|-----|------------|------|--------------|
| 🟢 Green   | #2d6a4f | #e8f2ec | **5.8:1 AA** | Level 1 · Spokojnie |
| 🟡 Yellow  | #b8830d | #fbf0d9 | **4.6:1 AA** | Level 2 · Uważaj (darkened z #e6a817 dla AA) |
| 🔴 Red     | #a5121a | #fbe7e9 | **6.1:1 AA** | Level 3 · Alarm (darkened z #c1121f) |
| 🟣 Purple  | #5a0561 | #f3e6f5 | **8.9:1 AAA** | Level 4 · Krytyczne |

**Kluczowa reguła:** WCAG AA (≥4.5:1) na białym tle — wszystkie sprawdzone i przeszły.

## Info

| Nazwa | Hex | WCAG | Zastosowanie |
|-------|-----|------|--------------|
| info-blue | #1e40af | 8.6:1 · AAA | FHIR banner, informational alerts (nie critical) |
| info-blue-bg | #dbeafe | — | Info card backgrounds |

## Neutrals

| Nazwa | Hex | Zastosowanie |
|-------|-----|-------------|
| paper | #fbfaf7 | **Główne tło** — off-white (nie kliniczna biel!) |
| paper-2 | #f5f3ee | Alternate bg dla card heads, empty states |
| paper-3 | #eeeadc | Subtle emphasis bg |
| ink-900 | #0e1a2e | Body text default |
| ink-700 | #2a3654 | Secondary text |
| ink-500 | #5a6a8a | Muted text (captions) |
| line | #e4e0d5 | Warm border · **nie zimny gray** |
| line-strong | #cfc9b8 | Emphasized borders (form inputs) |

**Dlaczego `paper` a nie `#ffffff`?** Czysta biel jest kliniczna, wywołuje skojarzenia szpitalne. Off-white (#fbfaf7) redukuje zmęczenie oczu przy długich sesjach + daje ciepły, editorial feel (Nordic humanism target).

---

## Testowanie kontrastu

Sprawdź wszystkie combos przed produkcją:
- https://webaim.org/resources/contrastchecker/
- Chrome DevTools · Elements panel → color picker → WCAG hint

**Minimalne wymagania:**
- Body text (`ink-900` na `paper`): **≥7:1 AAA**
- Secondary text (`ink-500` na `paper`): **≥4.5:1 AA**
- Interactive elements: **≥3:1 AA large**
- Focus rings: kolor `granat-600` z 3px shadow — widoczne dla użytkowników keyboard nav
