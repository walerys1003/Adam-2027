🎯 KOMPLETNA SPECYFIKACJA — PANEL OPIEKUNA, LANDING PAGE, RBAC
CZĘŚĆ I: PANEL OPIEKUNA / RODZINY — PEŁNA SPECYFIKACJA
I.A. ARCHITEKTURA NAWIGACJI I EKRANÓW
PANEL OPIEKUNA — MAPA EKRANÓW
══════════════════════════════════
/login                          → Ekran logowania
/login/reset-password           → Reset hasła
/login/request-access           → "Poproś o dostęp do bliskiego"
/panel                          → Dashboard opiekuna (lista seniorów)
/panel/senior/:id               → Widok szczegółowy seniora
/panel/senior/:id/rozmowy       → Historia rozmów (pełna)
/panel/senior/:id/leki          → Panel leków (szczegółowy)
/panel/senior/:id/alerty        → Historia alertów
/panel/senior/:id/raporty       → Raporty tygodniowe/miesięczne
/panel/ustawienia               → Ustawienia konta opiekuna
/panel/ustawienia/powiadomienia → Preferencje powiadomień
/panel/pomoc                    → Jak korzystać z panelu
I.B. EKRAN 1: LOGOWANIE OPIEKUNA
Ścieżka: /login
Komponenty:
LoginPage/
├── LoginPage.tsx               # Kontener strony
├── LoginForm.tsx               # Formularz logowania
├── LoginMethodToggle.tsx       # Przełącznik: email / kod SMS
├── EmailPasswordFields.tsx     # Pola email + hasło
├── SmsCodeFields.tsx           # Pole telefonu + kod SMS
├── SocialProof.tsx             # "Zaufało nam 200+ rodzin..."
├── LoginFooter.tsx             # Linki: reset hasła, poproś o dostęp
└── LoginIllustration.tsx       # Ilustracja (starsza osoba + telefon)
Wygląd:
┌──────────────────────────────────────────────────────┐
│                                                      │
│   ┌───────────────────┐    ┌──────────────────────┐  │
│   │                   │    │                      │  │
│   │   [ILUSTRACJA]    │    │  👋 Witaj w Panelu   │  │
│   │   Senior +        │    │     Opiekuna Adama   │  │
│   │   telefon +       │    │                      │  │
│   │   wnuczka         │    │  Zaloguj się, żeby   │  │
│   │                   │    │  sprawdzić, jak      │  │
│   │                   │    │  czuje się Twój      │  │
│   │                   │    │  bliski.             │  │
│   └───────────────────┘    │                      │  │
│                            │  [Email / SMS] 🔄    │  │
│                            │                      │  │
│                            │  ┌────────────────┐  │  │
│                            │  │ adres@email.pl │  │  │
│                            │  └────────────────┘  │  │
│                            │  ┌────────────────┐  │  │
│                            │  │ ••••••••••      │  │  │
│                            │  └────────────────┘  │  │
│                            │                      │  │
│                            │  [  ZALOGUJ SIĘ  ]   │  │
│                            │                      │  │
│                            │  Nie pamiętasz hasła? │  │
│                            │  Poproś o dostęp →    │  │
│                            └──────────────────────┘  │
│                                                      │
│  "Zaufało nam 200+ rodzin. Codziennie dbamy          │
│   o bezpieczeństwo seniorów w całej Polsce."         │
│                                                      │
└──────────────────────────────────────────────────────┘
API Endpointy:
// backend/app/api/v1/auth.py
POST /api/v1/auth/caregiver/login
  Body: { email: string, password: string }
  Response: { access_token: string, refresh_token: string, caregiver: CaregiverProfile }
  Errors: 401 (nieprawidłowe dane), 403 (konto nieaktywne)
POST /api/v1/auth/caregiver/login/sms
  Body: { phone_number: string }
  Response: { message: "Kod SMS wysłany", expires_in: 300 }
  // Po wpisaniu kodu:
POST /api/v1/auth/caregiver/verify-sms
  Body: { phone_number: string, code: string }
  Response: { access_token: string, caregiver: CaregiverProfile }
POST /api/v1/auth/caregiver/reset-password
  Body: { email: string }
  Response: { message: "Link do resetu hasła wysłany na email" }
POST /api/v1/auth/caregiver/reset-password/confirm
  Body: { token: string, new_password: string }
  Response: { message: "Hasło zmienione" }
Stany UI:
| Stan | Co pokazać |
| Domyślny | Pusty formularz, ilustracja |
| Ładowanie | Spinner na przycisku “Zaloguj się”, disabled |
| Błąd | Czerwony banner: “Nieprawidłowy email lub hasło. Spróbuj ponownie.” |
| Sukces | Przekierowanie na /panel po 0.5s |
| Kod SMS wysłany | “Wysłaliśmy kod na numer +48••••••. Wpisz go poniżej.” + pole na 6 cyfr + timer (5:00) |
| Kod SMS wygasł | “Kod wygasł. Wyślij ponownie.” + przycisk |
| Brak dostępu | “Twoje konto nie ma przypisanych seniorów. Poproś o dostęp.” + link |
I.C. EKRAN 2: “POPROŚ O DOSTĘP”
Ścieżka: /login/request-access
Wygląd:
┌──────────────────────────────────────────────────────┐
│                                                      │
│  📋 Poproś o dostęp do seniora                       │
│                                                      │
│  Wypełnij formularz. Opiekun seniora (np. syn/       │
│  córka) zatwierdzi Twój dostęp i otrzymasz login.    │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │ Imię i nazwisko *                             │    │
│  │ ┌──────────────────────────────────────────┐ │    │
│  │ │ Anna Nowak                               │ │    │
│  │ └──────────────────────────────────────────┘ │    │
│  │                                              │    │
│  │ Twój email lub telefon *                     │    │
│  │ ┌──────────────────────────────────────────┐ │    │
│  │ │ anna.nowak@email.pl                      │ │    │
│  │ └──────────────────────────────────────────┘ │    │
│  │                                              │    │
│  │ Imię i nazwisko seniora *                    │    │
│  │ ┌──────────────────────────────────────────┐ │    │
│  │ │ Jan Kowalski                             │ │    │
│  │ └──────────────────────────────────────────┘ │    │
│  │                                              │    │
│  │ Kim jesteś dla seniora? *                   │    │
│  │ ┌──────────────────────────────────────────┐ │    │
│  │ │ Wnuczka                              ▾   │ │    │
│  │ └──────────────────────────────────────────┘ │    │
│  │                                              │    │
│  │ Wiadomość (opcjonalnie)                      │    │
│  │ ┌──────────────────────────────────────────┐ │    │
│  │ │ Chciałabym mieć podgląd stanu zdrowia    │ │    │
│  │ │ dziadka, bo mieszkam daleko...           │ │    │
│  │ └──────────────────────────────────────────┘ │    │
│  │                                              │    │
│  │ ✅ Wyrażam zgodę na przetwarzanie danych...  │    │
│  │                                              │    │
│  │ [       WYŚLIJ PROŚBĘ       ]               │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
└──────────────────────────────────────────────────────┘
API Endpoint:
POST /api/v1/auth/caregiver/request-access
  Body: {
    requester_name: string,
    requester_contact: string,  // email lub telefon
    senior_name: string,
    relationship: "daughter" | "son" | "granddaughter" | "grandson" | "neighbor" | "friend" | "other",
    message?: string,
    consent_given: boolean
  }
  Response: { message: "Prośba wysłana. Opiekun główny otrzyma powiadomienie." }
