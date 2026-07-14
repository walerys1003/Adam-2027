CO JUŻ JEST, CO TRZEBA STWORZYĆ W WARSTWIE UI/UX ORAZ DOSTĘPACH
1. 📊 CO JUŻ ISTNIEJE W AVA (v7.3.2)
Admin UI — localhost:3003 — JEST ✅
AVA ma rozbudowany panel administratora (operatora systemu). Oto dokładnie, co zawiera:
| Strona / Widok | Opis | Zrzut |
| Setup Wizard | Kreator pierwszego uruchomienia – konfiguracja providerów AI krok po kroku | ✅ |
| Dashboard | Live KPI: aktywne agenty, połączenia, przekierowania, statystyki per-agent, status kontenerów (ai_engine, admin_ui, local_ai_server), wskaźnik połączenia Asterisk | ✅ |
| Live-status (SSE) | Sub-sekundowy push stanu systemu (health, sesje, audio, ARI) | ✅ |
| System Topology | Wizualna mapa komponentów z tri‑state health (green/yellow/red) + 2‑strike debounce | ✅ |
| Agents Tab | CRUD agentów, szablony (receptionist, after‑hours, appointment booker, itp.), prompt editor, voice picker, kopiowanie snippetów dialplan | ✅ |
| Call History | Pełna historia połączeń: transkrypty, metadane (głos, provider, czas), odtwarzanie nagrań (.ulaw, .WAV, .gsm), typ zakończenia (w tym “No input timeout” z watchdoga) | ✅ |
| Call Recordings | Odtwarzacz audio bezpośrednio w przeglądarce (transkodowanie server‑side) | ✅ |
| YAML Editor | Monaco‑based editor z walidacją, kolorowanie nazw tooli wg statusu (enabled/global/not‑enabled) | ✅ |
| Provider Forms | Formularze konfiguracji dla każdego providera (OpenAI, Google, Deepgram, ElevenLabs, Grok, Telnyx, MiniMax, Azure) + ~260 inline tooltipów | ✅ |
| Live Logs | WebSocket‑based streaming logów systemowych | ✅ |
| Asterisk Setup | Live ARI status, module checklist, config audit z komendami naprawczymi | ✅ |
| EnvPage | Podgląd zmiennych środowiskowych, sekcja “Per‑Instance Provider Credentials” | ✅ |
| Calendar Integration | Google Calendar + Microsoft Calendar — konfiguracja, test połączenia | ✅ |
| Settings / Advanced | Voice Activity Detection, Caller Inactivity (watchdog), HTTP tool test guards | ✅ |
| WCAG AA | Skip‑to‑content, programmatic labels, focus‑trapping modal, non‑colour status cues | ✅ |
Przeznaczenie Admin UI: dla operatora/technika SilverTech — zarządza agentami, providerami, sprawdza logi, konfiguruje system. Nie dla opiekuna/rodziny.
Panel opiekuna / rodziny — NIE MA ❌
AVA nie posiada:
Logowania z podziałem na role (admin vs opiekun vs rodzina)
Widoku dedykowanego dla opiekuna/koordynatora seniorów
Widoku dla członka rodziny (wnuka, córki)
Jakiegokolwiek panelu skierowanego do seniora (co słuszne — senior tylko rozmawia przez telefon)
Strony landing page produktu
To wszystko trzeba stworzyć od zera.
Landing page — NIE MA ❌
AVA to projekt open‑source na GitHubie — ma README.md, a nie komercyjny landing page. Trzeba zbudować.
2. 🏗️ HIERARCHIA DOSTĘPU — KTO, DO CZEGO, JAK
Oto pełna mapa dostępów w systemie Agent Adam:
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT ADAM                                │
│                     SilverTech, Poznań                           │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   ┌─────────┐          ┌──────────┐          ┌──────────┐
   │  SENIOR │          │ OPIEKUN  │          │  ADMIN   │
   │ (70-90) │          │(rodzina) │          │(SilverTech)│
   └─────────┘          └──────────┘          └──────────┘
        │                     │                     │
        │                     │                     │
   📞 TYLKO             💻 Panel                💻 Panel
   TELEFON             webowy                 webowy
   (przychodzący/      (przeglądarka)         (przeglądarka)
   wychodzący)
        │                     │                     │
        ▼                     ▼                     ▼
   ┌──────────────────────────────────────────────────────┐
   │             CO MOŻE / CO WIDZI                       │
   ├──────────────────────────────────────────────────────┤
   │                                                      │
   │ SENIOR (telefon):                                    │
   │  • Odbiera telefon od Adama (welfare-check)          │
   │  • Może sam zadzwonić do Adama (gdy potrzebuje)      │
   │  • Rozmawia, zgłasza problemy, zamawia usługi        │
   │  • NIE ma dostępu do żadnego panelu                  │
   │                                                      │
   │ OPIEKUN / RODZINA (panel webowy):                    │
   │  • Widzi TYLKO swoich przypisanych seniorów          │
   │  • Podgląd semafora (🟢🟡🔴🟣)                      │
   │  • Historia rozmów + transkrypty                     │
   │  • Wykres nastroju (30 dni)                          │
   │  • Raport przyjmowania leków                         │
   │  • Alerty i powiadomienia                            │
   │  • Ustawienia powiadomień (SMS/email)                │
   │  • NIE może konfigurować agentów ani systemu         │
   │                                                      │
   │ ADMIN SILVERTECH (panel webowy):                     │
   │  • WSZYSTKO co opiekun, PLUS:                        │
   │  • Zarządzanie seniorami (dodawanie/edycja/usuwanie) │
   │  • Zarządzanie opiekunami (konta, przypisania)       │
   │  • Konfiguracja agentów AI i providerów              │
   │  • Konfiguracja harmonogramów                        │
   │  • Marketplace usług (dodawanie dostawców)           │
   │  • Logi systemowe, monitoring, health                │
   │  • Eksport danych, raporty zbiorcze                  │
   │  • Rozliczenia, statystyki zużycia API               │
   │                                                      │
   └──────────────────────────────────────────────────────┘
