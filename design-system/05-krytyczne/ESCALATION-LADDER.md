# Escalation Ladder · Semafor Progresywny

Dokument referencyjny dla implementacji semafora 4-poziomowego.

**Plik demo:** `Ekrany Alertów Krytycznych.html`
**Adam spec:** Faza F3 (Czterokolorowy Semafor Eskalacji)

---

## Zasada projektowa (nie do złamania)

> **Alarm ma siłę.** Semafor jest progresywny. Zieleń szepcze, purpura krzyczy. Nigdy odwrotnie. Nigdy w tej samej intensywności.

**Wynik:** zapobiega **alarm fatigue** — gdy opiekun widzi pulsowanie codziennie przy stanie normalnym, przestaje reagować na realny alarm.

---

## Poziomy

### 🟢 Level 1 · GREEN · Spokojnie

**Trigger:**
- Welfare check OK (mood ≥0.6, leki wzięte, samopoczucie dobre)
- Wearable w normie
- Brak wykrytych sygnałów niepokoju

**Response:**
- Log w bazie
- Panel Opiekuna aktualizuje semafor (via SSE)
- **Zero notyfikacji push/SMS** (jeśli opiekun ustawił Green=on w matrycy powiadomień, wtedy passive push tylko w godzinach aktywnych)

**Wizualnie:**
- Statyczna 3px wstęga po lewej stronie karty seniora
- Zielona ikona statusu (nie pulsuje)
- Badge `.pip.green` w tabelach

**MTTA target:** brak (nie jest alertem)

---

### 🟡 Level 2 · YELLOW · Uważaj

**Trigger:**
- Mood <0.5
- Wykryty sygnał samotności ("wnuki dawno nie dzwoniły", "nikt nie odwiedza")
- Pominięta 1 dawka leków
- Sen <6h powtarzalny 3+ dni
- HR chronicznie podwyższone (baseline +15%)

**Response:**
- Log + panel update
- **Push do rodziny** (bez wibracji nocą, respect quiet hours)
- SMS opcjonalny (tylko jeśli włączony w matrycy)
- Sugestia w powiadomieniu ("Warto zadzwonić do mamy w tym tygodniu")

**Wizualnie:**
- 3px żółta wstęga
- Badge z ikoną ostrzeżenia
- **NIE pulsuje** (ambient)

**MTTA target:** 2h (informational, nie krytyczne)

---

### 🔴 Level 3 · RED · Alarm

**Trigger:**
- **Wykryto upadek** (Xiaomi Band / Apple Watch fall detection)
- **HR >140** przez >2 min bez kontekstu aktywności
- **Ból w klatce piersiowej** (werbalny · pattern match Adam guardrails)
- **Pominięte 2+ dawki leków** w ciągu doby
- **Adam nie może się dodzwonić** 3× w odstępach 20s
- SpO₂ <92% przez >5 min

**Response (KRYTYCZNE — od 0s):**
```
t=0s      Log + panel update
t=0s      Adam próbuje dodzwonić (próba 1)
t=20s     Adam retry (próba 2)
t=40s     Adam retry (próba 3)
t=60s     ⚠ Nie odebrał 3 razy:
          → SMS + push CRITICAL do rodziny (wszyscy opiekunowie)
          → Powiadomienie koordynatora SilverTech
          → SSE push aktualizuje Panel Admina
t=60-120s Koordynator ma 60s na przejęcie ticketu
t=120s    Jeśli koordynator nie potwierdza → auto-escalate do PURPLE
```

**Wizualnie:**
- **Pulsujący pierścień wokół awatara** (semaphore-pulse-ring keyframe)
- Gradient tła karty (linear-gradient(90deg, sem-red-bg 0%, white 40%))
- Banner z akcją "Zadzwoń" / "Otwórz szczegóły"
- Badge `.pip.red` z animacją `sem-dot-pulse`

**MTTA target:** **18 sekund** (od trigger do SMS rodzinie)

**iOS Push:**
```json
{
  "aps": {
    "alert": { "title": "🔴 Alarm — Maria N.", "body": "Wykryto upadek..." },
    "sound": { "critical": 0, "name": "alarm.wav", "volume": 1.0 },
    "interruption-level": "time-sensitive"
  }
}
```

**Android Push:** priority `high`, channel `adam-alert`, vibration `[500, 300, 500, 300, 500]`

---

### 🟣 Level 4 · PURPLE · Krytyczne (zagrożenie życia)