I.D. EKRAN 3: DASHBOARD OPIEKUNA
Ścieżka: /panel
Komponenty:
DashboardPage/
├── DashboardPage.tsx              # Kontener
├── DashboardHeader.tsx            # Powitanie + data + przycisk "Pomoc"
├── SeniorCardGrid.tsx             # Siatka kafelków seniorów
├── SeniorCard.tsx                 # Pojedynczy kafelek seniora
│   ├── SeniorAvatar.tsx           # Awatar (inicjały na kolorowym tle)
│   ├── SemaphoreBadge.tsx         # Kolorowe kółko semafora (pulsujące dla RED/PURPLE)
│   ├── LastContact.tsx            # "Ostatnia rozmowa: 2h temu"
│   └── MoodIndicator.tsx          # Emotka nastroju 😊 😐 😟
├── AlertBanner.tsx                # Banner alertów (jeśli YELLOW+ dla dowolnego seniora)
├── QuickSummary.tsx               # "Dziś: 3 rozmowy, 100% leków, bez alertów"
└── EmptyState.tsx                 # Gdy brak przypisanych seniorów
Wygląd:
┌──────────────────────────────────────────────────────────────┐
│  🧑‍🦳 Adam · Panel Opiekuna                  🔔 2   👤 AN  ▾ │
│──────────────────────────────────────────────────────────────│
│                                                              │
│  Dzień dobry, Anno! 👋                   📅 12 lipca 2026   │
│  Twoi bliscy są pod opieką Adama.                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ ⚠️ UWAGA: Jan Kowalski ma status 🔴 UWAŻAJ.         │    │
│  │ Ostatnia rozmowa wykazała obniżony nastrój.           │    │
│  │                                       [Sprawdź →]    │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─── Dziś ────────────────────────────────────────────┐    │
│  │  📞 2 rozmowy  ·  💊 100% leków  ·  😊 nastrój 7/10│    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐   │
│  │    JK           │  │    ZN           │  │    MK       │   │
│  │ Jan Kowalski    │  │ Zofia Nowak     │  │ Maria K.    │   │
│  │                 │  │                 │  │             │   │
│  │      🔴         │  │      🟢         │  │      🟡      │   │
│  │   Ostatnio:     │  │   Ostatnio:     │  │  Ostatnio:  │   │
│  │   2 godz. temu  │  │   3 godz. temu  │  │  1 godz. temu│   │
│  │   Nastrój: 😟   │  │   Nastrój: 😊   │  │  Nastrój: 😐 │   │
│  │                 │  │                 │  │             │   │
│  │ [Szczegóły →]   │  │ [Szczegóły →]   │  │[Szczegóły →]│   │
│  └─────────────────┘  └─────────────────┘  └────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
API Endpoint:
GET /api/v1/caregiver/dashboard
  Headers: Authorization: Bearer <token>
  Response: {
    caregiver: {
      first_name: string,
      last_name: string,
      unread_alerts: number
    },
    seniors: [
      {
        id: string,
        first_name: string,
        last_name: string,
        semaphore: "green" | "yellow" | "red" | "purple",
        last_contact_at: string,        // ISO datetime
        last_mood_score: number | null,  // 1-10
        last_mood_emoji: string,         // 😊 😐 😟 😢
        today_calls: number,
        today_medication_rate: number,   // 0-100
        has_active_alert: boolean
      }
    ],
    daily_summary: {
      total_calls: number,
      avg_mood: number,
      avg_medication_rate: number,
      active_alerts: number
    }
  }
I.E. EKRAN 4: WIDOK SZCZEGÓŁOWY SENIORA
Ścieżka: /panel/senior/:id
To najważniejszy ekran — centrum dowodzenia opiekuna.
Komponenty:
SeniorDetailPage/
├── SeniorDetailPage.tsx            # Kontener + routing podstron
├── SeniorHeader.tsx                # Nagłówek z danymi seniora
│   ├── SemaphoreHero.tsx           # Duży, animowany semafor
│   ├── SeniorInfoBar.tsx           # Imię, wiek, adres, telefon
│   └── QuickActions.tsx            # "Poproś o kontakt" / "Zgłoś problem"
├── TabNavigation.tsx               # Zakładki: Przegląd | Rozmowy | Leki | Alerty | Raporty
│
├── OverviewTab.tsx                 # ZAKŁADKA "Przegląd"
│   ├── MoodChartMini.tsx           # Miniwykres nastroju (14 dni)
│   ├── RecentConversations.tsx     # Ostatnie 3 rozmowy (rozwijane)
│   ├── MedicationWidget.tsx        # Wskaźnik kołowy leków + lista
│   ├── AlertTimeline.tsx           # Ostatnie alerty (timeline)
│   └── WeeklySummaryCard.tsx       # Podsumowanie tygodnia
│
├── ConversationsTab.tsx            # ZAKŁADKA "Rozmowy"
│   ├── ConversationsFilter.tsx     # Filtry: data, nastrój, typ
│   ├── ConversationList.tsx        # Lista rozmów
│   └── ConversationDetail.tsx      # Modal/rozwinięcie: pełny transkrypt
│
├── MedicationsTab.tsx              # ZAKŁADKA "Leki"
│   ├── AdherenceChart.tsx          # Wykres słupkowy: 7/14/30 dni
│   ├── MedicationList.tsx          # Lista leków z dawkami i porami
│   └── MissedDosesLog.tsx          # Lista pominiętych dawek
│
├── AlertsTab.tsx                   # ZAKŁADKA "Alerty"
│   ├── AlertsFilter.tsx            # Filtry: poziom, data
│   ├── AlertList.tsx               # Lista alertów
│   └── AlertDetail.tsx             # Szczegóły alertu (co go wywołało)
│
└── ReportsTab.tsx                  # ZAKŁADKA "Raporty"
    ├── WeeklyReport.tsx            # Raport tygodniowy (tekstowy + metryki)
    ├── MonthlyReport.tsx           # Raport miesięczny
    └── ExportButton.tsx            # Eksport do PDF
