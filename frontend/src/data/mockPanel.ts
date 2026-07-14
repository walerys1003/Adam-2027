import type { OrderCategory, Thread, Invoice, Session, Order } from '@/types/domain'

/* ---------- Marketplace categories (10) ---------- */
export const ORDER_CATEGORIES: OrderCategory[] = [
  { id: 'pharmacy', label: 'Apteka', icon: 'Pill', examples: 'Leki, recepty, suplementy' },
  { id: 'groceries', label: 'Zakupy spożywcze', icon: 'ShoppingCart', examples: 'Pieczywo, nabiał, warzywa' },
  { id: 'meals', label: 'Posiłki', icon: 'UtensilsCrossed', examples: 'Obiady, catering dietetyczny' },
  { id: 'transport', label: 'Transport', icon: 'Car', examples: 'Wizyta u lekarza, do rodziny' },
  { id: 'cleaning', label: 'Sprzątanie', icon: 'Sparkles', examples: 'Mieszkanie, okna, pranie' },
  { id: 'repair', label: 'Drobne naprawy', icon: 'Wrench', examples: 'Hydraulik, elektryk, złota rączka' },
  { id: 'care', label: 'Opieka', icon: 'HeartHandshake', examples: 'Pielęgniarka, rehabilitant' },
  { id: 'companion', label: 'Towarzystwo', icon: 'Users', examples: 'Spacer, rozmowa, wolontariat' },
  { id: 'beauty', label: 'Fryzjer / kosmetyka', icon: 'Scissors', examples: 'Fryzjer domowy, pedicure' },
  { id: 'other', label: 'Inne', icon: 'Package', examples: 'Zgłoszenie indywidualne' },
]

/* ---------- Existing seeded orders ---------- */
export const SEED_ORDERS: Order[] = [
  {
    orderId: 'O-4821',
    seniorId: 'HW-01247',
    categoryId: 'pharmacy',
    status: 'waiting_manual_confirm',
    requestSource: 'adam-call',
    cancellationWindowEndsAt: new Date(Date.now() + 4 * 60 * 1000).toISOString(),
    partner: { name: 'DOZ · Apteka św. Marcin', nip: '7831234567', rating: 4.8 },
    estimatedPrice: '34 zł',
    estimatedDelivery: '45 min',
    createdAt: new Date(Date.now() - 60 * 1000).toISOString(),
  },
  {
    orderId: 'O-4790',
    seniorId: 'ZK-00812',
    categoryId: 'groceries',
    status: 'confirmed',
    requestSource: 'caregiver-panel',
    partner: { name: 'Frisco.pl', nip: '5213851671', rating: 4.6 },
    estimatedPrice: '128 zł',
    estimatedDelivery: 'jutro 10–12',
    createdAt: new Date(Date.now() - 3 * 3600 * 1000).toISOString(),
  },
  {
    orderId: 'O-4712',
    seniorId: 'IW-04455',
    categoryId: 'transport',
    status: 'auto_confirmed',
    requestSource: 'adam-call',
    partner: { name: 'iTaxi · Senior', nip: '5252544173', rating: 4.9 },
    estimatedPrice: '52 zł',
    estimatedDelivery: '15 min',
    createdAt: new Date(Date.now() - 26 * 3600 * 1000).toISOString(),
  },
]

/* ---------- Messages / Threads ---------- */
export const MOCK_THREADS: Thread[] = [
  {
    id: 'T-1',
    subject: 'Alert: Wykryto upadek — Marek Nowak',
    seniorId: 'MN-02341',
    seniorName: 'Marek Nowak',
    category: 'alert',
    lastMessageAt: new Date(Date.now() - 20 * 60 * 1000).toISOString(),
    unread: 1,
    messages: [
      { id: 'm1', from: 'system', authorName: 'System Adam', body: 'Apple Watch SE wykrył upadek o 06:22. Semafor: CZERWONY.', timestamp: new Date(Date.now() - 40 * 60 * 1000).toISOString(), read: true },
      { id: 'm2', from: 'coordinator', authorName: 'Anna Kowalczyk', body: 'Dzwonię do pana Marka. Proszę pozostać w gotowości.', timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(), read: true },
      { id: 'm3', from: 'coordinator', authorName: 'Anna Kowalczyk', body: 'Kontakt nawiązany — fałszywy alarm, telefon spadł z nocnej szafki. Semafor wraca do zielonego.', timestamp: new Date(Date.now() - 20 * 60 * 1000).toISOString(), read: false },
    ],
  },
  {
    id: 'T-2',
    subject: 'Raport miesięczny — Halina Wiśniewska (czerwiec)',
    seniorId: 'HW-01247',
    seniorName: 'Halina Wiśniewska',
    category: 'report',
    lastMessageAt: new Date(Date.now() - 2 * 86400 * 1000).toISOString(),
    unread: 0,
    messages: [
      { id: 'm4', from: 'adam', authorName: 'Adam', body: 'Raport za czerwiec jest gotowy. Nastrój stabilny (70%), adherencja leków 93%.', timestamp: new Date(Date.now() - 2 * 86400 * 1000).toISOString(), read: true },
    ],
  },
  {
    id: 'T-3',
    subject: 'Przypomnienie: przegląd progów wearable',
    category: 'system',
    lastMessageAt: new Date(Date.now() - 5 * 86400 * 1000).toISOString(),
    unread: 1,
    messages: [
      { id: 'm5', from: 'system', authorName: 'System Adam', body: 'Progi alarmowe dla Apple Watch SE (Marek N.) wymagają zatwierdzenia przez koordynatora medycznego.', timestamp: new Date(Date.now() - 5 * 86400 * 1000).toISOString(), read: false },
    ],
  },
]

/* ---------- Account ---------- */
export const MOCK_INVOICES: Invoice[] = [
  { id: 'FV/2026/07', period: 'Lipiec 2026', amount: '249 zł', status: 'pending' },
  { id: 'FV/2026/06', period: 'Czerwiec 2026', amount: '249 zł', status: 'paid' },
  { id: 'FV/2026/05', period: 'Maj 2026', amount: '249 zł', status: 'paid' },
  { id: 'FV/2026/04', period: 'Kwiecień 2026', amount: '199 zł', status: 'paid' },
]

export const MOCK_SESSIONS: Session[] = [
  { id: 'S-1', device: 'Chrome · Windows', location: 'Poznań, PL', lastActive: 'teraz', current: true },
  { id: 'S-2', device: 'Adam iOS · iPhone 13', location: 'Poznań, PL', lastActive: '2 godz. temu', current: false },
  { id: 'S-3', device: 'Safari · iPad', location: 'Warszawa, PL', lastActive: '3 dni temu', current: false },
]