**Trigger:**
- **AFib + symptomy werbalne** ("duszność", "ból serca")
- **Utrata przytomności** (brak ruchu >5 min + puls poza normą)
- **Samobójcze ideje** (Adam wykrywa pattern w rozmowie)
- **RED nierozwiązany >15 min** (auto-escalation)
- **Aktywacja SOS** przez seniora (jeśli Xiaomi Band z SOS button)

**Response (0s):**
```
t=0s   Wszystko z Red +
t=0s   🚨 Auto-dial 112 (Adam dzwoni do dyspozytora):
       → Podaje pełny adres seniora
       → Wiek, choroby (arytmia, cukrzyca, nadciśnienie)
       → Aktualne leki (dla ratowników)
       → Numer telefonu do rodziny
t=0s   LIVE feed dla rodziny + koordynatora:
       → Panel Opiekuna pokazuje ekran z chronologią + karetka ETA
       → Repeat push notification co 30s aż potwierdzone
t=42s  Docelowe MTTA rodziny (SMS + push critical bypass DND)
```

**Wizualnie:**
- **Pulsujący pierścień wokół awatara** (silniejszy niż RED)
- Gradient tła purpura + akcent
- **LIVE badge** z pulsującą kropką
- Banner "🚨 112 W DRODZE · ETA X min" z live countdown
- Cała karta ma nadrzędny priorytet w liście

**MTTA target:** **42 sekundy** (od trigger do potwierdzenia karetki)

**iOS Push:** wymaga **CriticalAlert entitlement** (wniosek Apple):
```json
{
  "aps": {
    "alert": { "title": "🟣 KRYTYCZNE — Stanisław Z.", "body": "112 wezwane..." },
    "sound": { "critical": 1, "name": "critical-alarm.wav", "volume": 1.0 },
    "interruption-level": "critical"
  }
}
```

**Android Push:** priority `max`, channel `adam-critical` (bypass DND user cannot disable), vibration `[1000, 200, 1000, 200, 1000]`, repeat until acknowledged.

---

## Statystyki celu

| Poziom | Częstotliwość target | % wszystkich alertów |
|--------|----------------------|---------------------|
| Green  | 96% dni normalnych  | 96% |
| Yellow | 2-3× tygodniowo per senior | 3% |
| Red    | 1-2× miesięcznie per senior | 0.7% |
| Purple | ~0.3% wszystkich alertów | 0.3% |

**Cel:** Purple to <1% wszystkich alertów — jeśli więcej, coś jest źle skonfigurowane (progi za wąskie, false-positive fall detection, itp.).

---

## State machine (implementacja)

```typescript
// src/lib/semaphore/state-machine.ts
type SemaphoreLevel = 'green' | 'yellow' | 'red' | 'purple';

interface SemaphoreEvent {
  seniorId: string;
  trigger: string;
  currentLevel: SemaphoreLevel;
  newLevel: SemaphoreLevel;
  context: Record<string, any>;
}

const TRANSITIONS: Record<string, SemaphoreLevel> = {
  // Direct triggers to RED
  'fall_detected': 'red',
  'hr_above_140_sustained': 'red',
  'chest_pain_verbal': 'red',
  'meds_missed_2_plus': 'red',
  'no_answer_3_retries': 'red',
  
  // Direct triggers to PURPLE
  'afib_with_symptoms': 'purple',
  'unconscious_prolonged': 'purple',
  'suicide_ideation': 'purple',
  'sos_button_pressed': 'purple',
  
  // De-escalation
  'welfare_ok': 'green',
  'family_confirmed_ok': 'green',
  'coordinator_resolved': 'green',
};

const AUTO_ESCALATIONS = [
  {
    from: 'red',
    to: 'purple',
    condition: 'unresolved_for_ms',
    threshold: 15 * 60 * 1000,   // 15 min
  },
  {
    from: 'yellow',
    to: 'red',
    condition: 'unresolved_for_ms',
    threshold: 6 * 60 * 60 * 1000, // 6h
    onlyIf: (ctx) => ctx.moodDropRate > 0.2,
  },
];
```

---

## UI acceptance criteria

- [ ] Green + Yellow **NIGDY** nie pulsują (weryfikacja `getComputedStyle`)
- [ ] Red + Purple **ZAWSZE** pulsują (2 keyframes: dot + ring)
- [ ] Purple ma silniejszą wizualną intensywność niż Red (większy ring, gradient background)
- [ ] Timeline dla RED/PURPLE pokazuje **chronologię minutę po minucie**
- [ ] Cancel button dostępny w oknie 30 min dla ORDERS (nie dla alertów)
- [ ] `aria-live="assertive"` dla RED/PURPLE alertów (screen readers)
- [ ] `aria-live="polite"` dla YELLOW
- [ ] Brak `aria-live` dla GREEN (nie przeszkadzać)