Wygląd — Zakładka “Przegląd”:
┌──────────────────────────────────────────────────────────────┐
│  ← Powrót                                                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │    ┌─────┐    Jan Kowalski                          │    │
│  │    │ JK  │    78 lat · Poznań, ul. Słoneczna 12     │    │
│  │    └─────┘    ☎ +48 501 002 003                     │    │
│  │                                                      │    │
│  │          🔴                                         │    │
│  │      STATUS: UWAŻAJ                                  │    │
│  │   Ostatnia rozmowa: 2 godziny temu                   │    │
│  │                                                      │    │
│  │   [ Poproś o kontakt ]    [ Zgłoś problem ]          │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  [ Przegląd ]  [ Rozmowy ]  [ Leki ]  [ Alerty ]  [ Raporty ]│
│  ─────────────────────────────────────────────────────────   │
│                                                              │
│  ┌── Nastrój (ostatnie 14 dni) ─────────────────────────┐   │
│  │                                                      │   │
│  │  10┤                                          ●      │   │
│  │    │                                ●──●             │   │
│  │   8┤      ●──●──●        ●──●                       │   │
│  │    │    ●          ●──●                              │   │
│  │   6┤                              ●──●               │   │
│  │    │                                        ●──●     │   │
│  │   4┤                                                │   │
│  │    │                              ⚠ moment spadku   │   │
│  │   2┤                                                │   │
│  │    └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───   │   │
│  │    1  3  5  7  9  11 13 15 17 19 21 23 25 27       │   │
│  │                                                      │   │
│  │  Średnia: 6.8/10  ·  Trend: 📉 lekki spadek          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌── Ostatnie rozmowy ──────────────────────────────────┐   │
│  │                                                      │   │
│  │  📞 Dzisiaj, 09:15  ·  😟 Nastrój 4/10  ·  8 min    │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │ Adam: Dzień dobry Panie Janie, jak się Pan   │    │   │
│  │  │ dzisiaj czuje?                                │    │   │
│  │  │ Senior: A wie pan... Jakoś kiepsko. Kolano    │    │   │
│  │  │ znowu boli, nie mogłem spać...                │    │   │
│  │  │ [rozwiń cały transkrypt ▾]                    │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  📞 Wczoraj, 09:22  ·  😐 Nastrój 6/10  ·  6 min   │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │ [kliknij żeby rozwinąć]                      │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  📞 10.07, 09:18  ·  😊 Nastrój 8/10  ·  5 min     │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │ [kliknij żeby rozwinąć]                      │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌── Leki w tym tygodniu ──┐  ┌── Ostatnie alerty ──────┐   │
│  │                         │  │                          │   │
│  │     ┌───────┐          │  │  ⚠️ 11.07.2026 09:22     │   │
│  │     │  78%  │          │  │  Nastrój spadł do 4/10    │   │
│  │     │       │          │  │  Powód: ból kolana,       │   │
│  │     │ 13/17 │          │  │  bezsenność               │   │
│  │     └───────┘          │  │                           │   │
│  │  dawek przyjętych      │  │  ⚠️ 08.07.2026 20:15     │   │
│  │                         │  │  Pominięta dawka leku    │   │
│  │  💊 Bisoprolol 5 mg    │  │  wieczornego              │   │
│  │     ✅ ✅ ✅ ❌ ✅     │  │                           │   │
│  │  💊 Polocard 75 mg     │  │  🟡 05.07.2026 09:10     │   │
│  │     ✅ ✅ ✅ ✅ ✅     │  │  Senior zgłasza           │   │
│  │                         │  │  samotność                │   │
│  └─────────────────────────┘  └──────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
API Endpointy dla widoku seniora:
// Główny endpoint — wszystkie dane do zakładki "Przegląd"
GET /api/v1/caregiver/senior/:senior_id/overview
  Response: {
    senior: SeniorProfile,
    semaphore: SemaphoreStatus,
    last_call: CallSummary,
    mood_chart: MoodDataPoint[],       // 14 dni
    recent_calls: CallSummary[],       // 3 ostatnie
    medication_widget: {
      adherence_rate_7d: number,
      total_doses_7d: number,
      taken_7d: number,
      medications: MedicationWithStatus[]
    },
    recent_alerts: AlertSummary[],     // 5 ostatnich
    weekly_summary: string             // tekst podsumowania
  }
// Historia rozmów (zakładka "Rozmowy")
GET /api/v1/caregiver/senior/:senior_id/calls?page=1&limit=20&mood=low&date_from=2026-07-01
  Response: {
    calls: CallSummary[],
    pagination: { page, limit, total, pages }
  }
GET /api/v1/caregiver/senior/:senior_id/calls/:call_id
  Response: {
    call: CallDetail,          // pełny obiekt z transkryptem, nagraniem
    transcript: Message[],     // tablica wiadomości z timestampami
    recording_url: string,     // URL do pliku audio
    analysis: CallAnalysis     // sentyment, semafor, słowa kluczowe
  }
// Leki (zakładka "Leki")
GET /api/v1/caregiver/senior/:senior_id/medications
  Response: {
    medications: Medication[],
    adherence_30d: AdherenceDataPoint[],
    missed_doses: MissedDose[]
  }
GET /api/v1/caregiver/senior/:senior_id/medications/adherence?days=30
  Response: {
    adherence_rate: number,
    trend: "improving" | "stable" | "declining",
    daily_data: { date: string, rate: number }[]
  }
// Alerty (zakładka "Alerty")
GET /api/v1/caregiver/senior/:senior_id/alerts?level=red&page=1&limit=20
  Response: {
    alerts: AlertDetail[],
    pagination: Pagination
  }
// Raporty (zakładka "Raporty")
GET /api/v1/caregiver/senior/:senior_id/reports/weekly?date=2026-07-12
  Response: {
    period: { start: string, end: string },
    summary_text: string,
    metrics: {
      avg_mood: number,
      mood_trend: string,
      adherence_rate: number,
      total_calls: number,
      alerts_count: number
    },
    recommendations: string[]
  }
GET /api/v1/caregiver/senior/:senior_id/reports/monthly?month=2026-07
  Response: { ... podobna struktura, więcej danych }
GET /api/v1/caregiver/senior/:senior_id/reports/export/pdf?type=monthly&month=2026-07
  Response: PDF file (application/pdf)
