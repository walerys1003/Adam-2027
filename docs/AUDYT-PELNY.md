# ADAM-2027 — PEŁNY AUDYT INFORMACYJNY PROJEKTU
### Kompletny przewodnik po projekcie: czym jest, jak działa, z czego się składa i dlaczego

> Dokument napisany tak, aby zrozumiała go osoba **nietechniczna** — krok po kroku,
> od najprostszych pojęć do najbardziej zaawansowanych mechanizmów. Jednocześnie jest
> na tyle szczegółowy i analityczny, że stanowi pełną mapę systemu dla inżyniera,
> inwestora, audytora i koordynatora SilverTech.
>
> **Wersja dokumentu:** 1.0 · **Data:** 2026-07 · **Stan kodu:** backend 295 testów,
> 51 endpointów, 18 tabel, 7 migracji; frontend 29 testów adaptera + pełny interfejs.

---

## SPIS TREŚCI

1. [Czym jest ADAM — w jednym akapicie](#1)
2. [Problem, który rozwiązujemy — dlaczego Adam w ogóle powstał](#2)
3. [Dla kogo jest Adam — trzy grupy odbiorców](#3)
4. [Wielka metafora — jak wyobrazić sobie cały system](#4)
5. [Architektura z lotu ptaka — z jakich „pięter" składa się projekt](#5)
6. [Serce systemu: czterokolorowy semafor bezpieczeństwa](#6)
7. [Jak przebiega jedna rozmowa telefoniczna — tura po turze](#7)
8. [Warstwa głosowa w szczegółach — uszy, mózg i usta Adama](#8)
9. [Katalog funkcji F1–F18 — co każdy moduł robi i za co odpowiada](#9)
10. [Warstwa API — jak części systemu rozmawiają ze sobą](#10)
11. [Baza danych — co i jak jest zapamiętywane](#11)
12. [Frontend — trzy interfejsy dla trzech grup ludzi](#12)
13. [Bezpieczeństwo, prywatność i zgodność z prawem](#13)
14. [Zasady projektowe — filozofia „fail-safe" i dlaczego jest kluczowa](#14)
15. [Technologie — z czego to jest zbudowane i dlaczego akurat to](#15)
16. [Jak to wszystko jest spójne — przepływ danych od telefonu do panelu](#16)
17. [Warianty pracy: tryb deweloperski vs produkcyjny](#17)
18. [Przewagi konkurencyjne — dlaczego to jest wartościowe](#18)
19. [Stan projektu i co pozostało do pełnego uruchomienia](#19)
20. [Słowniczek pojęć](#20)

---

<a name="1"></a>
## 1. Czym jest ADAM — w jednym akapicie

**Adam to cyfrowy, empatyczny asystent głosowy, który dzwoni do seniorów zwykłym
telefonem, rozmawia z nimi po polsku jak troskliwy znajomy, sprawdza jak się czują,
przypomina o lekach, a w razie wykrycia zagrożenia życia natychmiast uruchamia
łańcuch pomocy — powiadamia rodzinę, koordynatora opieki, a w sytuacji krytycznej
dzwoni po pogotowie (112).** Senior **nie musi obsługiwać żadnej aplikacji ani
smartfona** — wystarczy, że odbierze telefon. Cała „inteligencja" i kontrola dzieje
się po stronie systemu: rodzina i opiekunowie widzą stan seniora na czytelnym panelu
webowym/mobilnym, a firma opiekuńcza SilverTech (z Poznania) zarządza wszystkim
z panelu administracyjnego.

Projekt nosi nazwę **ADAM-2027** i jest zbudowany na fundamencie otwartego
oprogramowania (open-source voice agent **AVA** na licencji MIT), rozbudowanego
o kilkanaście własnych modułów senior-care, zgodność z RODO i unijnym AI Act,
oraz trzy warstwy interfejsu użytkownika.

---

<a name="2"></a>
## 2. Problem, który rozwiązujemy — dlaczego Adam w ogóle powstał

Wyobraź sobie samotnego 82-latka mieszkającego sam. Jego dzieci pracują w innym
mieście. Codziennie mają jedno pytanie w głowie: *„Czy mama/tata dzisiaj je w porządku?
Czy wzięła leki? Czy się nie przewróciła?"*. Nie da się dzwonić co godzinę. Nie da
się zatrudnić opiekuna na 24 h dla każdego. A jednocześnie **większość dramatów
u seniorów to nie nagłe katastrofy, lecz powoli narastające sygnały** — gorszy nastrój,
pominięte leki, bezsenność, izolacja — które nikt na czas nie zauważył.

Adam rozwiązuje dokładnie ten problem:

- **Regularny, ciepły kontakt** — dzwoni np. 2 razy dziennie (welfare-check), pyta
  jak minął dzień, słucha.
- **Wczesne wykrywanie** — rozpoznaje w wypowiedziach sygnały ostrzegawcze
  (od „jestem smutny" po „boli mnie w klatce") i klasyfikuje ich powagę.
- **Automatyczna eskalacja** — gdy coś jest nie tak, sam uruchamia powiadomienia
  i — w kryzysie — połączenie z 112, z gotowym pakietem informacji (adres, wiek, leki).
- **Spokój dla rodziny** — bliscy mają w telefonie „semafor": zielony = wszystko OK,
  bez potrzeby ciągłego dzwonienia.

To nie jest zabawka technologiczna. To **codzienna praktyka opieki**, którą interfejs
ma wspierać, a nie zastępować.

---

<a name="3"></a>
## 3. Dla kogo jest Adam — trzy grupy odbiorców

System obsługuje **trzy zupełnie różne role**, każda z własnym widokiem i uprawnieniami:

| Rola | Kto to | Czego używa | Co widzi/robi |
|---|---|---|---|
| **Senior** | osoba 70–90 lat | **tylko telefon** (żadnej aplikacji) | odbiera połączenia od Adama, rozmawia po polsku |
| **Rodzina / opiekun** | dzieci, wnuki, opiekun główny | **Panel Opiekuna** (web + apka mobilna) | semafor stanu 🟢🟡🔴🟣, historia rozmów, nastrój, leki, alerty, zamawianie usług, wiadomości |
| **Koordynator SilverTech** | pracownik firmy opiekuńczej | **Panel Admina** (web) | zarządzanie wszystkimi seniorami, agentami AI, kampaniami dzwonienia, marketplace, raportami, infrastrukturą |

To rozróżnienie jest **wbudowane w system uprawnień (RBAC)** — o czym w rozdziale 13.
Kluczowa zasada: *rodzina widzi tylko swoich seniorów; koordynator/admin widzi wszystkich.*

---

<a name="4"></a>
## 4. Wielka metafora — jak wyobrazić sobie cały system

Żeby zrozumieć, jak części do siebie pasują, wyobraź sobie **profesjonalne centrum
opieki telefonicznej**, tyle że zautomatyzowane:

- **Adam (agent głosowy)** to *empatyczny konsultant*, który dzwoni i rozmawia.
  Ma **uszy** (rozpoznawanie mowy), **mózg** (model językowy + reguły bezpieczeństwa)
  i **usta** (synteza mowy).
- **Semafor** to *tablica świetlna dyspozytora* — dla każdego seniora świeci się jeden
  z czterech kolorów, mówiąc od razu „czy trzeba reagować".
- **Drabina eskalacji** to *procedura alarmowa* — dokładnie rozpisane kroki: kogo
  powiadomić, w jakiej kolejności, z jakim opóźnieniem.
- **Baza danych** to *kartoteka* — profile seniorów, historia rozmów, leki, pomiary.
- **API** to *system łączności wewnętrznej* — sposób, w jaki wszystkie działy
  przekazują sobie informacje.
- **Panel Opiekuna/Admina** to *okno na centrum* — ekrany, przez które ludzie widzą,
  co się dzieje, i wydają polecenia.

Każdy element jest **wymienny i testowalny osobno** — to nie jeden wielki blok, lecz
zestaw współpracujących, dobrze odseparowanych „działów".

---

<a name="5"></a>
## 5. Architektura z lotu ptaka — z jakich „pięter" składa się projekt

Projekt to **monorepo** — jedno repozytorium zawierające wszystkie warstwy w osobnych
katalogach. Oto struktura najwyższego poziomu:

```
ADAM-2027/
├── agent/            ← BACKEND (mózg systemu, Python)
│   └── adam_modules/ ←   20+ modułów domenowych + warstwa API (FastAPI)
├── frontend/         ← INTERFEJSY (React + TypeScript): Landing, Panel Opiekuna, Panel Admina
│   ├── android/      ←   projekt aplikacji mobilnej Android (Capacitor)
│   └── ios/          ←   projekt aplikacji mobilnej iOS (Capacitor)
├── design-system/    ← ADAM DESIGN SYSTEM (kolory, fonty, komponenty, mockupy ekranów)
├── docs/             ← DOKUMENTACJA (roadmapa, audyty, runbooki deploy, źródła)
└── rag/              ← BAZA WIEDZY RAG (semantyczne przeszukiwanie dokumentacji)
```

**Dlaczego monorepo?** Bo wszystkie warstwy jednego produktu żyją razem, wersjonują
się razem i łatwo utrzymać spójność (np. kontrakt API backendu i typy we frontendzie).

### Trzy główne warstwy techniczne

1. **Backend (`agent/adam_modules/`)** — cała logika biznesowa i bezpieczeństwa,
   napisana w Pythonie. To tu żyją funkcje F1–F18, warstwa głosowa i baza danych.
2. **API (`agent/adam_modules/api/`)** — „kelner" między backendem a światem: przyjmuje
   żądania HTTP/JSON i zwraca dane. Zbudowany na **FastAPI**.
3. **Frontend (`frontend/`)** — to, co widzi człowiek: strona reklamowa (Landing),
   Panel Opiekuna i Panel Admina, plus opakowanie w aplikację mobilną (Capacitor).

W kolejnych rozdziałach schodzimy w głąb każdej z nich.

---

<a name="6"></a>
## 6. Serce systemu: czterokolorowy semafor bezpieczeństwa

Jeżeli miałbyś zapamiętać **jedną rzecz** o Adamie, niech to będzie semafor. To
centralny mechanizm, wokół którego kręci się cała reszta.

### Cztery kolory = cztery poziomy pilności

| Kolor | Nazwa | Co oznacza | Przykładowy sygnał | Reakcja systemu |
|---|---|---|---|---|
| 🟢 **Zielony** | `green` | Wszystko w porządku, rutyna | „Czuję się dobrze, zjadłam obiad" | tylko zapis, brak alarmu |
| 🟡 **Żółty** | `yellow` | Obserwacja, drobne sygnały | „Jestem smutny", „nie wziąłem leków", „źle śpię" | notatka + monitoring, ew. informacja do rodziny |
| 🔴 **Czerwony** | `red` | Pilne — potrzebna interwencja | „bardzo mnie boli", „przewróciłem się", nieprawidłowe parametry życiowe | uruchomienie drabiny eskalacji |
| 🟣 **Fioletowy** | `purple` | Kryzys — zagrożenie życia | „ból w klatce", „nie mogę oddychać", objawy udaru, „nie chcę żyć" | natychmiastowe 112 + wszyscy powiadomieni |

Te poziomy w kodzie to `SemaphoreLevel` (green / yellow / red / purple), a konkretne
sygnały to `Trigger` (np. `chest_pain`, `fall_reported`, `mood_low`).

### Jak semafor „myśli" — trzy żelazne reguły

Logika żyje w pliku `semaphore/engine.py` (klasa `SemaphoreEngine`). Trzy zasady,
które musisz zrozumieć:

**1. Poziom wynikowy = MAKSIMUM z sygnałów.**
Jeśli w jednej rozmowie padnie i „jestem smutny" (żółty), i „boli mnie w klatce"
(fioletowy) — system wybiera **wyższy** poziom (fioletowy). Bezpieczeństwo zawsze
wygrywa. W kodzie robi to funkcja `max_level()`.

**2. Semafor nie „gaśnie" sam.**
To najważniejsza zasada bezpieczeństwa. Gdy stan podniesie się do czerwonego lub
fioletowego, **nie może samoczynnie wrócić do zielonego**. Musi być *jawnie
rozwiązany* przez człowieka (funkcja `resolve()`). Dzięki temu żaden alarm nie
„zniknie po cichu". Domyślnie poziom może tylko rosnąć lub trwać (`allow_downgrade=False`).

**3. Każda zmiana zostawia ślad.**
Każde podniesienie/obniżenie poziomu zapisuje `SemaphoreEvent` w bazie — z poprzednim
poziomem, nowym poziomem, wyzwalaczem, pewnością i dowodami. To pełny, audytowalny
dziennik (wymóg AI Act).

### Skąd biorą się sygnały — detektor kryzysu

Sygnały wykrywa `CrisisDetector` (`semaphore/detector.py`). Działa **regułowo** —
ma słowniki polskich fraz dobranych pod mowę seniorów:

```python
Trigger.chest_pain: ["ból w klatce", "ściska mnie w piersi", "ból serca", ...]
Trigger.breathing_difficulty: ["nie mogę oddychać", "duszę się", "brak powietrza", ...]
Trigger.fall_reported: ["przewróciłem się", "upadłem", "leżę na podłodze", ...]
Trigger.mood_low: ["jestem smutny", "przygnębiony", "nic mi się nie chce", ...]
```

**Dlaczego reguły, a nie „sztuczna inteligencja"?** Bo twarde sygnały kryzysowe
(ból w klatce, udar, myśli samobójcze) **muszą** być wykrywane w 100% niezawodnie
i w sposób *wytłumaczalny* („wykryto, bo padła fraza X"). Model AI mógłby się pomylić
albo „zawiesić". Reguła jest deterministyczna i audytowalna — a to wymóg prawny.
Detektor rozpoznaje też **nieprawidłowe parametry życiowe** z opasek (np. tętno <40
lub >130, saturacja <90%, ciśnienie skurczowe <90 lub >180 → czerwony).

> **Uwaga:** w produkcji reguły są *wzmacniane* głosem modelu AI (konsensus — rozdz. 8),
> ale AI może tylko **podnieść** czujność, nigdy jej nie **obniżyć**.

---

<a name="7"></a>
## 7. Jak przebiega jedna rozmowa telefoniczna — tura po turze

Prześledźmy realny scenariusz. Silnikiem rozmowy jest `DialogEngine`
(`voice/dialog.py`) — „maszyna stanów", która przechodzi przez ściśle określone etapy:

```
INIT → DISCLOSED → ACTIVE → (ESCALATING) → CLOSED
```

**Etap 0 — INIT (start).** System buduje profil rozmowy: kim jest senior, jaki ma
wiek, jaki profil mowy (o tym w rozdz. 8), i tworzy „system prompt" — instrukcję
dla mózgu Adama.

**Etap 1 — DISCLOSED (obowiązkowe ujawnienie AI).** Adam **musi** zacząć od zdania:

> *„Dzień dobry, tu Adam — jestem cyfrowym asystentem głosowym, który dzwoni
> w imieniu zespołu opieki SilverTech. Nie jestem człowiekiem. Dzwonię, żeby zapytać,
> jak się Pan/Pani dziś czuje."*

To nie jest grzecznościowe — to **wymóg prawny** (unijny AI Act, art. 50: człowiek
ma prawo wiedzieć, że rozmawia z AI). System zapisuje, że ujawnienie padło
(`disclosure_said = True`).

**Etap 2 — ACTIVE (właściwa rozmowa, tura po turze).** Dla **każdej** wypowiedzi
seniora dzieje się to samo:
1. Tekst trafia do detektora/konsensusu → wychodzi poziom semafora + wyzwalacz.
2. Jeśli poziom to **zielony/żółty** → Adam odpowiada normalnie (empatyczna reakcja
   z modelu językowego) i rozmowa toczy się dalej.
3. Poziom jest „podbijany" w wyniku rozmowy (`_bump_level`) — pamiętamy najwyższy
   zaobserwowany poziom.

**Etap 3 — ESCALATING (przerwanie na kryzys).** Jeśli wypowiedź osiągnie **czerwony
lub fioletowy**, Adam **natychmiast przerywa zwykłe Q&A** i mówi:

> *„Słyszę, że dzieje się coś poważnego. Proszę zachować spokój — już przekazuję
> pilną informację do zespołu opieki i, jeśli trzeba, służb ratunkowych. Zostaję
> z Panem/Panią na linii."*

Uruchamia się drabina eskalacji (rozdz. 6, tabela). Adam **nie diagnozuje** i **nie
udaje lekarza** — jego zadaniem jest rozpoznać i przekazać dalej.

**Etap 4 — CLOSED (zakończenie).** Adam żegna się ciepło. Cała rozmowa jest
podsumowana w obiekcie `CallOutcome`: pełna transkrypcja, najwyższy poziom semafora,
najgroźniejszy wyzwalacz, czy nastąpiła eskalacja, czy potrzebna jest weryfikacja
człowieka (`needs_review`).

> **Genialny szczegół projektowy:** cała ta logika jest **czysta** — nie wymaga
> prawdziwego telefonu ani nagrań. Dzięki temu można ją w 100% przetestować „na sucho"
> (endpoint `POST /api/voice/simulate-call` przechodzi cały tor tekstowo).

---

<a name="8"></a>
## 8. Warstwa głosowa w szczegółach — uszy, mózg i usta Adama

Warstwa głosowa (`agent/adam_modules/voice/`) to najbardziej zaawansowana część
systemu. Rozłóżmy ją na „narządy".

### Trzy „porty" — uszy, mózg, usta

Adam potrzebuje trzech zdolności, a każda jest zdefiniowana jako **port** (kontrakt,
umowa o tym „co ma robić", bez przesądzania „jak"):

| Port | „Narząd" | Zadanie | Skrót |
|---|---|---|---|
| **ASR** | uszy | zamiana mowy na tekst (rozpoznawanie mowy) | Automatic Speech Recognition |
| **LLM** | mózg | zrozumienie i wygenerowanie odpowiedzi + klasyfikacja | Large Language Model |
| **TTS** | usta | zamiana tekstu na mowę (synteza głosu) | Text-To-Speech |

**Dlaczego „porty"?** To kluczowa decyzja architektoniczna. Port to jak gniazdko
elektryczne: możesz wpiąć różne urządzenia, byle miały pasującą wtyczkę. Dzięki temu:

- **W trybie deweloperskim/testowym** (`voice/ports.py`) wpina się „atrapy" bez sieci:
  - `EchoASR` — udaje rozpoznawanie mowy,
  - `RuleLLM` — prosty „mózg" na regułach,
  - `TextTTS` — udaje syntezę.
  Dzięki temu testy działają **bez internetu, bez kluczy, bez kosztów**.

- **W trybie produkcyjnym** (`voice/prod_ports.py`) wpina się realne usługi:
  - `WhisperASR` — rozpoznawanie mowy przez OpenAI Whisper,
  - `OpenAITTS` **lub** `ElevenLabsTTS` — synteza głosu (ElevenLabs daje naturalny
    polski głos),
  - `OpenAILLM` — prawdziwy model językowy jako mózg.

Kod aplikacji **nie wie i nie musi wiedzieć**, która wersja jest wpięta — widzi tylko
port. To pozwala rozwijać i testować logikę niezależnie od kosztownych usług AI.

### System Prompt — „instrukcja obsługi" dla mózgu

Zanim model językowy cokolwiek powie, dostaje **system prompt** — precyzyjną instrukcję
(`semaphore/prompt.py`). Zawiera m.in.:

- **Tożsamość i transparentność:** „zawsze mówisz, że jesteś AI; nigdy nie udajesz
  lekarza, pielęgniarki ani członka rodziny".
- **Zasady rozmowy:** „mów spokojnie, ciepło, prostym językiem; krótkie zdania; jedno
  pytanie naraz; nie poganiaj; szanuj godność seniora".
- **Bezpieczeństwo:** „twoim zadaniem jest ROZPOZNAĆ sygnały, nie DIAGNOZOWAĆ; nie
  podajesz porad medycznych; nie zmieniasz dawek leków".
- **Czego nie robić:** „nie wymyślaj faktów o zdrowiu (anty-halucynacja); nie obiecuj
  rzeczy niemożliwych; nie zbieraj danych ponad potrzebę (RODO)".

Prompt jest **dynamiczny** — wstrzykuje imię, wiek i profil mowy konkretnego seniora.

### Profil mowy senioralnej (F14) — dostrojenie do słuchu i tempa

Seniorzy różnie słyszą i różnie przetwarzają mowę. Moduł `speech/profile.py` na
podstawie poziomu słuchu (`HearingLevel`: normal / mild_loss / moderate_loss /
severe_loss) i tempa poznawczego (`CognitivePace`) **deterministycznie** wylicza
parametry głosu: tempo (WPM — słowa na minutę, baza 140) i głośność (wzmocnienie w dB).
Te parametry trafiają do TTS. Efekt: dla osoby z niedosłuchem Adam mówi wolniej
i głośniej — automatycznie, bez „zgadywania" przez AI.

### Konsensus kryzysowy (F16) — dwa niezależne głosy

Najbardziej wyrafinowany mechanizm bezpieczeństwa (`voice/consensus.py`). Zamiast
polegać na jednym źródle, dla każdej wypowiedzi system zbiera **dwa głosy**:

1. **Detektor regułowy** (deterministyczny, audytowalny — rozdz. 6).
2. **Klasyfikator LLM** (model AI ocenia tę samą wypowiedź).

Oba głosy trafiają do `ConsensusEngine`, który stosuje **regułę fail-safe**:
- przy rozbieżności wybiera **wyższy** poziom,
- oznacza `needs_review` (człowiek powinien zerknąć),
- **LLM może tylko podnieść czujność, nigdy jej obniżyć** — twardy sygnał detektora
  jest nienaruszalny,
- jeśli LLM zawiedzie (błąd, brak sieci) → zostaje sam detektor, system dalej działa.

To najlepsze z obu światów: niezawodność reguł + wyczucie niuansów modelu AI.

### Telefonia — jak Adam faktycznie dzwoni (Asterisk / ARI)

Prawdziwe połączenia obsługuje **Asterisk** (otwarta centrala telefoniczna) przez
interfejs **ARI** (Asterisk REST Interface). W kodzie:
- `voice/asterisk.py` (`AsteriskAriChannel`) — adapter do centrali telefonicznej,
- `voice/ari.py` — sesja połączenia (`CallSession`) i kanał (`AriChannel` / `FakeChannel`),
- `voice/stasis.py` (`StasisApp`) — warstwa zdarzeń telefonicznych: reaguje na to, że
  ktoś odebrał, rozłączył się itd., i inicjuje połączenia wychodzące (`originate_call`).

Wszystkie te elementy są **fail-safe**: bez skonfigurowanej centrali (`ASTERISK_ARI_URL`)
działają jako „no-op" — nie wywalają systemu, po prostu grzecznie zwracają „nie wykonano".

---

<a name="9"></a>
## 9. Katalog funkcji F1–F18 — co każdy moduł robi i za co odpowiada

Cała logika biznesowa jest podzielona na **18 ponumerowanych funkcji (F1–F18)**, każda
w swoim module. To „działy" firmy opiekuńczej przełożone na kod.

| # | Funkcja | Moduł | Co robi (po ludzku) |
|---|---|---|---|
| **F1** | Profile seniorów + szyfrowanie PII | `seniors/` | Kartoteka podopiecznych. Dane wrażliwe (PESEL, telefon) są **szyfrowane** i nigdy nie wracają jawnie w odpowiedziach. |
| **F2** | Scheduler welfare-check | `scheduler/` | „Grafik dzwonienia". Planuje kampanie (np. 2×/dzień), ponawia próby przy braku odpowiedzi; po wyczerpaniu prób → sygnał do eskalacji. |
| **F3** | Semafor bezpieczeństwa | `semaphore/` | Serce systemu (rozdz. 6): klasyfikacja poziomu 🟢🟡🔴🟣 + drabina eskalacji. |
| **F4** | Guardrails | `semaphore/guardrails.py` | „Bezpieczniki" — walidują klasyfikację, blokują porady medyczne i obietnice; fioletowy wymaga twardego sygnału. |
| **F5** | System Prompt Adama | `semaphore/prompt.py` | Instrukcja osobowości i zasad dla mózgu (rozdz. 8). |
| **F6** | Medication tracker | `medication/` | Leki, harmonogramy dawek, raport przyjmowania (adherence) — np. „82% dawek w 30 dni". |
| **F7** | Pamięć semantyczna | `memory/` | Adam „pamięta" wcześniejsze rozmowy — fragmenty są indeksowane i wyszukiwane po znaczeniu. |
| **F8** | Crisis detection | `semaphore/`, `voice/` | Detektor sygnałów z mowy i pomiarów (rozdz. 6). |
| **F9** | Dashboard rodzinny + powiadomienia | `family/` | Opiekunowie, ich role, kanały (SMS/e-mail/push), strumień powiadomień, tryby dostarczania (digest / natychmiast / z pominięciem „nie przeszkadzać"). |
| **F10** | Wearables | `wearables/` | Opaski/zegarki (Xiaomi, Apple, Garmin, Fitbit): urządzenia, odczyty parametrów życiowych, progi alarmowe. |
| **F11** | Marketplace usług | `marketplace/` | Katalog usług (zakupy, sprzątanie, wizyty), zamawianie z oknem anulowania (30 min). |
| **F12** | RODO | `rodo/` | Prawa osoby: eksport danych, „prawo do bycia zapomnianym", rejestr czynności przetwarzania. |
| **F13** | AI Act compliance | `compliance/` | Rejestr systemu AI, logi ujawnień natury AI (art. 50), rejestr wymagany przez AI Act. |
| **F14** | Mowa senioralna | `speech/` | Profil mowy → parametry TTS (rozdz. 8). |
| **F15** | QA rozmów | `qa/` | Ocena jakości rozmowy (wynik 0–100 + flagi problemów). |
| **F16** | Konsensus decyzyjny | `consensus/` | Silnik wielogłosowy fail-safe (rozdz. 8). |
| **F17** | Emergency payload (112) | `emergency/` | Buduje pakiet dla służb: adres, wiek, leki, kontekst — gotowy do przekazania do 112. |
| **F18** | Testy end-to-end | `tests/` | Kompletne scenariusze sprawdzające cały przepływ (295 testów łącznie). |

Do tego dochodzą moduły „wspólne":
- **`auth/`** — logowanie, hasła (bezpiecznie haszowane), tokeny JWT, role i uprawnienia.
- **`common/`** — połączenie z bazą (`db.py`) i kryptografia PII (`crypto.py`).
- **`api/`** — warstwa REST (rozdz. 10).

---

<a name="10"></a>
## 10. Warstwa API — jak części systemu rozmawiają ze sobą

**API** (Application Programming Interface) to „kelner" restauracji: gość (frontend,
aplikacja mobilna, panel) składa zamówienie w ustalonym języku, a kuchnia (backend)
je realizuje i odsyła gotowe danie. U nas ten „język" to **HTTP + JSON**, a kelnerem
jest framework **FastAPI**.

### Fabryka aplikacji — jak API się składa

Wszystko buduje jedna funkcja `create_app()` w `api/app.py`. Krok po kroku:
1. Tworzy instancję FastAPI z tytułem i opisem.
2. Nakłada **warstwy pośredniczące (middleware)** — o nich za chwilę.
3. Inicjalizuje bazę danych.
4. Podpina **12 routerów** (grup endpointów) i zwraca gotową aplikację.

### Middleware — cztery „bramki", przez które przechodzi każde żądanie

Wyobraź sobie, że każde żądanie od użytkownika musi przejść przez cztery bramki
(od zewnątrz do wewnątrz):

```
[Nagłówki bezpieczeństwa] → [CORS] → [Kontekst żądania] → [Rate-limit] → aplikacja
```

1. **SecurityHeaders** — dokleja nagłówki bezpieczeństwa do KAŻDEJ odpowiedzi
   (blokada osadzania w ramkach, zakaz „zgadywania" typu treści, polityka CSP itd.).
2. **CORS** — pilnuje, że tylko zaufane adresy (panel opiekuna/admina) mogą wołać API.
3. **RequestContext** — nadaje każdemu żądaniu unikalny identyfikator (`X-Request-ID`)
   i mierzy czas odpowiedzi (`X-Response-Time-ms`) — bezcenne przy diagnozowaniu.
4. **Rate-limit** — ogranicza liczbę żądań na klienta (ochrona przed przeciążeniem/atakiem);
   po przekroczeniu zwraca `429` z informacją, kiedy spróbować ponownie. **Ważne:**
   endpointy zdrowia (`/health`, `/health/live`, `/health/ready`), `/metrics` i `/`
   są **zwolnione** z limitu — bo pytają je maszyny (load balancer) bardzo często.

### 51 endpointów w 12 routerach

Endpoint to pojedynczy „adres" API, np. `GET /api/seniors` (pobierz listę seniorów).
Pełna mapa (w `docs/API.md`) obejmuje **51 endpointów**. Grupy:

| Router | Prefiks | Przykładowe endpointy |
|---|---|---|
| **System** | — | `/health`, `/health/live`, `/health/ready`, `/metrics`, `/` |
| **Auth** | `/api/auth` | `login` (e-mail+hasło → tokeny JWT), `refresh`, `me` (profil) |
| **Seniorzy (F1)** | `/api/seniors` | lista, tworzenie, szczegóły, aktualizacja, soft-delete |
| **Bezpieczeństwo (F3/F8)** | `/api/safety` | `analyze` (analiza tekstu+pomiarów), historia, resolve |
| **Leki (F6)** | `/api/seniors/{id}/medications` | lista, dodanie, raport adherence |
| **Wearables (F10)** | `/api/seniors/{id}/wearables` | urządzenia, odczyty, przekroczenia progów |
| **Rodzina (F9)** | `/api/seniors/{id}/family` | członkowie, dispatch powiadomień, feed, `events` (na żywo, SSE) |
| **Marketplace (F11)** | `/api/marketplace` | katalog usług, zamówienia, anulowanie |
| **RODO (F12)** | `/api/seniors/{id}/rodo` | eksport, soft-delete, erase, audyt |
| **Compliance (F13–F17)** | `/api/compliance` | rejestr AI, disclosures, QA, konsensus, payload 112, profil mowy |
| **Voice (F5/F12/F19)** | `/api/voice` | `simulate-call` (symulacja rozmowy), `call-start` (webhook telefonii) |
| **Konto/Wiadomości (F22)** | `/api/account` | wątki wiadomości, wysyłanie, faktury, sesje |

### Jak wygląda błąd — spójne, bezpieczne odpowiedzi

System tłumaczy błędy na czytelne kody HTTP:
- **401** — problem z uwierzytelnieniem (złe hasło/token). Komunikat jest celowo
  ogólny, żeby nie zdradzać, czy dany e-mail istnieje (ochrona przed enumeracją).
- **422** — błąd walidacji danych (np. niepoprawny PESEL, próba anulowania po oknie).
- **429** — za dużo żądań (rate-limit).
- **503** — system żyje, ale zależność (baza) jest niedostępna (z `/health/ready`).

### Endpointy zdrowia — jak maszyny sprawdzają, czy Adam działa

To standard w profesjonalnym hostingu (Kubernetes, load balancery):
- **`/health` i `/health/live`** — „czy proces żyje?" (szybka odpowiedź, bez sprawdzania
  zależności).
- **`/health/ready`** — „czy jestem gotów obsłużyć ruch?" — realnie odpytuje bazę
  (`SELECT 1`). Jeśli baza padnie → zwraca **503**, a load balancer przestaje kierować
  ruch do tej instancji. To też jest **fail-safe** — wyjątek jest łapany, proces nigdy
  się nie wywala.

---

<a name="11"></a>
## 11. Baza danych — co i jak jest zapamiętywane

Wszystkie trwałe dane żyją w bazie relacyjnej (tabele + relacje). W trybie
deweloperskim to **SQLite** (plik lub pamięć), w produkcji **PostgreSQL** (we
Frankfurt DC). Dostęp odbywa się przez **SQLAlchemy** (biblioteka mapująca tabele
na obiekty Pythona), a strukturę tworzą **migracje Alembic** (0001–0007) — czyli
wersjonowane „przepisy" na budowę i zmianę bazy.

### 18 tabel — kartoteka całego systemu

| Tabela | Moduł | Co przechowuje |
|---|---|---|
| `seniors` | F1 | profile podopiecznych (dane wrażliwe szyfrowane) |
| `campaigns` | F2 | kampanie dzwonienia (grafik welfare-check) |
| `call_attempts` | F2 | pojedyncze próby połączeń + status |
| `semaphore_events` | F3 | pełna historia zmian semafora (audyt) |
| `medications` | F6 | leki seniora |
| `medication_schedules` | F6 | harmonogramy dawek |
| `dose_logs` | F6 | dziennik przyjęcia dawek |
| `memory_chunks` | F7 | fragmenty rozmów do pamięci semantycznej |
| `family_members` | F9 | opiekunowie + role + kanały kontaktu |
| `notifications` | F9 | powiadomienia (poziom, tryb, treść, status) |
| `wearable_devices` | F10 | zarejestrowane urządzenia |
| `vital_readings` | F10 | odczyty parametrów życiowych |
| `vital_thresholds` | F10 | progi alarmowe dla parametrów |
| `partners` | F11 | dostawcy usług w marketplace |
| `marketplace_services` | F11 | katalog usług |
| `marketplace_orders` | F11 | zamówienia |
| `data_processing_logs` | F12 | rejestr czynności przetwarzania (RODO art. 30) |
| `disclosure_logs` | F13 | logi ujawnień natury AI (AI Act art. 50) |

### Kluczowa zasada: dane wrażliwe są szyfrowane

Numer PESEL czy telefon **nigdy** nie są przechowywane „gołym tekstem". Moduł
`common/crypto.py` szyfruje je (AES/Fernet) oraz tworzy tzw. *blind index* — dzięki
temu można wyszukiwać po numerze bez odszyfrowywania go w bazie. Odpowiedzi API
maskują PII (funkcja `SeniorOut.from_model`), więc nawet zalogowany opiekun nie
zobaczy pełnego PESEL-u w zwykłym widoku.

---

<a name="12"></a>
## 12. Frontend — trzy interfejsy dla trzech grup ludzi

Frontend (`frontend/`) to wszystko, co widzi człowiek. Zbudowany w **React +
TypeScript** (nowoczesny, typowany JavaScript), stylowany przez **Tailwind CSS**,
z wykresami z **Recharts** i ikonami **Lucide**. Aplikację mobilną tworzy **Capacitor**
(opakowuje stronę w natywną apkę iOS/Android).

### Trzy „produkty" w jednym

**1. Landing Page** (`pages/LandingPage.tsx` + `components/landing/`) — strona
reklamowo-informacyjna: sekcja bohatera (Hero), opis problemu, jak to działa, funkcje,
cennik, opinie, partnerzy, wezwanie do działania. To „wizytówka" projektu.

**2. Panel Opiekuna** (`pages/panel/` + `components/panel/`) — dla rodziny. Ekrany:
- **Dashboard** — przegląd wszystkich „moich" seniorów z semaforem.
- **Lista seniorów** i **szczegóły seniora** (zakładki: nastrój, leki, wearables, historia).
- **Zamówienia** (marketplace), **Wiadomości**, **Raporty**, **Konto**, **Ustawienia**, **Pomoc**.
- **Baner alertu krytycznego** — gdy senior jest 🔴/🟣, panel krzyczy wizualnie.

**3. Panel Admina** (`pages/admin/` — ok. 25 ekranów) — dla koordynatora SilverTech:
zarządzanie seniorami, flotą agentów AI, modelami, dostawcami, kampaniami dzwonienia,
Asteriskiem, Dockerem, logami, terminalem, marketplace, alertami i wieloma innymi
aspektami infrastruktury.

### Sprytny przełącznik: mock kontra żywe API

Najciekawsza decyzja projektowa frontendu żyje w `lib/api/client.ts`:

```
USE_MOCK = brak adresu backendu (VITE_API_URL)
```

- **Bez adresu backendu** → frontend używa **danych-atrap** (`mockApi.ts`) trzymanych
  w pamięci. Można rozwijać i pokazywać interfejs **bez uruchamiania backendu**.
- **Z adresem backendu** → frontend używa **prawdziwego API** przez adapter
  `realApi.ts`, który tłumaczy odpowiedzi FastAPI na typy zrozumiałe dla interfejsu.

To pozwala projektantom i testerom pracować niezależnie od backendu, a jednocześnie
jednym ustawieniem przełączyć całość na „żywo". Obecnie na żywym API działają już:
logowanie (login/refresh/me), seniorzy, nastrój, zamówienia oraz wiadomości/konto
(wątki, faktury, sesje).

### Aplikacja mobilna (Capacitor)

Ten sam kod webowy jest „owinięty" w natywną aplikację. Dołożone są funkcje natywne:
- **BiometricGate** — logowanie odciskiem palca / Face ID,
- **NotificationService** — powiadomienia push i lokalne,
- **InstallPrompt / PWA** — instalacja jako aplikacja.

Uruchomienie na iOS/Android wymaga jedynie kont deweloperskich Apple/Google (kod jest
gotowy).

---

<a name="13"></a>
## 13. Bezpieczeństwo, prywatność i zgodność z prawem

Adam działa z **danymi medycznymi osób starszych** — to jedna z najwrażliwszych
kategorii danych. Dlatego bezpieczeństwo i zgodność z prawem nie są dodatkiem,
lecz fundamentem.

### Kto może co — uwierzytelnianie i role (RBAC)

- **Logowanie** przez e-mail + hasło → system wydaje **dwa tokeny JWT**: krótki
  „access" (15 min) i długi „refresh" (14 dni). Hasła są haszowane algorytmem
  PBKDF2-HMAC-SHA256 (200 tys. rund, sól per-hasło) — nie da się ich odczytać z bazy.
- **Trzy role (hierarchia):** `family` < `coordinator` < `admin`. Endpoint wymagający
  wyższej roli zwróci `403`, jeśli użytkownik ma za niską.
- **Widoczność seniorów:** rodzina (`family`) widzi **tylko przypisanych** seniorów
  (lista `senior_ids` zaszyta w tokenie); koordynator/admin — wszystkich.
- Dodatkowo można włączyć **klucz API** (`X-API-Key`) jako drugą warstwę ochrony.

### Prywatność (RODO)

- **Szyfrowanie PII** (AES) + maskowanie w odpowiedziach (rozdz. 11).
- **Minimalizacja danych** — Adam ma w promptach zakaz zbierania informacji ponad cel.
- **Prawa osoby** (moduł `rodo/`): eksport danych (art. 15/20), soft-delete,
  **prawo do bycia zapomnianym** (art. 17 — trwałe usunięcie), rejestr czynności
  przetwarzania (art. 30).
- **Retencja nagrań** — założona na 30 dni.

### Zgodność z AI Act (unijne prawo o AI)

- **Obowiązkowe ujawnienie natury AI** przy każdej rozmowie (art. 50) — wbudowane
  w `DialogEngine` i logowane (`disclosure_logs`).
- **Wytłumaczalność** — twarde decyzje kryzysowe są regułowe i audytowalne
  („dlaczego alarm?" → „bo padła fraza X").
- **Rejestr systemu AI** (`compliance/`) — wymagana dokumentacja systemu wysokiego
  ryzyka.

### Hardening warstwy API

- Nagłówki bezpieczeństwa na wszystkich odpowiedziach (nawet błędach).
- Rate-limit (opcjonalnie globalny przez Redis) — z zasadą *fail-open* (awaria cache
  nie blokuje ruchu; dostępność > twardy limit).
- HSTS włączane za TLS w produkcji.

---

<a name="14"></a>
## 14. Zasady projektowe — filozofia „fail-safe" i dlaczego jest kluczowa

Przez cały kod przewija się jedna, konsekwentnie stosowana filozofia. Warto ją nazwać,
bo to ona odróżnia poważny system opieki od prototypu.

### 1. Fail-safe — „awaria nie może zaszkodzić"

Każdy element, który korzysta z zewnętrznych usług (model AI, synteza głosu, centrala
telefoniczna, powiadomienia, baza), jest zaprojektowany tak, że **w razie awarii lub
braku klucza nie wywraca systemu**, tylko grzecznie zwraca bezpieczną wartość lub
„nic nie robi" (no-op). Przykłady:
- LLM zawiódł w konsensusie → zostaje detektor regułowy, decyzja dalej zapada.
- Brak centrali telefonicznej → `call-start` zwraca „nie wykonano", ale API żyje.
- Baza niedostępna → `/health/ready` zwraca 503, proces nie pada.
- Kanał powiadomień „live" bez sekretu → zwraca „nie wysłano" zamiast rzucać błąd.

### 2. Bezpieczeństwo zawsze wygrywa

Semafor bierze **maksimum** z sygnałów, nie „gaśnie" sam, a AI może tylko **podnieść**
czujność. Przy niepewności system woli fałszywy alarm niż przeoczony kryzys.

### 3. Wytłumaczalność ponad „magię"

Krytyczne decyzje są regułowe i audytowalne. To nie jest „czarna skrzynka AI" — każdy
alarm da się uzasadnić i prześledzić w dzienniku zdarzeń.

### 4. Czysta logika, testowalna bez świata zewnętrznego

Logika rozmowy nie potrzebuje prawdziwego telefonu; logika bazy działa na SQLite
w pamięci. Dzięki temu **295 testów backendu + 29 testów frontendu** przechodzi
bez internetu, kluczy i kosztów — co daje pewność, że zmiany niczego nie psują.

### 5. Wymienność przez „porty" i adaptery

Usługi zewnętrzne są za kontraktami (portami). Można podmienić dostawcę TTS z OpenAI
na ElevenLabs bez dotykania logiki rozmowy. To chroni przed uzależnieniem od jednego
dostawcy i ułatwia rozwój.

### 6. Design light-only

Warstwa wizualna Adam Design System jest celowo **tylko jasna** (bez trybu ciemnego) —
dla czytelności i spójności, zwłaszcza w kontekście osób starszych i opiekunów.

---

<a name="15"></a>
## 15. Technologie — z czego to jest zbudowane i dlaczego akurat to

| Warstwa | Technologia | Dlaczego |
|---|---|---|
| **Język backendu** | Python | ekosystem AI/ML, czytelność, biblioteki senior-care |
| **Framework API** | FastAPI | szybki, nowoczesny, automatyczna dokumentacja (`/docs`), walidacja |
| **Baza (dev)** | SQLite | zero-konfiguracji, idealna do testów w pamięci |
| **Baza (prod)** | PostgreSQL | wydajność, niezawodność, skala produkcyjna |
| **ORM / migracje** | SQLAlchemy + Alembic | mapowanie tabel na obiekty + wersjonowanie schematu |
| **Telefonia** | Asterisk + ARI | otwarta, dojrzała centrala telefoniczna (VoIP) |
| **Rozpoznawanie mowy** | OpenAI Whisper | wysoka jakość STT, dobre wsparcie polskiego |
| **Model językowy** | OpenAI GPT (wymienny) | „mózg" rozmowy + klasyfikacja |
| **Synteza głosu** | OpenAI TTS / ElevenLabs | naturalny polski głos |
| **Frontend** | React + TypeScript + Vite | standard branżowy, typowanie, szybki build |
| **Stylowanie** | Tailwind CSS + Adam Design System | spójny, szybki, light-only |
| **Wykresy / ikony** | Recharts / Lucide | czytelne wizualizacje |
| **Mobile** | Capacitor (iOS + Android) | jeden kod → natywne aplikacje |
| **Powiadomienia** | Twilio (SMS), SendGrid (e-mail), FCM (push) | sprawdzeni dostawcy |
| **Rate-limit (opcj.)** | Redis | globalny limit współdzielony przez procesy |
| **Wyszukiwanie wiedzy** | RAG (embeddingi) | semantyczne przeszukiwanie dokumentacji projektu |

**Fundament open-source:** projekt wyrasta z **AVA** (AI Voice Agent for Asterisk,
licencja MIT), rozbudowanego o moduły senior-care, zgodność prawną i interfejsy.
Fonty (Fraunces + Geist) są na wolnej licencji SIL OFL.

---

<a name="16"></a>
## 16. Jak to wszystko jest spójne — przepływ danych od telefonu do panelu

Prześledźmy **jedną pełną ścieżkę** — od momentu, gdy Adam dzwoni, do chwili, gdy
rodzina widzi alert w telefonie. To pokazuje, jak wszystkie warstwy grają razem.

```
1. SCHEDULER (F2) o 9:00 planuje welfare-check dla pani Anny.
      │  tworzy CallAttempt, prosi telefonię o połączenie
      ▼
2. TELEFONIA (Asterisk/ARI + Stasis) dzwoni. Pani Anna odbiera.
      │  zdarzenie „odebrano" → StasisApp buduje sesję rozmowy
      ▼
3. DIALOG ENGINE (F5) otwiera rozmowę:
      │  → obowiązkowe ujawnienie AI (art. 50)  [zapis: disclosure_logs]
      ▼
4. Pani Anna mówi: „Dzień dobry… trochę mnie ściska w piersi."
      │  ASR (uszy) → tekst
      ▼
5. KONSENSUS (F16): detektor regułowy (F8) + głos LLM oceniają tekst.
      │  fraza „ściska w piersi" → Trigger.chest_pain → poziom PURPLE 🟣
      ▼
6. SEMAFOR (F3): poziom = maksimum = PURPLE. Zapis SemaphoreEvent.
      │  DialogEngine przerywa Q&A → stan ESCALATING
      ▼
7. Adam mówi spokojnie: „Słyszę, że dzieje się coś poważnego… zostaję na linii."
      │  TTS (usta) → głos w słuchawce
      ▼
8. DRABINA ESKALACJI (F3.2) dla PURPLE:
      │  → call_112 (z payloadem F17: adres, wiek, leki)
      │  → notify_coordinator (równolegle)
      │  → sms_family (bypass „nie przeszkadzać")
      ▼
9. POWIADOMIENIA (F9): adaptery SMS/e-mail/push wysyłają alert.
      │  zapis Notification w bazie
      ▼
10. API udostępnia stan przez /api/seniors/{id}/family/events (SSE, na żywo).
      ▼
11. PANEL OPIEKUNA odbiera zdarzenie → baner alertu 🟣 zapala się w telefonie córki.
      Córka widzi: kto, kiedy, jaki sygnał, jaki status eskalacji.
```

Każda strzałka to realny mechanizm opisany w rozdziałach 6–11. Zwróć uwagę, że
**dane płyną w jedną, spójną stronę**, a każdy etap zostawia audytowalny ślad w bazie.
To sprawia, że system jest przewidywalny, testowalny i zgodny z wymogami prawa.

---

<a name="17"></a>
## 17. Warianty pracy: tryb deweloperski vs produkcyjny

System celowo działa w **dwóch trybach**, przełączanych konfiguracją (zmiennymi
środowiskowymi) — bez zmiany kodu.

| Aspekt | Tryb DEWELOPERSKI (dev/test) | Tryb PRODUKCYJNY (prod) |
|---|---|---|
| Baza danych | SQLite (plik / pamięć) | PostgreSQL (Frankfurt DC) |
| Uszy (ASR) | `EchoASR` (atrapa) | `WhisperASR` (OpenAI) |
| Mózg (LLM) | `RuleLLM` (reguły) | `OpenAILLM` (GPT) |
| Usta (TTS) | `TextTTS` (atrapa) | `OpenAITTS` / `ElevenLabsTTS` |
| Telefonia | `FakeChannel` (symulacja) | Asterisk / ARI |
| Powiadomienia | `memory` / `null` | `live` (Twilio / SendGrid / FCM) |
| Rate-limit | in-memory (per proces) | Redis (globalny) |
| Klucze/sekrety | atrapowe (`dev`) | prawdziwe (z sejfu) |

Tryb dev pozwala rozwijać i testować **całość bez internetu, kont i kosztów**. Tryb
prod to ta sama logika, tylko z podłączonymi realnymi usługami. Przełączenie polega
wyłącznie na uzupełnieniu zmiennych (np. `OPENAI_API_KEY`, `ASTERISK_ARI_URL`,
`ADAM_DATABASE_URL`) — opisanych w `.env.adam.example` i `docs/DEPLOY-CHECKLIST.md`.

---

<a name="18"></a>
## 18. Przewagi konkurencyjne — dlaczego to jest wartościowe

1. **Zero bariery dla seniora.** Nie ma aplikacji do nauki, ekranów do obsługi,
   haseł do zapamiętania. Senior po prostu odbiera telefon — jak od wnuka.
2. **Wczesne wykrywanie, nie tylko reagowanie.** System łapie *narastające* sygnały
   (nastrój, sen, leki), a nie tylko katastrofy — tu ratuje się najwięcej.
3. **Bezpieczeństwo klasy medycznej.** Semafor „nie gaśnie sam", konsensus dwóch
   niezależnych głosów, twarde reguły kryzysowe, pełny audyt.
4. **Zgodność z prawem od pierwszego dnia.** RODO i AI Act nie są „dołożone później" —
   są wbudowane (ujawnienie AI, szyfrowanie, prawo do zapomnienia, rejestry).
5. **Fail-safe w każdej warstwie.** Awaria dostawcy nie kładzie systemu; opieka nad
   człowiekiem nie może zależeć od jednego API.
6. **Otwarty fundament + wymienność.** Baza open-source (MIT) i architektura portów
   chronią przed uzależnieniem od jednego dostawcy AI/telefonii.
7. **Trzy dopasowane interfejsy.** Senior, rodzina i koordynator dostają dokładnie to,
   czego potrzebują — nie jeden przeładowany ekran dla wszystkich.
8. **Gotowość mobilna.** Ten sam kod działa jako strona, PWA i natywna apka
   (iOS + Android) z biometrią i powiadomieniami push.
9. **Dojrzałość inżynierska.** 295 + 29 testów, migracje bazy, CI gotowe do aktywacji,
   healthchecki, metryki, obserwowalność — to poziom produkcyjny, nie prototyp.

---

<a name="19"></a>
## 19. Stan projektu i co pozostało do pełnego uruchomienia

### Co jest GOTOWE (po stronie kodu — ~89%)

- ✅ **Backend:** 18 modułów F1–F18, 12 routerów, 51 endpointów, 18 tabel, 7 migracji.
- ✅ **Warstwa głosowa:** dialog, detektor, konsensus, profil mowy, realne adaptery
  (Whisper/GPT/TTS/ElevenLabs), warstwa telefonii (Asterisk/ARI + Stasis).
- ✅ **Bezpieczeństwo:** JWT + role, szyfrowanie PII, rate-limit, nagłówki, RODO, AI Act.
- ✅ **Frontend:** Landing + Panel Opiekuna + Panel Admina (~25 ekranów), przełącznik
  mock/live, część funkcji już na żywym API.
- ✅ **Mobile:** projekty iOS/Android (Capacitor), biometria, powiadomienia.
- ✅ **Jakość:** 295 testów backendu, 29 testów frontendu, healthchecki, metryki,
  CI gotowe do aktywacji.

### Co pozostało (po stronie SilverTech — ~11%)

To **nie jest brak kodu**, lecz elementy infrastrukturalno-organizacyjne, których
nie da się dostarczyć z poziomu repozytorium:

1. **Infrastruktura docelowa** — serwer/klaster we Frankfurt DC: PostgreSQL, Redis,
   Asterisk (centrala VoIP), kontenery.
2. **Konta i klucze dostawców** — OpenAI, ElevenLabs, Twilio, SendGrid, FCM.
3. **Sekrety produkcyjne** — wygenerowanie `ADAM_JWT_SECRET`, kluczy szyfrujących PII.
4. **Aktywacja CI** — gotowy plik workflow czeka na uprawnienie `workflows` w repo.
5. **Konta mobilne** — Apple Developer + Google Play do publikacji aplikacji.

Pełna, praktyczna lista „zero-to-live" znajduje się w **`docs/DEPLOY-CHECKLIST.md`**,
a szczegóły techniczne w `docs/DEPLOY-ADAM.md` i `docs/BACKEND-DEPLOY.md`.

---

<a name="20"></a>
## 20. Słowniczek pojęć

- **Agent głosowy** — program, który rozmawia głosem przez telefon (tu: Adam).
- **API** — sposób, w jaki programy wymieniają dane (u nas HTTP + JSON).
- **Endpoint** — pojedynczy „adres" API, np. `GET /api/seniors`.
- **Backend / Frontend** — zaplecze (logika) / to, co widzi użytkownik.
- **Router** — grupa powiązanych endpointów (np. wszystko o lekach).
- **Middleware** — „bramka", przez którą przechodzi każde żądanie (bezpieczeństwo,
  limity, logowanie).
- **ASR / LLM / TTS** — rozpoznawanie mowy / model językowy / synteza mowy.
- **Port / adapter** — kontrakt „co robić" / konkretna implementacja „jak" (wymienna).
- **Semafor** — czterokolorowy wskaźnik stanu seniora (🟢🟡🔴🟣).
- **Trigger (wyzwalacz)** — konkretny sygnał (np. „ból w klatce"), który podnosi semafor.
- **Eskalacja** — automatyczny łańcuch powiadomień/działań po alarmie.
- **Konsensus** — łączenie kilku niezależnych ocen w jedną decyzję (fail-safe).
- **Fail-safe** — projekt odporny na awarie: błąd nie szkodzi, system nie pada.
- **RBAC** — kontrola dostępu oparta na rolach (kto co może).
- **JWT** — token uwierzytelniający (cyfrowa „przepustka" po zalogowaniu).
- **PII** — dane osobowe wrażliwe (np. PESEL, telefon) — u nas szyfrowane.
- **RODO / AI Act** — unijne przepisy o ochronie danych / o sztucznej inteligencji.
- **Welfare-check** — regularny telefon „kontrolny" sprawdzający samopoczucie.
- **Asterisk / ARI / Stasis** — centrala telefoniczna / jej interfejs / warstwa zdarzeń.
- **Migracja (Alembic)** — wersjonowany „przepis" na strukturę bazy danych.
- **Capacitor** — narzędzie zamieniające stronę w natywną aplikację mobilną.
- **RAG** — semantyczne przeszukiwanie dokumentów (baza wiedzy projektu).
- **SSE** — technika strumieniowania zdarzeń „na żywo" do przeglądarki.

---

> **Podsumowanie jednym zdaniem:** ADAM-2027 to dojrzały, wielowarstwowy system
> opieki nad seniorami, w którym empatyczny agent głosowy, czterokolorowy semafor
> bezpieczeństwa i drabina eskalacji łączą się z solidną warstwą API, szyfrowaną bazą,
> trzema interfejsami i konsekwentną filozofią „fail-safe", tworząc rozwiązanie gotowe
> po stronie kodu (~89%) i czekające jedynie na infrastrukturę oraz klucze SilverTech.

*Dokument wygenerowany na podstawie analizy realnego kodu repozytorium (stan: commit
na gałęzi `main`, 2026-07). Szczegóły techniczne: `docs/API.md`, `docs/AUDIT.md`,
`docs/MASTER-PLAN.md`, `docs/DEPLOY-CHECKLIST.md`.*
