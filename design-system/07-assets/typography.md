# Adam · Typography Setup

**Fonts:** Fraunces (serif) + Geist (sans + mono) — **oba darmowe**, licencja SIL OFL, komercyjne OK.

## Dlaczego te fonty

- **Nie Inter/Roboto** — te są AI-slop, każda generyczna aplikacja ich używa
- **Fraunces** — serif z osobowością, variable font (opsz axis) · Google Fonts
- **Geist** — nowoczesny neo-grotesk (Vercel 2023) · humanistyczny, ciepły · dobrze czyta się w małych rozmiarach
- **Geist Mono** — dla mono use cases (labels, code, numbers w tabelach)

## Instalacja — opcja A: Google Fonts CDN (najprostsze)

```html
<!-- W public/index.html lub Vite index.html -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link
  href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,ital,wght@9..144,0,300;9..144,0,400;9..144,0,500;9..144,0,600;9..144,0,700;9..144,1,400;9..144,1,500&family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap"
  rel="stylesheet">
```

**Zalety:** brak setup, auto-cache CDN.
**Wady:** wymaga internetu (problematyczne dla PWA offline first-load).

## Instalacja — opcja B: Self-hosted (dla PWA offline)

### 1. Pobierz fonty

```bash
# Fraunces
curl -o public/fonts/Fraunces.woff2 "https://fonts.googleapis.com/css2?family=Fraunces:opsz,ital,wght@9..144,0,400..700;9..144,1,400..500"

# Geist (npm package)
pnpm add @vercel/font-geist
```

### 2. Umieść w `public/fonts/`

```
public/fonts/
├── Fraunces-VariableFont_SOFT,WONK,opsz,wght.woff2
├── Fraunces-Italic-VariableFont_SOFT,WONK,opsz,wght.woff2
├── Geist-Variable.woff2
├── Geist-Mono-Variable.woff2
```

### 3. Dodaj `@font-face` w `src/styles/globals.css`

```css
@font-face {
  font-family: 'Fraunces';
  src: url('/fonts/Fraunces-VariableFont_SOFT,WONK,opsz,wght.woff2') format('woff2-variations');
  font-weight: 300 700;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'Fraunces';
  src: url('/fonts/Fraunces-Italic-VariableFont_SOFT,WONK,opsz,wght.woff2') format('woff2-variations');
  font-weight: 300 700;
  font-style: italic;
  font-display: swap;
}

@font-face {
  font-family: 'Geist';
  src: url('/fonts/Geist-Variable.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'Geist Mono';
  src: url('/fonts/Geist-Mono-Variable.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
```

## Type scale (implementacja)

Wszystkie zdefiniowane w `tokens.css` jako `--text-*` variables + w `tailwind.config` jako `fontSize`.

### Kluczowe zasady:

1. **Serif w nagłówkach + cyfrach KPI** — signature Adama (Fraunces)
2. **Serif italic w akcentach** — `<em>codziennie</em>` → color `zloto-700`, italic
3. **Sans w body i UI** — Geist
4. **Mono w labelach, captionach, cyfrach w tabelach** — Geist Mono z `letter-spacing: 0.06em` uppercase

### Fraunces `opsz` axis (kluczowe dla optymalnej estetyki)

Fraunces jest variable font z osi `opsz` (optical size). Musisz ustawiać `font-variation-settings` per rozmiar:

```css
h1 { font-variation-settings: 'opsz' 144; }  /* Display 84px+ */
h2 { font-variation-settings: 'opsz' 100; }  /* H1 56px */
h3 { font-variation-settings: 'opsz' 60;  }  /* H2 40px */
h4 { font-variation-settings: 'opsz' 36;  }  /* H3 28px */
h5 { font-variation-settings: 'opsz' 24;  }  /* H4 20px */
```

**Bez tego** litery wyglądają za "grube" w małych rozmiarach i za "cienkie" w wielkich.

### Sygnatura brand: cyfry w Fraunces (nie Geist)

```tsx
// ✅ POPRAWNIE (Fraunces w KPI)
<div className="font-serif text-5xl font-medium tracking-tight">
  96<span className="text-zloto-700 text-lg">%</span>
</div>

// ❌ ŹLE (Geist w KPI)
<div className="text-5xl font-bold">
  96%
</div>
```

**Dlaczego:** Serif w cyfrach → skojarzenie z gazetami finansowymi (Financial Times, NYT). Fortune-tier. Sans w cyfrach → generyczny SaaS.

## Fallbacki

Jeśli Fraunces / Geist nie załadują się (offline, adblock CDN):

```css
--font-serif: 'Fraunces', 'Iowan Old Style', Georgia, serif;
--font-sans:  'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono:  'Geist Mono', 'SF Mono', Menlo, monospace;
```

Iowan Old Style (macOS system serif) i Georgia (Windows/Linux) są najbliższymi Fraunces charakterem. System sans jest akceptowalnym fallbackiem dla Geist.

## Testy

- [ ] `document.fonts.ready` — sprawdź w console
- [ ] `getComputedStyle(el).fontFamily` — musi być `Fraunces` lub `Geist` (nie fallback)
- [ ] Lighthouse — sprawdź "Ensure text remains visible during webfont load" (font-display: swap)
- [ ] PWA offline — po drugim odwiedzeniu, fonty załadowane z cache Service Worker