I.F. KOMPONENTY WSPÓŁDZIELONE (Design System Opiekuna)
SemaphoreBadge.tsx
interface SemaphoreBadgeProps {
  level: "green" | "yellow" | "red" | "purple";
  size?: "sm" | "md" | "lg" | "hero";     // hero = duży na stronie seniora
  pulsing?: boolean;                        // pulsowanie dla RED/PURPLE
  label?: string;                           // "OK" / "UWAGA" / "ALARM"
}
// Wizualnie:
// 🟢 sm: kółko 12px, md: 24px, lg: 48px, hero: 96px
// 🔴 RED/PURPLE: pulsująca animacja (opacity 1.0 ↔ 0.6 co 1.5s)
// Label pod spodem dla sm/md, wewnątrz koła dla lg/hero
MoodChart.tsx
interface MoodChartProps {
  data: { date: string; score: number; emoji?: string }[];
  days: 7 | 14 | 30;
  showTrend?: boolean;
  highlightLow?: boolean;    // podświetla spadki na czerwono
  onPointClick?: (date: string) => void;  // kliknięcie = przejście do rozmowy z tego dnia
}
// Recharts LineChart
// Oś Y: 1-10, Oś X: daty
// Punkty <4 na czerwono, punkty z alertami mają obwódkę
// Tooltip: data, wynik, emotka, przycisk "Zobacz rozmowę"
MedicationRing.tsx
interface MedicationRingProps {
  percentage: number;         // 0-100
  taken: number;
  total: number;
  size?: number;              // średnica w px
  strokeWidth?: number;
  color?: string;             // domyślnie: zielony >70%, żółty 40-70%, czerwony <40%
}
// SVG circular progress bar
// Środek: liczba (np. "78%")
// Pod spodem: "13/17 dawek"
AlertTimeline.tsx
interface AlertTimelineProps {
  alerts: AlertEntry[];
  maxItems?: number;
  showSeniorName?: boolean;   // dla widoku zbiorczego
}
// Pionowa timeline:
// 🟣 ─ 12.07.2026 09:22 — ALARM: wykryto słowo "nie mogę oddychać"
// 🔴 ─ 11.07.2026 09:22 — UWAŻAJ: nastrój spadł do 4/10
// 🟡 ─ 08.07.2026 20:15 — MONITORUJ: pominięta dawka wieczorna
// 🟢 ─ 05.07.2026 09:10 — INFO: drobne zgłoszenie samotności
ConversationCard.tsx
interface ConversationCardProps {
  call: CallSummary;
  expanded?: boolean;
  onToggle: () => void;
}
// Zwinięty: data, godzina, długość, nastrój (emotka), pierwsza linia transkryptu
// Rozwinięty: pełny transkrypt z kolorowaniem (Adam = niebieski, Senior = szary)
// Przycisk "Odsłuchaj nagranie" (jeśli dostępne)
// Przycisk "Zgłoś nieprawidłowość"
I.G. USTAWIENIA OPIEKUNA
Ścieżka: /panel/ustawienia
┌──────────────────────────────────────────────────────────────┐
│  Ustawienia konta                                            │
│──────────────────────────────────────────────────────────────│
│                                                              │
│  ┌── Dane osobowe ──────────────────────────────────────┐    │
│  │ Imię i nazwisko:  Anna Nowak                         │    │
│  │ Email:            anna.nowak@email.pl          [✏️]  │    │
│  │ Telefon:          +48 601 002 003              [✏️]  │    │
│  │ Relacja:          Wnuczka                            │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌── Powiadomienia ─────────────────────────────────────┐    │
│  │                                                      │    │
│  │  🔴 Alerty krytyczne (RED/PURPLE):                   │    │
│  │  [✓] SMS na +48••••003    [✓] Email                  │    │
│  │                                                      │    │
│  │  🟡 Alerty ostrzegawcze (YELLOW):                    │    │
│  │  [✓] Email                 [ ] SMS                   │    │
│  │                                                      │    │
│  │  📋 Raport dzienny:                                  │    │
│  │  [✓] Email o 20:00         [ ] SMS                   │    │
│  │                                                      │    │
│  │  📋 Raport tygodniowy:                               │    │
│  │  [✓] Email (poniedziałek 9:00)                       │    │
│  │                                                      │    │
│  │  Godziny ciszy nocnej (bez powiadomień):             │    │
│  │  Od: [22:00 ▾]  Do: [07:00 ▾]                       │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌── Bezpieczeństwo ────────────────────────────────────┐    │
│  │ Zmień hasło:                                  [✏️]   │    │
│  │ Wyloguj się ze wszystkich urządzeń:        [Wyloguj] │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  [  ZAPISZ ZMIANY  ]                                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
API Endpointy:
GET /api/v1/caregiver/profile
  Response: CaregiverProfile
PUT /api/v1/caregiver/profile
  Body: { email?: string, phone?: string }
GET /api/v1/caregiver/notification-preferences
  Response: NotificationPreferences
PUT /api/v1/caregiver/notification-preferences
  Body: NotificationPreferences
PUT /api/v1/caregiver/password
  Body: { current_password: string, new_password: string }
