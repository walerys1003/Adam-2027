# Panel Opiekuna — Mapa Ekranów

**Plik referencyjny:** `Panel Opiekuna.html`
**Route prefix:** `/panel`
**Layout:** Sidebar (240px) + TopBar + Main content

---

## Ekrany

### 1. Dashboard · `/panel`
**Sidebar item:** Dashboard (active default)
**Zawartość:**
- Page head: "Dzień dobry, Anno" · Wtorek 12 lipca · Live · Odświeżenie 14:22
- Krytyczny alert banner (warunkowy, jeśli jest RED/PURPLE)
- KPI strip 4 kart: Twoi bliscy · Rozmowy 7d · Śr. adherence · Alerty 30d
- Section "Moi bliscy" z listą kart seniorów (SeniorCard z semaforem)

**Komponenty do zbudowania:**
- `<Dashboard />` container
- `<CriticalAlertBanner />` (warunkowy, level='red' | 'purple')
- `<KPIStrip />` (4 kart)
- `<SeniorList senior="mine" />`

**API endpoints:**
- `GET /api/seniors/mine` — lista
- `GET /api/alerts/active` — dla banner
- `GET /api/stats/mine?range=30d` — KPI
- Subscribe SSE: `/api/events?filter=alerts`

---

### 2. Widok seniora · `/panel/senior/:id`
**Sidebar item:** Moi bliscy (badge count)
**Zawartość:**
- **DetailHead** z awatarem 88px, semaforem, 5 quick stats
- **Actions** right: last call time + Zadzwoń teraz / Notatka / Kontakt rodziny
- **Tabs bar** — 8 tabów:

#### 2.1 Tab: Przegląd (`?tab=overview`)
- 2/1 grid split
- Lewo: **MoodChart 14d** + **RecentCalls list** (3 ostatnie)
- Prawo: **MedicationList summary** + **AI Observations** + **EmergencyContactList**

#### 2.2 Tab: Rozmowy (`?tab=calls`) — count 147
- Full table transkrypty + tools użyte + audio playback

#### 2.3 Tab: Leki (`?tab=meds`) — count 4
- Harmonogram leków (rano/południe/wieczór ikons)
- Kalendarz adherence 30d (heatmap 7×5)

#### 2.4 Tab: Wearable (`?tab=wearable`) — Xiaomi
- Live vitals grid 4 kart (HR/SpO₂/Kroki/Sen)
- **HR chart 24h** z threshold band
- **Sleep phases** kolorowy pasek
- **Steps 7d** słupki
- Prawa kolumna: kalibracja + notatki kontekstowe + progi (**READ ONLY**)

#### 2.5 Tab: Alerty (`?tab=alerts`) — count 3
- Historia z timeline

#### 2.6 Tab: Raporty (`?tab=reports`)
- Weekly/Monthly PDF cards

#### 2.7 Tab: Rodzina · RBAC (`?tab=family`)
- Kontakty alarmowe z rolami (Opiekun Główny / Opiekun / Lekarz / 112)

#### 2.8 Tab: RODO · Zgody (`?tab=gdpr`)
- Zgody z datami + retention + prawo do usunięcia

**Komponenty:**
- `<SeniorDetail seniorId={id} />` główny wrapper
- `<SeniorDetailHead />`
- `<Tabs value={activeTab} onChange={setTab} />`
- Wszystkie tab-panels jako lazy

**API endpoints:**
- `GET /api/seniors/:id` — full detail
- `GET /api/seniors/:id/mood?range=14d`
- `GET /api/seniors/:id/calls?limit=20`
- `GET /api/seniors/:id/wearable/live` — WebSocket
- `GET /api/seniors/:id/alerts`
- `GET /api/seniors/:id/reports`
- `POST /api/seniors/:id/contextual-notes` — soft context

---

### 3. Zamówienia · `/panel/orders`
**Sidebar item:** Zamówienia (badge count active orders)
**Zawartość:**
- Info banner "Jak to działa" — 30-min okno anulowania
- Section: Aktywne zamówienia
  - Karta ze złotym paskiem (zamówione przez Adama, w 30-min oknie) z **countdown 27:00**
  - Karta z zielonym paskiem (w realizacji, mapa taxi)
  - Karta z żółtym paskiem (oczekuje potwierdzenia koordynatora)
- Section: Zamów w imieniu bliskiego
  - Wybór seniora
  - Grid 10 kategorii z tagami AUTO/HYBRID/MANUAL
- Section: Historia 30d — 24 zamówienia, 3247 zł, 4.7★

**Komponenty:**
- `<OrderCard order={} withCountdown />`
- `<CategoryPicker seniors={} />`
- `<CancellationCountdown createdAt={} />` — hook z useOrderCancellationWindow

**API:**
- `GET /api/orders?status=active`
- `POST /api/orders` — złóż w imieniu
- `DELETE /api/orders/:id` — anuluj (jeśli w oknie)

---

### 4. Wiadomości · `/panel/messages`
**Sidebar item:** Wiadomości (badge count unread)
**Zawartość:**
- **3-column inbox layout**:
  - Lewo (220px): filtry źródeł (Adam / Koordynator / Rodzina / Partnerzy) + kategorie
  - Środek (380px): lista wiadomości z avatarami, previewem, badges
  - Prawo (flex): wątek — header + body + reply box + ▶ audio

**Komponenty:**
- `<InboxFilters filters={} onChange={} />`
- `<MessageList messages={} selectedId={} onSelect={} />`
- `<MessageThread message={} onReply={} />`

**API:**
- `GET /api/messages?source=all&status=unread`
- `GET /api/messages/:id/thread`
- `POST /api/messages/:id/reply`