Kto do kogo dzwoni?
| Kierunek | Opis | Kto inicjuje |
| Adam → Senior | Welfare‑check o zaplanowanej porze (np. codziennie o 10:00) | Scheduler (automat) |
| Adam → Senior | Przypomnienie o lekach (np. 8:00 i 20:00) | Scheduler (automat) |
| Senior → Adam | Senior sam dzwoni, gdy potrzebuje pomocy, rozmowy, zamówienia usługi | Senior (ręcznie) |
| Adam → 112 | Automatyczne połączenie alarmowe (semafor PURPLE) | Crisis Engine (automat) |
| Adam → Rodzina | SMS/email z alertem lub dziennym podsumowaniem | Notification Service |
3. 🎨 STRATEGIA REDESIGNU PRZEZ GENSPARK DESIGN/PROTOTYPE
Tak, możesz wgrać paczkę kodu do GenSpark Design/Prototype
GenSpark ma funkcję Design/Prototype, gdzie możesz:
Wgrać obecny kod frontendu AVA (React/Next.js w frontend/src/)
Podać wytyczne redesignu
Otrzymać od GenSpark przeprojektowany UI
Co dokładnie trzeba wgrać:
frontend/src/
├── App.tsx                    # Główna aplikacja + routing
├── pages/
│   ├── Dashboard/
│   ├── Agents/
│   ├── CallHistory/
│   ├── Settings/
│   ├── Providers/
│   ├── System/
│   └── ...
├── components/                # Współdzielone komponenty UI
├── styles/                    # CSS / Tailwind / styled-components
└── ...
Co trzeba zbudować od zera (GenSpark Design/Prototype):
A. Panel Opiekuna / Rodziny — NOWY ✨
frontend/src/pages/Caregiver/
├── CaregiverLogin.tsx          # Logowanie opiekuna (email+hasło / kod SMS)
├── CaregiverDashboard.tsx      # Dashboard opiekuna – lista seniorów z semaforami
├── SeniorDetail.tsx            # Szczegóły seniora:
│   ├── SeniorHeader.tsx        #   Imię, semafor, ostatni kontakt, avatar
│   ├── MoodChart.tsx           #   Wykres nastroju (7/14/30 dni)
│   ├── RecentCalls.tsx         #   Ostatnie rozmowy z transkryptami
│   ├── MedicationPanel.tsx     #   Panel leków – % przyjętych, historia
│   ├── AlertTimeline.tsx       #   Timeline alertów i eskalacji
│   └── SettingsPanel.tsx       #   Preferencje powiadomień
└── FamilyAccessRequest.tsx     # Formularz "poproś o dostęp do seniora"
B. Landing Page — NOWY ✨
landing/
├── index.html                  # Strona główna SilverTech
├── css/
├── js/
├── assets/
└── sections/
    ├── hero.html               # Hero section – "Adam – asystent głosowy dla Twoich bliskich"
    ├── how_it_works.html       # Jak działa Adam (3 kroki: dzwoni → rozmawia → powiadamia)
    ├── features.html           # Co potrafi Adam (ikony + opisy)
    ├── pricing.html            # Cennik (subskrypcja miesięczna)
    ├── testimonials.html       # Opinie (placeholder)
    ├── faq.html                # Najczęstsze pytania
    ├── contact.html            # Formularz kontaktowy / zapytanie ofertowe
    └── footer.html             # Stopka z linkami: Login Opiekuna | Login Admina | RODO