CZĘŚĆ II: LANDING PAGE — PEŁNY COPY I STRUKTURA
II.A. STRUKTURA STRONY (One-Page + podstrony)
STRONA GŁÓWNA (index.html) — one-page scroll:
1.  HERO                    — główna sekcja z CTA
2.  PROBLEM                 — "Dlaczego Adam?"
3.  JAK TO DZIAŁA           — 3 kroki
4.  FUNKCJE                 — 6 funkcji w kartach
5.  DEMO                    — wideo lub symulacja rozmowy
6.  CENNIK                  — 3 pakiety
7.  OPINIE                  — testimonials (placeholder)
8.  FAQ                     — najczęstsze pytania
9.  KONTAKT / CTA FINALNE   — formularz + finalne CTA
10. STOPKA                  — linki, RODO, login
PODSTRONY:
/regulamin                 — Regulamin usługi
/polityka-prywatnosci      — Polityka prywatności
/rodo                      — Informacja RODO
/kontakt                   — Pełny formularz kontaktowy
/login                     — Logowanie opiekuna
/admin-login               — Logowanie admina
II.B. PEŁNY COPY — SEKCJA PO SEKCJI
1. HERO
═══════════════════════════════════════════════════════════
NAGŁÓWEK (H1):
"Adam — asystent głosowy,
który codziennie dzwoni do Twoich bliskich."
PODNAGŁÓWEK (H2):
Adam dzwoni, rozmawia i dba o bezpieczeństwo seniora.
A Ty dostajesz spokój i codzienny raport.
Bez aplikacji. Bez internetu. Wystarczy telefon.
PRZYCISKI CTA:
[ 🟡 Zamów Adama — od 49 zł/mc ]   [ ▶️ Zobacz, jak działa ]
SOCIAL PROOF:
"Zaufało nam już 200+ rodzin w Poznaniu i okolicach"
"Rekomendowany przez geriatrów i opiekunów społecznych"
WIZUALNIE (prawa strona):
Ilustracja: starszy pan siedzi w fotelu, uśmiecha się,
trzyma słuchawkę starego telefonu. Obok mały robot/ikona
Adama (przyjazny, ciepły). W tle ciepłe kolory.
═══════════════════════════════════════════════════════════
2. PROBLEM (Dlaczego Adam?)
═══════════════════════════════════════════════════════════
NAGŁÓWEK:
"Twój bliski zasługuje na codzienną rozmowę.
Nawet gdy nie możesz być obok."
LEWA KOLUMNA — bez Adama:
❌ "Mamo, dlaczego nie odebrałaś? Dzwonię trzeci raz..."
❌ "Czy tata wziął dzisiaj leki? Nie pamiętam..."
❌ "Babcia przewróciła się w nocy, a nikt nie wiedział..."
❌ "Codzienny niepokój: czy wszystko w porządku?"
PRAWA KOLUMNA — z Adamem:
✅ Adam dzwoni codziennie o stałej porze
✅ Pyta o samopoczucie, nastrój, ból, leki
✅ W razie niepokoju natychmiast Cię powiadamia
✅ Dostajesz codzienny raport na email
PODSUMOWANIE (śródtytuł):
"To nie jest chatbot. To nie jest aplikacja.
To prawdziwy telefon od życzliwego głosu,
który dba o bezpieczeństwo Twoich bliskich 24/7."
═══════════════════════════════════════════════════════════
3. JAK TO DZIAŁA (3 kroki)
═══════════════════════════════════════════════════════════
NAGŁÓWEK: "Jak działa Adam?"
KROK 1: 📞 Adam dzwoni
─────────────────────────
"Codziennie o ustalonej porze Adam dzwoni do seniora.
Na telefon stacjonarny lub komórkowy.
Nie trzeba nic instalować, klikać ani konfigurować.
Senior po prostu odbiera telefon — tak jak zawsze."
KROK 2: 💬 Rozmawia
─────────────────────────
"Adam pyta o samopoczucie, nastrój, czy coś boli,
czy leki zostały wzięte, czy senior jadł, spał,
czy wyszedł na spacer. Rozmowa trwa 5-10 minut.
To ciepła, naturalna konwersacja — nie ankieta."
KROK 3: 📊 Powiadamia
─────────────────────────
"Po rozmowie dostajesz krótki raport: nastrój (1-10),
status leków, ewentualne niepokojące sygnały.
Jeśli Adam wykryje coś alarmującego — od razu
dostajesz SMS. W kryzysie Adam sam wezwie pomoc."
═══════════════════════════════════════════════════════════
4. FUNKCJE (6 kart)
═══════════════════════════════════════════════════════════
NAGŁÓWEK: "Co potrafi Adam?"
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 😊           │  │ 💊           │  │ 🚨           │
│ MONITORING   │  │ PRZYPOMNIENIA│  │ ALERTY       │
│ NASTROJU     │  │ O LEKACH     │  │ BEZPIECZEŃSTWA│
│              │  │              │  │              │
│ Adam codzien-│  │ Adam pyta    │  │ Jeśli senior  │
│ nie sprawdza │  │ o każdy lek  │  │ zgłasza ból,  │
│ samopoczucie │  │ z Twojej     │  │ upadek, dusz- │
│ w skali 1-10.│  │ listy.       │  │ ności lub     │
│ Widzisz trend│  │ Dostajesz    │  │ mówi o śmierci│
│ na wykresie. │  │ raport:      │  │ — Adam        │
│ Wykrywamy    │  │ które wzięte,│  │ natychmiast   │
│ spadki nastro-│  │ które pomi-  │  │ Cię powiadomi │
│ ju zanim     │  │ nięte.       │  │ SMS-em.       │
│ będzie źle.  │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ ⌚            │  │ 🧹           │  │ 📋           │
│ INTEGRACJA   │  │ ADAM KONCIERŻ│  │ RAPORTY      │
│ Z OPASKĄ     │  │              │  │ DLA RODZINY  │
│              │  │              │  │              │
│ Opcjonalnie   │  │ Senior może  │  │ Codzienny lub│
│ podłączamy    │  │ przez telefon │  │ tygodniowy   │
│ Mi Band /     │  │ zamówić      │  │ raport na    │
│ Apple Watch.  │  │ sprzątanie,  │  │ email: nastrój│
│ Adam widzi    │  │ transport do  │  │ leki, alerty,│
│ tętno, kroki, │  │ lekarza,     │  │ podsumowanie │
│ wykrywa upadki│  │ zakupy.       │  │ rozmów.      │
│              │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
═══════════════════════════════════════════════════════════
5. PANEL OPIEKUNA (wizualny preview)
═══════════════════════════════════════════════════════════
NAGŁÓWEK: "Wszystko na jednym ekranie"
"Panel Opiekuna to Twoje centrum dowodzenia.
Prosty, czytelny, dostępny z telefonu i komputera."
[SCREEN MOCKUP: zrzut ekranu Dashboardu Opiekuna — kafelki
seniorów z semaforami 🟢🟡🔴, wykres nastroju, lista leków]
LEWA STRONA — podpisy do screena:
• Widzisz stan wszystkich bliskich na jednym ekranie
• Zielony = OK, Żółty = monitoruj, Czerwony = działaj
• Jeden klik i widzisz pełną historię rozmów
• Wykres nastroju pokazuje trendy
• Raport leków: które wzięte, które nie
═══════════════════════════════════════════════════════════
6. CENNIK
═══════════════════════════════════════════════════════════
NAGŁÓWEK: "Wybierz plan dla swojej rodziny"
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│                 │ │   ⭐ NAJCZĘŚCIEJ│ │                 │
│  PODSTAWOWY     │ │   WYBIERANY     │ │  PREMIUM        │
│                 │ │   RODZINNY      │ │                 │
│   49 zł/mc      │ │   79 zł/mc      │ │  119 zł/mc     │
│                 │ │                 │ │                 │
│ ✓ Codzienna     │ │ ✓ Codzienna     │ │ ✓ Dwie rozmowy  │
│   rozmowa       │ │   rozmowa       │ │   dziennie      │
│ ✓ Raport         │ │ ✓ Raport        │ │ ✓ Raport         │
│   dzienny email  │ │   dzienny email │ │   dzienny email  │
│ ✓ SMS przy       │ │ ✓ SMS przy       │ │ ✓ SMS przy       │
│   alarmie        │ │   alarmie       │ │   alarmie        │
│ ✓ 1 senior       │ │ ✓ Do 2 seniorów │ │ ✓ Do 3 seniorów  │
│ ✓ Historia       │ │ ✓ Panel Opiekuna│ │ ✓ Panel Opiekuna │
│   rozmów (7 dni) │ │ ✓ Przypomnienia │ │ ✓ Przypomnienia  │
│                  │ │   o lekach      │ │   o lekach       │
│                  │ │ ✓ Historia      │ │ ✓ Historia       │
│                  │ │   rozmów (30dni)│ │   rozmów (bez l.)│
│                  │ │                 │ │ ✓ Integracja     │
│                  │ │                 │ │   z opaską       │
│                  │ │                 │ │ ✓ Adam Koncierż  │
│                  │ │                 │ │ ✓ Priorytetowe   │
│                  │ │                 │ │   wsparcie       │
│                  │ │                 │ │ ✓ Raport         │
│                  │ │                 │ │   tygodniowy     │
│                  │ │                 │ │                 │
│ [ Wybieram → ]  │ │ [ Wybieram → ]  │ │ [ Wybieram → ]  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
"Wszystkie plany: 14 dni za darmo. Bez umowy. Rezygnujesz
kiedy chcesz. Możesz zmienić plan w dowolnym momencie."
═══════════════════════════════════════════════════════════
7. OPINIE (placeholder)
═══════════════════════════════════════════════════════════
"Co mówią rodziny?"
┌──────────────────────────────────────────────────┐
│ "Mieszkam w Warszawie, mama w Poznaniu. Adam     │
│  dzwoni do niej codziennie o 10. Wczoraj dostałam│
│  SMS, że mama źle się czuje. Zadzwoniłam od razu. │
│  Okazało się, że ma grypę. Bez Adama nie          │
│  wiedziałabym przez tydzień."                     │
│                                                   │
│  — Katarzyna, 43 lata, córka pani Zofii (78 lat) │
└──────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────┐
│ "Tata był sceptyczny. 'Robot będzie do mnie      │
│  dzwonił?'. Po tygodniu mówi do Adama per 'panie │
│  Adamie' i czeka na telefon. Dla nas — spokój,   │
│  że codziennie ktoś sprawdza, czy wszystko OK."   │
│                                                   │
│  — Michał, 37 lat, syn pana Jerzego (82 lata)    │
└──────────────────────────────────────────────────┘
═══════════════════════════════════════════════════════════
8. FAQ
═══════════════════════════════════════════════════════════
NAGŁÓWEK: "Najczęściej zadawane pytania"
❓ Czy senior musi mieć smartfon lub internet?
   Nie! Adam dzwoni na zwykły telefon — stacjonarny
   lub komórkowy (nawet stary model z klawiaturą).
   Senior tylko odbiera. Nie musi nic instalować.