---

### 5. Raporty · `/panel/reports`
**Sidebar item:** Raporty
**Zawartość:**
- 5 KPI: raporty 30d · wysłane lekarzowi · **mood trend +0.04** · **adherence 96%** · auto-wysyłka
- Wielki wykres trendu 90d (mood + adherence overlay + alert markers)
- Featured card najnowszy (tygodniowy 05-12 lip) ze złotą obwódką:
  - 4 metryki z sparklinami
  - Timeline 7 dni ✓/! kafle
  - Actions: PDF / Podgląd / Share / Lekarzowi
- Prawa kolumna: **Delivery config** + **Share link** (adam.silvertech.pl/r/hw-...)
- Section: Raport miesięczny czerwiec (granatowo-złota karta) z DELIVERED status
- Section: Kalendarz heatmap 6 mies. (26 tygodni · zielone/złote/dashed)
- Table archiwum
- FHIR + Retencja side-by-side

**Komponenty:**
- `<ReportsTrendChart range="90d" />`
- `<FeaturedReport report={} />`
- `<ReportsCalendarHeatmap months={6} />`
- `<FHIRExportInfo />`

**API:**
- `GET /api/reports?limit=20&sortBy=newest`
- `GET /api/reports/:id.pdf`
- `GET /api/reports/:id.fhir`
- `POST /api/reports/:id/send-to-doctor`
- `POST /api/reports/:id/share-link` — generate URL

---

### 6. Konto · `/panel/account`
**Sidebar item:** Konto
**Zawartość:**
- Page head: "Twoje konto · Anna Chmielewska" · "Członkini SilverTech od 12 marca 2026"
- **Subscription Hero** — granatowo-złota karta (Rodzinny 79 zł/mies + 4 stats + CTA Upgrade Premium)
- Prawa kolumna: **Loyalty card** (4 miesiące → Adam Loyal ★★ za 3 mies.) + **Referral card** (30 zł dla obojga)
- **Banner roli** — Opiekun Główny ★ z uprawnieniami inline
- **Dane osobowe** + **Twoi bliscy 1/5** grid 2-col
- **"Twój Adam · 4 miesiące"** — 4 KPI usage stats
- **Aktywne sesje** — 3 karty grid (MacBook z ★ TA SESJA, iPhone Face ID, iPad nieaktywna)
- **Faktury** — split (summary 373 zł + Visa card) + tabela historia

**Komponenty:**
- `<SubscriptionHero plan={} />`
- `<LoyaltyProgress startDate={} />` — progress bar
- `<ReferralCard code={} referrals={} />`
- `<SessionCard device={} isCurrent={} />`
- `<InvoiceTable invoices={} />`

**API:**
- `GET /api/me/subscription`
- `GET /api/me/sessions`
- `DELETE /api/me/sessions/:id` — wyloguj
- `GET /api/me/invoices`

---

### 7. Ustawienia · `/panel/settings`
**Sidebar item:** Ustawienia
**Zawartość:**
- **Sticky sidebar** z 6 sekcji + status box "12/12 skonfigurowane"
- Sekcje (przewijalne):

#### 7.1 🔔 Powiadomienia · matryca semafora
- **Table 5 wierszy × 4 kolumny** (Push / SMS / E-mail / Telefon × Green / Yellow / Red / Purple)
- Custom switches (`<Switch />` z Radix, styled Adam)
- **Purple × Telefon** — locked switch (checked + disabled) + "WYMAGANE" badge
- Warning banner: Purple bypass DND

#### 7.2 🌙 Godziny ciszy
- Enabled switch + Od/Do inputs mono centered + strefa czasowa + weekend override

#### 7.3 🌍 Język i region
- 4 dropdowns styled: język, format daty, format godziny, waluta

#### 7.4 🛡 Bezpieczeństwo
- 2FA active card (green)
- Zmień hasło card
- Auto-wylogowanie card z dropdown 30/7/nigdy

#### 7.5 📜 RODO · Prywatność
- 4 kolorowe karty (Pobierz / Sprostuj / Przenieś / Usuń)
- Wielki granatowy banner "Ochrona danych medycznych mamy" ze złotym akcentem + linki

**Komponenty:**
- `<NotificationMatrix />` — key component, matryca 5×5
- `<QuietHoursCard />`
- `<LanguageCard />`
- `<SecurityCard />`
- `<GDPRCard />` — Pobierz/Sprostuj/Przenieś/Usuń

**API:**
- `GET /api/me/settings` / `PATCH /api/me/settings`
- `POST /api/me/gdpr/export-request`
- `DELETE /api/me` (soft delete + 30-day grace period)

---

### 8. Pomoc · `/panel/help`
**Sidebar item:** Pomoc
**Zawartość:**
- 4 KPI status: Twój ticket · Koordynatorzy online 3 · Śr. odpowiedź 8min · Historia 4 rozwiązane
- **Emergency box** (czerwony gradient) — 24/7 · +48 61 22 44 000
- **3 kanały wsparcia grid**: Chat / Telefon / E-mail
- **Wideoporadniki** — 4 video preview cards z time badges
- **FAQ** — 6 pytań accordion (jedno rozwinięte)
- **Kontakt z zespołem** + **Społeczność opiekunów** grid 2-col

**Komponenty:**
- `<SupportStatusBar />`
- `<EmergencyBox />`
- `<SupportChannel type="chat" | "phone" | "email" />`
- `<VideoTutorial thumbnail={} duration={} />`
- `<FAQAccordion items={} />`

**API:**
- `GET /api/support/status` — coordinators online
- `POST /api/support/chat` — start chat session
- `POST /api/support/ticket` — create ticket
