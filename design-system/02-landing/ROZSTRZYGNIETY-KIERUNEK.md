# 🎯 Rozstrzygnięty kierunek Landing Page

**Zwycięski wariant:** **Wariant B Editorial** (Nordic humanism full)
**Odrzucony:** Wariant A Instytucjonalny (Medical-premium leaning)
**Data decyzji:** Lipiec 2026

---

## Uzasadnienie

**Wariant B wygrał** ze względu na:

1. **Emocjonalny hook** — asymetryczna typografia + portret editorialny + cytat seniora ("Adam dzwoni codziennie o ósmej. Nie wiem, czy to komputer, ale zawsze pyta, jak spałam.") jako pierwsze wrażenie · Wariant A miał głównie liczby
2. **Storytelling** — magazynowa struktura "Rozdział 01 · 02 · 03" jest bardziej zgodna z misją Adama ("codzienna praktyka opieki, nie aplikacja")
3. **Nordic humanism** = docelowy kierunek wizualny całego brandu (patrz DEVELOPER-HANDOFF)
4. **Airbnb + Apple Health warmth** — target 30-55 lat (dorośli synowie/córki), edukowany w editorialu i storytellingu

**Wariant A** pozostaje jako **referencja stylistyczna** dla:
- Panel Opiekuna (bardziej strukturalne widoki danych)
- Panel Admina (data-dense)
- Wersje B2B (jeśli SilverTech kiedyś zrobi enterprise sales)

---

## Do produkcji

### Zaimplementuj tylko Wariant B (`Landing — Wariant B Editorial.html`)

**Kluczowe sekcje w kolejności:**

1. **Nav** — sticky, backdrop-blur, logo mark + linki + `Zaloguj` + `Zamów Adama →`
2. **Hero editorial** — 1:1 grid:
   - LEWO: eyebrow "Numer 01" + tagline + duży H1 (`Codziennie dzwoni do niej. Ty masz spokój.`) z serif italic akcentem + lead + CTA + meta stats 4×
   - PRAWO: portret placeholder (do zamiany na prawdziwe zdjęcie seniorki z Poznania) + cytat seniora + attribution
3. **Signoff marquee** — granatowy pasek z rotacyjnymi zaletami ("Wykrywa samotność · Przypomina o lekach · Alarmuje w 18s · Zna wielkopolski · Bez smartfona")
4. **Chapter 01: Problem** — 2-column magazine layout · zdjęcie 4:5 + drop-cap pull quote + narracja
5. **Chapter 02: How it works** — 3 story cuts (08:00 · 19:00 · 22:14 · Wtorek 12 lipca) z meta tags
6. **Chapter 03: Features** — asymetryczny 6-card grid (2× wide dark + 4× regular)
7. **Partners section** — "Osiemdziesiąt rąk, jeden Poznań." + 8 kart partnerów + editorial stats footer
8. **Testimonial** — big pull quote na granacie z awatarem MC (Magdalena C.)
9. **Pricing** — 3 tiers z hero card middle (79 zł Rodzinny)
10. **Final CTA** — "Twój bliski zasługuje na codzienną rozmowę."
11. **Footer** — 4 kolumny + tagline "Adam nie jest aplikacją. Jest codzienną praktyką opieki."

---

## Fotografia

**Placeholdery MUSZĄ być zamienione przed launch:**

- Hero portret — starsza kobieta 70+ z Poznania · fotografia editorialna · zgoda na wizerunek podpisana
- Chapter 01 image — kadr niedzielny (rodzina + senior) lub metaforyczny (ręka na telefonie stacjonarnym)
- Partnerzy — jeśli chcesz zdjęcia partnerów SilverTech (DOZ apteka, MPT taxi), poproś o zgody na wizerunek + logo

**Nie używać stocku typu "happy grandma with dentures".** To zabija wiarygodność.

---

## Copy do zamiany (przed launch)

- Ceny: sprawdź czy 49/79/119 zł to finalne
- Numer telefonu: `+48 61 22 44 000` — zweryfikuj z SilverTech
- Adres w footer: `ul. Święty Marcin 24, 61-805 Poznań` — zweryfikuj
- NIP: SilverTech Sp. z o.o. NIP 7831234567 — placeholder, wymień na prawdziwy

---

## SEO/OG

Zanim wdrożenie:

```html
<meta name="description" content="Adam to głosowy asystent, który codziennie dzwoni do Twojej mamy. Sprawdza samopoczucie, przypomina o lekach, alarmuje rodzinę w 18 sekund. SilverTech Poznań.">

<meta property="og:title" content="Adam — Codziennie dzwoni do Twojej mamy">
<meta property="og:description" content="Cyfrowy opiekun rodzinny · SilverTech · 79 zł/mies. · bez umowy">
<meta property="og:image" content="https://adam.silvertech.pl/og-hero.jpg">
<meta property="og:url" content="https://adam.silvertech.pl">

<link rel="canonical" href="https://adam.silvertech.pl">
```

**OG image (1200×630):** wygenerować z hero — portret + tagline overlay.