❓ Czy to nagranie, czy prawdziwa rozmowa?
   To prawdziwa rozmowa. Adam reaguje na to, co mówi
   senior. Pyta, słucha, dopytuje. To nie jest sztywne
   nagranie ani ankieta.
❓ Czy rozmowy są nagrywane?
   Tak — za zgodą seniora i rodziny. Nagrania są
   bezpiecznie przechowywane na serwerach w Polsce
   (zgodnie z RODO). Rodzina ma do nich dostęp
   w Panelu Opiekuna.
❓ Co się stanie, jeśli senior nie odbiera?
   Adam oddzwoni 2 razy w odstępach 15-minutowych.
   Jeśli nadal brak kontaktu — dostajesz SMS.
   Możesz ustawić własne reguły eskalacji.
❓ Czy Adam wezwie pomoc, jeśli senior upadnie?
   Tak. Jeśli senior zgłosi upadek, ból w klatce,
   duszności, albo jeśli podłączona jest opaska
   wykrywająca upadek — Adam natychmiast powiadomi
   Ciebie, a w sytuacji zagrożenia życia — 112.
❓ Czy mogę sam(a) ustawić, o co Adam pyta?
   Tak. W Panelu Opiekuna konfigurujesz listę leków,
   ulubione tematy rozmowy, pory dzwonienia.
   Możesz też dodać własne pytania.
❓ Kim jesteście?
   SilverTech to spółdzielnia socjalna z Poznania.
   Łączymy technologię z troską o seniorów.
   Współpracujemy z geriatrami i opiekunami społecznymi.
❓ Czy mogę przetestować za darmo?
   Tak — pierwsze 14 dni jest całkowicie darmowe.
   Bez podawania karty. Bez zobowiązań.
═══════════════════════════════════════════════════════════
9. KONTAKT / CTA FINALNE
═══════════════════════════════════════════════════════════
NAGŁÓWEK: "Zacznij już dziś. 14 dni za darmo."
LEWA STRONA — formularz:
┌──────────────────────────────────┐
│ Imię i nazwisko:                 │
│ ┌──────────────────────────────┐ │
│ └──────────────────────────────┘ │
│                                  │
│ Email lub telefon:               │
│ ┌──────────────────────────────┐ │
│ └──────────────────────────────┘ │
│                                  │
│ Dla kogo Adam?                   │
│ ┌──────────────────────────────┐ │
│ │ Mama / Tata / Babcia / Dziadek│ │
│ └──────────────────────────────┘ │
│                                  │
│ ▢ Wyrażam zgodę na kontakt      │
│                                  │
│ [ 🟡 ZAMÓW DARMOWY OKRES PRÓBNY ]│
└──────────────────────────────────┘
PRAWA STRONA:
"📞 Lub zadzwoń: +48 61 000 00 00"
"📧 Napisz: kontakt@silvertech.poznan.pl"
"📍 Odwiedź nas: ul. Przykładowa 1, Poznań"
═══════════════════════════════════════════════════════════
10. STOPKA
═══════════════════════════════════════════════════════════
SilverTech Spółdzielnia Socjalna
ul. Przykładowa 1, 60-001 Poznań
NIP: XXX-XXX-XX-XX | KRS: XXXXXXXXXX
kontakt@silvertech.poznan.pl | +48 61 000 00 00
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ PRODUKT      │ │ FIRMA        │ │ PRAWNE       │
│              │ │              │ │              │
│ Jak to działa│ │ O nas        │ │ Regulamin    │
│ Funkcje      │ │ Kontakt      │ │ Polityka pryw│
│ Cennik       │ │ Dla mediów   │ │ RODO         │
│ FAQ          │ │ Praca        │ │              │
│ Blog         │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
            [ Logowanie Opiekuna ]  [ Logowanie Admina ]
© 2026 SilverTech. Wszelkie prawa zastrzeżone.
═══════════════════════════════════════════════════════════
CZĘŚĆ III: ARCHITEKTURA RBAC — PEŁNA SPECYFIKACJA
III.A. MODEL RÓL I UPRAWNIEŃ
ROLE W SYSTEMIE:
═══════════════════════════════════════════════════
👑 ADMIN
   └─ Pełny dostęp do wszystkiego
   └─ Zarządza seniorami, opiekunami, systemem
   └─ Widzi wszystkie dane wszystkich seniorów
   └─ Konfiguruje agentów AI, providerów, harmonogramy
   └─ Marketplace: dodaje/usuwa dostawców usług
   └─ Ma dostęp do Admin UI (obecne AVA UI + nowe zakładki)
👨‍👩‍👧 OPIEKUN (Caregiver)
   └─ Widzi TYLKO przypisanych mu seniorów
   └─ Czyta historię rozmów, nastrój, leki, alerty
   └─ Konfiguruje swoje powiadomienia
   └─ Nie może modyfikować danych seniora
   └─ Nie widzi innych opiekunów ani seniorów
   └─ Ma dostęp do Panelu Opiekuna
👨‍👩‍👧 OPIEKUN GŁÓWNY (Primary Caregiver)
   └─ Wszystko co OPIEKUN, PLUS:
   └─ Może dodawać/usuwać innych opiekunów dla "swoich" seniorów
   └─ Zatwierdza prośby o dostęp (request-access)
   └─ Może edytować dane seniora (adres, leki, preferencje)
   └─ Może zmieniać harmonogram połączeń
🔧 KOORDYNATOR (Coordinator) — opcjonalna rola pośrednia
   └─ Jak OPIEKUN GŁÓWNY, ale dla wielu seniorów
   └─ Zatrudniony przez SilverTech do nadzoru
   └─ Otrzymuje eskalacje YELLOW/RED
   └─ Może ręcznie wyzwalać połączenia