C. Admin UI — REDESIGN istniejącego 🎨
Przeprojektowanie obecnego Admin UI AVA na spójną szatę graficzną z nowym brandingiem SilverTech/Adam:
Nowa kolorystyka (branding SilverTech)
Logo “Adam” w sidebarze
Spójny design system (te same komponenty co w Panelu Opiekuna)
Dodanie nowych zakładek: Seniorzy, Marketplace, Raporty
Responsywność (mobile-first dla opiekunów-rodziny)
4. 📝 PROMPT DLA GENSPARK DESIGN/PROTOTYPE
Oto gotowy prompt, który możesz wkleić do GenSpark Design/Prototype:
GENSPARK DESIGN/PROTOTYPE PROMPT:
Zadanie: Stwórz kompletny, spójny redesign UI/UX dla systemu Agent Adam (SilverTech, Poznań) — asystenta głosowego dla seniorów. Oparte na istniejącym kodzie admin panelu AVA AI Voice Agent (React/TypeScript, Monaco editor, SSE live-status).
Do zrobienia:
1. LANDING PAGE (osobna strona statyczna)
Hero: “Adam — asystent głosowy dla Twoich bliskich. Codziennie dzwoni, rozmawia i dba o bezpieczeństwo seniora.”
Sekcja “Jak to działa”: 3 kroki (Adam dzwoni → rozmawia o samopoczuciu i lekach → powiadamia rodzinę)
Sekcja funkcji: monitoring nastroju, przypomnienia o lekach, alerty bezpieczeństwa, integracja z opaską, zamawianie usług
Cennik: 3 pakiety subskrypcyjne (Podstawowy 49 zł/mc, Rodzinny 79 zł/mc, Premium 119 zł/mc)
Sekcja FAQ
Przyciski: “Zamów Adama” (CTA), “Logowanie Opiekuna”, “Logowanie Admina” (dyskretne, w stopce)
Design: ciepły, ludzki, budzący zaufanie — stylistyka “silver tech” (połączenie nowoczesności z troską). Kolorystyka: granat (#1a2744), ciepłe złoto (#c8963e), biel.
2. PANEL OPIEKUNA / RODZINY (web app, nowy) Strony:
Logowanie: email + hasło lub kod SMS, opcja “Nie pamiętam hasła”, opcja “Poproś o dostęp do bliskiego”
Dashboard opiekuna: kafelki z przypisanymi seniorami (awatar inicjały, imię, semafor kolorowy 🟢🟡🔴🟣, data ostatniego kontaktu, przycisk “Szczegóły”)
Widok seniora:
Nagłówek: imię seniora, duży semafor, data ostatniej rozmowy, przycisk “Poproś o kontakt”
Wykres nastroju (liniowy, 30 dni, 1-10)
Timeline ostatnich rozmów (data, długość, nastrój, krótki opis — rozwijane do transkryptu)
Panel leków: wskaźnik kołowy % przyjętych dawek w tym tygodniu
Alerty: lista z datą i typem
Ustawienia: przełączniki SMS/email, godziny powiadomień
Design: prosty, czytelny, duże fonty, przyjazny dla osób 50+ (rodzina seniora często to osoby starsze)
3. REDESIGN ADMIN PANELU (przeprojektowanie istniejącego AVA UI)
Zachowaj WSZYSTKIE istniejące funkcje (Dashboard, Agents, Call History, Providers, System, Settings, Live Logs, YAML Editor, Setup Wizard, Calendar, Topology)
Dodaj nowe zakładki: Seniorzy (CRUD profili), Opiekunowie (zarządzanie kontami opiekunów), Marketplace (katalog usług), Raporty (zbiorcze, eksport)
Nowa szata graficzna: ta sama kolorystyka co landing page (granat + złoto), logo Adam w sidebarze
Sidebar: logo na górze, sekcje zgrupowane (System, Konfiguracja, Seniorzy, Marketplace)
Mobile-responsive (administrator może sprawdzić alert na telefonie)
4. DESIGN SYSTEM (wspólny dla wszystkich 3 paneli)
Kolory: primary=#1a2744, accent=#c8963e, success=#2d6a4f (GREEN), warning=#e6a817 (YELLOW), danger=#c1121f (RED), critical=#6a0572 (PURPLE)
Typografia: Inter (nagłówki), Lato (body) — oba Google Fonts
Komponenty: karty seniora, wskaźnik semafora (pulsujące kółko), timeline, wykres nastroju, wskaźnik kołowy leków
Styl: czysty, nowoczesny, ale ciepły — zaokrąglone rogi (12px), miękkie cienie, dużo białej przestrzeni
Pliki wejściowe: Załączam obecny kod frontendu AVA (frontend/src/). Przeprojektuj go zachowując funkcjonalność, zmieniając warstwę wizualną i dodając nowe strony.
5. 🗂️ PODSUMOWANIE — CO JUŻ JEST vs CO TRZEBA STWORZYĆ
| Element | Istnieje w AVA? | Co z tym zrobić |
| Admin UI (panel operatora) | ✅ Tak — bogaty, funkcjonalny | 🔄 Redesign — nowa szata graficzna + nowe zakładki (Seniorzy, Opiekunowie, Marketplace, Raporty) |
| Panel Opiekuna / Rodziny | ❌ Nie | 🆕 Stworzyć od zera — osobna mini-aplikacja (lub sekcja w ramach tego samego frontendu z routingiem po roli) |
| Landing Page | ❌ Nie (tylko GitHub README) | 🆕 Stworzyć od zera — osobna strona statyczna HTML/CSS/JS |
| Panel dla seniora | ❌ Nie | 🚫 Nie tworzyć — senior korzysta tylko przez telefon |
| RBAC (Role-Based Access Control) | ❌ Nie (tylko jeden admin) | 🆕 Dodać — role: admin, caregiver, family_member |
| System logowania | ✅ Tak — JWT, one-time password | 🔧 Rozbudować — o logowanie opiekuna, rejestrację, reset hasła, “poproś o dostęp” |
| Design system | Częściowo (brak spójnego design token) | 🆕 Stworzyć — wspólny design system dla Admin UI + Panel Opiekuna + Landing Page |
6. 🚀 KOLEJNE KROKI
Wgraj do GenSpark Design/Prototype folder frontend/src/ z repozytorium AVA wraz z promptem powyżej
GenSpark wygeneruje:
Przeprojektowany Admin UI
Nowy Panel Opiekuna
Landing page
Po otrzymaniu redesignu — zintegruj go z backendem (API z F1–F18)
Wdróż RBAC — middleware sprawdzające rolę przy każdym requeście API