III.B. PLIKI DO UTWORZENIA — RBAC
backend/
├── app/
│   ├── models/
│   │   ├── user.py                    # 🆕 Model User (admin + caregiver)
│   │   └── role.py                    # 🆕 Model Role + Permission
│   ├── schemas/
│   │   ├── user.py                    # 🆕 Pydantic schemas dla User
│   │   └── auth.py                    # 🆕 Login/Register/Token schemas
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py                # 🆕 Endpointy autoryzacji
│   │       ├── caregivers.py          # 🆕 Endpointy zarządzania opiekunami
│   │       └── dependencies.py        # 🆕 FastAPI dependencies (get_current_user, require_role)
│   ├── services/
│   │   ├── auth_service.py            # 🆕 Logika autoryzacji (JWT, hashowanie, SMS)
│   │   └── rbac_service.py            # 🆕 Sprawdzanie uprawnień
│   ├── middleware/
│   │   └── rbac_middleware.py          # 🆕 Middleware RBAC dla każdego requestu
│   └── utils/
│       └── security.py                # 🔧 Rozbudowa istniejącego o RBAC
├── alembic/
│   └── versions/
│       └── XXXX_create_users_roles.py  # 🆕 Migracja
└── config/
    └── rbac_permissions.yaml           # 🆕 Definicje uprawnień
III.C. MODELE — backend/app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, Table, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from backend.app.database import Base
# === TABELA ASOCJACYJNA: user_senior ===
user_senior = Table(
    "user_senior",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("senior_id", UUID(as_uuid=True), ForeignKey("seniors.id", ondelete="CASCADE"), primary_key=True),
    Column("relationship", String(50), nullable=True),      # "daughter", "son", "coordinator"
    Column("is_primary", Boolean, default=False),           # opiekun główny
    Column("created_at", DateTime, server_default="now())
)
# === TABELA: users ===
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CAREGIVER = "caregiver"
    COORDINATOR = "coordinator"
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(200), unique=True, nullable=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=True)     # null dla logowania SMS-only
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CAREGIVER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)             # email/SMS zweryfikowany
    last_login_at = Column(DateTime, nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    sms_verification_code = Column(String(6), nullable=True)
    sms_verification_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default="now()")
    updated_at = Column(DateTime, onupdate="now()")
    # Relacje
    seniors = relationship("Senior", secondary=user_senior, back_populates="caregivers")
    notification_prefs = relationship("NotificationPreference", back_populates="user", uselist=False)
class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    # Dla alertów RED/PURPLE
    critical_sms = Column(Boolean, default=True)
    critical_email = Column(Boolean, default=True)
    # Dla alertów YELLOW
    warning_sms = Column(Boolean, default=False)
    warning_email = Column(Boolean, default=True)
    # Raporty
    daily_report_sms = Column(Boolean, default=False)
    daily_report_email = Column(Boolean, default=True)
    weekly_report_email = Column(Boolean, default=True)
    # Godziny ciszy
    quiet_hours_start = Column(String(5), default="22:00")
    quiet_hours_end = Column(String(5), default="07:00")
    user = relationship("User", back_populates="notification_prefs")
III.D. JWT + DEPENDENCY INJECTION — backend/app/api/v1/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from backend.app.models.user import User, UserRole
security = HTTPBearer()
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Wyciąga usera z tokenu JWT. Wpinane jako zależność w każdym endpoincie."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Nieprawidłowy token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token wygasł lub jest nieprawidłowy")
    user = await User.get_or_none(id=user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Użytkownik nie istnieje lub jest nieaktywny")
    return user
def require_role(*roles: UserRole):
    """Factory — zwraca zależność sprawdzającą, czy user ma wymaganą rolę."""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Brak uprawnień. Wymagana rola: {[r.value for r in roles]}"
            )
        return current_user
    return role_checker
async def get_current_caregiver(
    current_user: User = Depends(require_role(UserRole.CAREGIVER, UserRole.COORDINATOR, UserRole.ADMIN))
) -> User:
    return current_user
async def get_current_admin(
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> User:
    return current_user
III.E. SPRAWDZANIE DOSTĘPU DO SENIORA
# backend/app/services/rbac_service.py
class RBACService:
    """Sprawdza, czy dany user ma dostęp do danego seniora."""
    @staticmethod
    async def can_access_senior(user: User, senior_id: str) -> bool:
        """Admin ma dostęp do wszystkich. Opiekun tylko do przypisanych."""
        if user.role == UserRole.ADMIN:
            return True
        # Sprawdź, czy user jest przypisany do seniora
        assignment = await user_senior.select().where(
            user_senior.c.user_id == user.id,
            user_senior.c.senior_id == senior_id
        ).first()
        return assignment is not None
    @staticmethod
    async def can_modify_senior(user: User, senior_id: str) -> bool:
        """Tylko admin i primary caregiver mogą modyfikować seniora."""
        if user.role == UserRole.ADMIN:
            return True
        assignment = await user_senior.select().where(
            user_senior.c.user_id == user.id,
            user_senior.c.senior_id == senior_id,
            user_senior.c.is_primary == True
        ).first()
        return assignment is not None
    @staticmethod
    async def get_accessible_senior_ids(user: User) -> list[str]:
        """Zwraca listę ID seniorów, do których user ma dostęp."""
        if user.role == UserRole.ADMIN:
            seniors = await Senior.all()
            return [str(s.id) for s in seniors]
        assignments = await user_senior.select().where(
            user_senior.c.user_id == user.id
        ).all()
        return [str(a.senior_id) for a in assignments]
III.F. API ENDPOINTY — RBAC
# backend/app/api/v1/auth.py
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
# --- LOGOWANIE ---
@router.post("/caregiver/login")
async def caregiver_login(data: CaregiverLogin):
    """Logowanie opiekuna emailem i hasłem."""
    user = await AuthService.authenticate(data.email, data.password)
    if not user or user.role not in [UserRole.CAREGIVER, UserRole.COORDINATOR]:
        raise HTTPException(401, "Nieprawidłowy email lub hasło")
    token = await AuthService.create_tokens(user)
    return token
@router.post("/admin/login")
async def admin_login(data: AdminLogin):
    """Logowanie admina. Wymaga dodatkowego 2FA (lub pozostaje przy obecnym one-time password)."""
    ...
# --- ZARZĄDZANIE OPIEKUNAMI (tylko ADMIN) ---
@router.post("/caregivers", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def create_caregiver(data: CaregiverCreate):
    ...
@router.get("/caregivers", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def list_caregivers():
    ...
@router.put("/caregivers/{caregiver_id}/seniors", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def assign_seniors(caregiver_id: str, data: AssignSeniorsRequest):
    """Przypisuje seniorów do opiekuna."""
    ...
# --- ZATWIERDZANIE PROŚB O DOSTĘP (PRIMARY CAREGIVER) ---
@router.get("/access-requests", dependencies=[Depends(require_role(UserRole.CAREGIVER, UserRole.ADMIN))])
async def list_access_requests(current_user: User = Depends(get_current_user)):
    """Lista próśb o dostęp dla seniorów przypisanych do zalogowanego opiekuna."""
    ...
@router.post("/access-requests/{request_id}/approve")
async def approve_access_request(request_id: str, current_user: User = Depends(get_current_user)):
    """Zatwierdza prośbę (tylko primary caregiver lub admin)."""
    ...
III.G. MIDDLEWARE RBAC
# backend/app/middleware/rbac_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.app.services.rbac_service import RBACService
class SeniorAccessMiddleware(BaseHTTPMiddleware):
    """
    Dla każdego requestu zawierającego senior_id w ścieżce,
    sprawdza czy zalogowany użytkownik ma dostęp do tego seniora.
    """
    async def dispatch(self, request: Request, call_next):
        # Wyciągnij senior_id z path params (jeśli istnieje)
        path = request.url.path
        # Wzorce ścieżek zawierających senior_id
        import re
        match = re.match(r'.*/senior/([a-f0-9-]{36})', path)
        if match:
            senior_id = match.group(1)
            user = request.state.current_user  # ustawione przez get_current_user
            if not await RBACService.can_access_senior(user, senior_id):
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Brak dostępu do tego seniora"}
                )
        response = await call_next(request)
        return response
III.H. KONFIGURACJA UPRAWNIEŃ — config/rbac_permissions.yaml
roles:
  admin:
    description: "Pełny dostęp do systemu"
    permissions:
      - "seniors:read_all"           # widzi wszystkich seniorów
      - "seniors:write"              # tworzy/edytuje/usuwa seniorów
      - "seniors:delete"
      - "caregivers:read"
      - "caregivers:write"
      - "caregivers:delete"
      - "caregivers:assign"          # przypisuje opiekunów do seniorów
      - "calls:read_all"
      - "calls:export"
      - "agents:configure"           # konfiguracja agentów AI
      - "providers:configure"        # konfiguracja providerów
      - "system:read"                # logi, health, monitoring
      - "system:configure"           # ustawienia systemowe
      - "marketplace:write"          # dodawanie usług
      - "reports:export_all"
  coordinator:
    description: "Koordynator opieki — nadzór nad wieloma seniorami"
    permissions:
      - "seniors:read_assigned"      # widzi TYLKO przypisanych
      - "seniors:write_assigned"     # edytuje przypisanych
      - "caregivers:read_assigned"   # widzi opiekunów przypisanych seniorów
      - "calls:read_assigned"
      - "calls:trigger"              # ręczne wyzwalanie połączeń
      - "reports:export_assigned"
      - "escalations:receive"        # otrzymuje eskalacje
  caregiver:
    description: "Opiekun/rodzina — widzi tylko swoich seniorów"
    permissions:
      - "seniors:read_assigned"
      - "calls:read_assigned"
      - "alerts:read_assigned"
      - "medications:read_assigned"
      - "reports:read_assigned"
      - "notifications:configure_self"
  primary_caregiver:
    description: "Opiekun główny — jak caregiver + zarządzanie dostępami"
    inherits: "caregiver"
    permissions:
      - "seniors:write_assigned"
      - "caregivers:invite"          # zaprasza innych opiekunów
      - "access_requests:approve"    # zatwierdza prośby o dostęp
III.I. INTEGRACJA Z ISTNIEJĄCYM KODEM AVA
Pliki, które trzeba zmodyfikować:
# backend/app/main.py — DODAĆ:
# 1. Nowe routery
from backend.app.api.v1 import auth, caregivers, seniors as senior_api
app.include_router(auth.router)
app.include_router(caregivers.router)
app.include_router(senior_api.router)
# 2. Middleware RBAC
from backend.app.middleware.rbac_middleware import SeniorAccessMiddleware
app.add_middleware(SeniorAccessMiddleware)
# 3. Middleware ustawiające current_user w request.state
@app.middleware("http")
async def set_current_user(request: Request, call_next):
    # Wyciągnij token z Authorization header (opcjonalnie dla public endpoints)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get("sub")
            user = await User.get_or_none(id=user_id)
            request.state.current_user = user
        except JWTError:
            request.state.current_user = None
    else:
        request.state.current_user = None
    return await call_next(request)
Frontend — routing z rolami:
// frontend/src/App.tsx — MODYFIKACJA:
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
function ProtectedRoute({ children, allowedRoles }: { children: JSX.Element, allowedRoles: string[] }) {
    const { user, isLoading } = useAuth();
    if (isLoading) return <Spinner />;
    if (!user) return <Navigate to="/login" />;
    if (!allowedRoles.includes(user.role)) return <Navigate to="/unauthorized" />;
    return children;
}
function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* PUBLICZNE */}
                <Route path="/landing" element={<LandingPage />} />
                <Route path="/login" element={<CaregiverLogin />} />
                <Route path="/admin-login" element={<AdminLogin />} />
                <Route path="/login/request-access" element={<RequestAccess />} />
                <Route path="/login/reset-password" element={<ResetPassword />} />
                {/* PANEL OPIEKUNA */}
                <Route path="/panel/*" element={
                    <ProtectedRoute allowedRoles={['caregiver', 'coordinator']}>
                        <CaregiverLayout />
                    </ProtectedRoute>
                }>
                    <Route index element={<CaregiverDashboard />} />
                    <Route path="senior/:id" element={<SeniorDetail />} />
                    <Route path="senior/:id/rozmowy" element={<Conversations />} />
                    <Route path="senior/:id/leki" element={<Medications />} />
                    <Route path="senior/:id/alerty" element={<Alerts />} />
                    <Route path="senior/:id/raporty" element={<Reports />} />
                    <Route path="ustawienia" element={<Settings />} />
                    <Route path="pomoc" element={<Help />} />
                </Route>
                {/* ADMIN UI (istniejące AVA) */}
                <Route path="/admin/*" element={
                    <ProtectedRoute allowedRoles={['admin']}>
                        <AdminLayout />
                    </ProtectedRoute>
                }>
                    {/* wszystkie istniejące trasy admina */}
                </Route>
                <Route path="/unauthorized" element={<Unauthorized />} />
                <Route path="*" element={<Navigate to="/landing" />} />
            </Routes>
        </BrowserRouter>
    );
}
IV. 📦 PODSUMOWANIE — CO MASZ TERAZ W RĘKU
| Dokument | Zawartość | Strony |
| Panel Opiekuna | 7 ekranów, ~20 komponentów, 15+ endpointów API, stany UI | Pełna specyfikacja |
| Landing Page | 10 sekcji z pełnym copy, struktura HTML, cennik, FAQ | Gotowe do wklejenia |
| RBAC | 4 role, modele, middleware, JWT, uprawnienia YAML, integracja frontend-backend | Pliki do utworzenia + snippet’y |
Natychmiastowe akcje:
Wgraj do GenSpark Design/Prototype: specyfikację Panelu Opiekuna + Landing Page jako wytyczne + obecny kod frontend/src/ AVA
Wgraj do GenSpark AI Developer: pliki RBAC (sekcja III.C–III.I) jako zadanie do zakodowania
Po otrzymaniu kodu: integracja RBAC → Panel Opiekuna → Admin UI redesign → Landing Page