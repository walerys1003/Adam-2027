/* ============================================================
   ADAM · Admin mock data
   Duże liczby prezentacyjne (1247 seniorów, 18.4K rozmów…)
   są agregatami; tabele pokazują reprezentatywne próbki.
   ============================================================ */

/* ---------- System KPIs ---------- */
export const ADMIN_KPIS = {
  seniorsTotal: 1247,
  seniorsActive: 1189,
  callsTotal: 18412,
  calls24h: 2314,
  agentsActive: 12,
  devicesTotal: 941,
  alertsOpen: 7,
  uptimePct: 99.94,
  avgLatencyMs: 780,
  successRatePct: 96.4,
}

export const SEMAPHORE_DISTRIBUTION = [
  { level: 'green', count: 1042 },
  { level: 'yellow', count: 158 },
  { level: 'red', count: 41 },
  { level: 'purple', count: 6 },
] as const

/* ---------- Seniors (sample of 1247) ---------- */
export interface AdminSenior {
  id: string
  name: string
  age: number
  district: string
  package: 'basic' | 'family' | 'premium'
  semaphore: 'green' | 'yellow' | 'red' | 'purple'
  coordinator: string
  lastCall: string
  adherence: number
}
const DISTRICTS = ['Wilda', 'Grunwald', 'Jeżyce', 'Stare Miasto', 'Winogrady', 'Nowe Miasto']
const COORDS = ['Anna Kowalczyk', 'Piotr Zieliński', 'Maria Lewandowska']
const PKGS = ['basic', 'family', 'premium'] as const
const SEMS = ['green', 'green', 'green', 'yellow', 'red', 'purple'] as const
const NAMES = [
  'Halina Wiśniewska', 'Marek Nowak', 'Zofia Kaczmarek', 'Tadeusz Baran', 'Irena Wójcik',
  'Stanisław Mazur', 'Krystyna Dąbrowska', 'Janusz Kowalski', 'Barbara Zając', 'Henryk Woźniak',
  'Genowefa Krawczyk', 'Ryszard Kaczmarek', 'Jadwiga Piotrowska', 'Czesław Grabowski', 'Wanda Nowakowska',
  'Zbigniew Pawlak', 'Teresa Michalska', 'Kazimierz Król', 'Danuta Wieczorek', 'Edward Jabłoński',
]
export const ADMIN_SENIORS: AdminSenior[] = Array.from({ length: 42 }, (_, i) => ({
  id: `SR-${String(1000 + i).padStart(5, '0')}`,
  name: NAMES[i % NAMES.length],
  age: 68 + (i % 22),
  district: DISTRICTS[i % DISTRICTS.length],
  package: PKGS[i % PKGS.length],
  semaphore: SEMS[i % SEMS.length],
  coordinator: COORDS[i % COORDS.length],
  lastCall: `${(i % 12) + 1} godz. temu`,
  adherence: 55 + ((i * 7) % 45),
}))

/* ---------- Call history (sample of 18.4K) ---------- */
export interface AdminCall {
  id: string
  senior: string
  agent: string
  startedAt: string
  duration: string
  outcome: 'green' | 'yellow' | 'red' | 'purple'
  toolsUsed: number
}
export const ADMIN_CALLS: AdminCall[] = Array.from({ length: 30 }, (_, i) => ({
  id: `CALL-${48210 - i}`,
  senior: NAMES[i % NAMES.length],
  agent: ['welfare-morning', 'welfare-evening', 'medication-reminder', 'crisis-detect'][i % 4] + ' v7.4.2',
  startedAt: `14:${String(59 - (i % 60)).padStart(2, '0')}`,
  duration: `${1 + (i % 6)}:${String((i * 13) % 60).padStart(2, '0')}`,
  outcome: SEMS[i % SEMS.length],
  toolsUsed: i % 5,
}))

/* ---------- Call scheduling campaigns ---------- */
export const CAMPAIGNS = [
  { id: 'C1', name: 'Poranny welfare-check', window: '07:00–09:00', seniors: 1189, agent: 'welfare-morning', status: 'active' },
  { id: 'C2', name: 'Przypomnienie o lekach', window: '12:00–13:00', seniors: 843, agent: 'medication-reminder', status: 'active' },
  { id: 'C3', name: 'Wieczorna rozmowa', window: '18:00–20:00', seniors: 1042, agent: 'welfare-evening', status: 'active' },
  { id: 'C4', name: 'Weekend companionship', window: 'Sob–Nd 10:00–12:00', seniors: 512, agent: 'companion', status: 'paused' },
]
// 24×7 heatmap of call volume
export const SCHEDULE_HEATMAP = Array.from({ length: 24 * 7 }, (_, i) => {
  const hour = i % 24
  const peak = hour >= 7 && hour <= 9 ? 0.9 : hour >= 18 && hour <= 20 ? 0.8 : hour >= 12 && hour <= 13 ? 0.6 : 0.1
  return { hour, value: Math.min(1, peak + (Math.sin(i) * 0.08)) }
})

/* ---------- Alerts + escalation ---------- */
export const ADMIN_ALERTS = [
  { id: 'AL-1', senior: 'Tadeusz Baran', level: 'purple', reason: 'AFib z objawami', stage: 'Auto-112 wywołane', age: '2 min', coordinator: 'Piotr Zieliński' },
  { id: 'AL-2', senior: 'Marek Nowak', level: 'red', reason: 'Wykryto upadek', stage: 'Kontakt z koordynatorem', age: '18 min', coordinator: 'Anna Kowalczyk' },
  { id: 'AL-3', senior: 'Zofia Kaczmarek', level: 'yellow', reason: 'Nastrój < 0.5', stage: 'Obserwacja', age: '3 godz.', coordinator: '—' },
]
export const ESCALATION_LADDER = [
  { step: 1, label: 'RED — ponowny telefon', detail: '3× co 20 s' },
  { step: 2, label: 'SMS do opiekuna', detail: 'natychmiast po nieudanych próbach' },
  { step: 3, label: 'Powiadomienie koordynatora', detail: 'dyżurny SilverTech' },
  { step: 4, label: 'PURPLE — auto-112', detail: 'protokół ratunkowy' },
]

/* ---------- Marketplace ---------- */
export const MARKET_ORDERS = ADMIN_CALLS.slice(0, 12).map((c, i) => ({
  id: `ORD-${9000 + i}`,
  senior: c.senior,
  category: ['Apteka', 'Zakupy', 'Transport', 'Posiłki'][i % 4],
  partner: ['DOZ', 'Frisco', 'iTaxi Senior', 'Lunching'][i % 4],
  amount: `${34 + i * 11} zł`,
  status: ['confirmed', 'waiting_manual_confirm', 'auto_confirmed'][i % 3],
}))
export const MARKET_CATALOG = [
  { id: 'cat-pharmacy', name: 'Apteka', mode: 'AUTO', partners: 14, orders30d: 842 },
  { id: 'cat-groceries', name: 'Zakupy spożywcze', mode: 'AUTO', partners: 9, orders30d: 611 },
  { id: 'cat-transport', name: 'Transport', mode: 'HYBRID', partners: 6, orders30d: 288 },
  { id: 'cat-care', name: 'Opieka', mode: 'MANUAL', partners: 22, orders30d: 134 },
]
export const MARKET_PARTNERS = Array.from({ length: 16 }, (_, i) => ({
  id: `PT-${100 + i}`,
  name: ['DOZ Apteka', 'Frisco.pl', 'iTaxi Senior', 'Lunching', 'Rossmann', 'Media Expert'][i % 6] + ` #${i + 1}`,
  nip: `${7000000000 + i * 137}`,
  rating: (4.2 + (i % 8) * 0.1).toFixed(1),
  category: ['Apteka', 'Zakupy', 'Transport', 'Posiłki'][i % 4],
  status: i % 5 === 0 ? 'pending' : 'active',
}))
export const SERVICE_GAPS = [
  { district: 'Winogrady', category: 'Transport medyczny', demand: 'wysoki', partners: 1 },
  { district: 'Nowe Miasto', category: 'Opieka nocna', demand: 'średni', partners: 0 },
  { district: 'Jeżyce', category: 'Rehabilitacja domowa', demand: 'wysoki', partners: 2 },
]

/* ---------- Agents ---------- */
export interface AdminAgent {
  id: string
  name: string
  role: string
  model: string
  voice: string
  status: 'active' | 'draft' | 'paused'
  calls30d: number
  successRate: number
}
export const ADMIN_AGENTS: AdminAgent[] = [
  { id: 'AG-1', name: 'welfare-morning', role: 'Poranny welfare-check', model: 'GPT-4o', voice: 'Zosia (PL)', status: 'active', calls30d: 34210, successRate: 97 },
  { id: 'AG-2', name: 'welfare-evening', role: 'Wieczorna rozmowa', model: 'GPT-4o', voice: 'Zosia (PL)', status: 'active', calls30d: 29880, successRate: 96 },
  { id: 'AG-3', name: 'medication-reminder', role: 'Przypomnienie leków', model: 'GPT-4o-mini', voice: 'Marek (PL)', status: 'active', calls30d: 21044, successRate: 98 },
  { id: 'AG-4', name: 'crisis-detect', role: 'Detekcja kryzysu', model: 'GPT-4o', voice: 'Zosia (PL)', status: 'active', calls30d: 1203, successRate: 99 },
  { id: 'AG-5', name: 'companion', role: 'Towarzystwo', model: 'GPT-4o', voice: 'Ala (PL)', status: 'active', calls30d: 8801, successRate: 95 },
  { id: 'AG-6', name: 'onboarding', role: 'Wdrożenie seniora', model: 'GPT-4o', voice: 'Marek (PL)', status: 'draft', calls30d: 0, successRate: 0 },
  { id: 'AG-7', name: 'marketplace-order', role: 'Zamówienia', model: 'GPT-4o-mini', voice: 'Marek (PL)', status: 'active', calls30d: 3120, successRate: 94 },
  { id: 'AG-8', name: 'family-update', role: 'Aktualizacje rodzina', model: 'GPT-4o-mini', voice: 'Ala (PL)', status: 'active', calls30d: 990, successRate: 97 },
  { id: 'AG-9', name: 'wearable-alert', role: 'Alerty z opaski', model: 'GPT-4o', voice: 'Zosia (PL)', status: 'active', calls30d: 445, successRate: 98 },
  { id: 'AG-10', name: 'satisfaction-survey', role: 'Ankieta satysfakcji', model: 'GPT-4o-mini', voice: 'Ala (PL)', status: 'paused', calls30d: 210, successRate: 92 },
  { id: 'AG-11', name: 'appointment-book', role: 'Umawianie wizyt', model: 'GPT-4o', voice: 'Marek (PL)', status: 'active', calls30d: 1502, successRate: 93 },
  { id: 'AG-12', name: 'emergency-112', role: 'Protokół 112', model: 'GPT-4o', voice: 'Zosia (PL)', status: 'active', calls30d: 41, successRate: 100 },
]

/* ---------- Providers ---------- */
export const PROVIDERS = [
  { id: 'P1', name: 'OpenAI', type: 'LLM', status: 'connected', models: 'GPT-4o, GPT-4o-mini', latency: '620 ms' },
  { id: 'P2', name: 'Azure Speech', type: 'STT/TTS', status: 'connected', models: 'pl-PL neural', latency: '210 ms' },
  { id: 'P3', name: 'ElevenLabs', type: 'TTS', status: 'connected', models: 'Multilingual v2', latency: '340 ms' },
  { id: 'P4', name: 'Deepgram', type: 'STT', status: 'connected', models: 'Nova-2', latency: '180 ms' },
  { id: 'P5', name: 'Anthropic', type: 'LLM', status: 'standby', models: 'Claude 3.5', latency: '—' },
  { id: 'P6', name: 'Twilio', type: 'Telefonia', status: 'connected', models: 'Programmable Voice', latency: '90 ms' },
  { id: 'P7', name: 'Pinecone', type: 'Vector DB', status: 'connected', models: 'serverless', latency: '45 ms' },
]

/* ---------- Pipelines ---------- */
export const PIPELINES = [
  { id: 'PL1', name: 'PL Standard', stt: 'Deepgram Nova-2', llm: 'GPT-4o', tts: 'Azure pl-PL', usedBy: 8 },
  { id: 'PL2', name: 'PL Premium (ElevenLabs)', stt: 'Deepgram Nova-2', llm: 'GPT-4o', tts: 'ElevenLabs v2', usedBy: 3 },
  { id: 'PL3', name: 'PL Lite', stt: 'Azure', llm: 'GPT-4o-mini', tts: 'Azure pl-PL', usedBy: 1 },
  { id: 'PL4', name: 'Crisis (low-latency)', stt: 'Deepgram', llm: 'GPT-4o', tts: 'Azure', usedBy: 1 },
]

/* ---------- Audio profiles ---------- */
export const AUDIO_PROFILES = [
  { id: 'A1', name: 'Senior-Clear', desc: 'Wolniejsze tempo, wyższa głośność, pauzy', effectiveness: 91, usedBy: 9 },
  { id: 'A2', name: 'Standard', desc: 'Naturalne tempo', effectiveness: 84, usedBy: 2 },
  { id: 'A3', name: 'Niedosłuch+', desc: 'Kompresja dynamiki, akcent na spółgłoski (F13)', effectiveness: 88, usedBy: 1 },
]

/* ---------- Tools (47, 4 phases) ---------- */
export const TOOLS = Array.from({ length: 47 }, (_, i) => ({
  id: `TL-${i + 1}`,
  name: [
    'get_senior_profile', 'log_mood', 'set_semaphore', 'create_order', 'cancel_order',
    'get_medications', 'confirm_medication', 'get_wearable_vitals', 'escalate_alert', 'call_112',
    'send_family_sms', 'schedule_call', 'get_weather', 'read_news', 'play_music',
  ][i % 15] + (i > 14 ? `_v${Math.floor(i / 15) + 1}` : ''),
  phase: (['F3', 'F6', 'F8', 'F11'] as const)[i % 4],
  enabled: i % 7 !== 0,
}))

/* ---------- MCP servers ---------- */
export const MCP_SERVERS = [
  { id: 'M1', name: 'health-records-mcp', status: 'connected', tools: 8, transport: 'stdio' },
  { id: 'M2', name: 'marketplace-mcp', status: 'connected', tools: 6, transport: 'sse' },
  { id: 'M3', name: 'wearables-mcp', status: 'connected', tools: 5, transport: 'sse' },
]
export const MCP_CATALOG = [
  'calendar-mcp', 'pharmacy-mcp', 'transport-mcp', 'weather-mcp', 'news-mcp', 'emergency-mcp',
]

/* ---------- Wearables fleet (941) ---------- */
export interface FleetDevice {
  id: string
  senior: string
  brand: 'xiaomi' | 'apple' | 'garmin' | 'fitbit'
  model: string
  battery: number
  sync: 'ok' | 'delayed' | 'offline'
  firmware: string
  mode: 'auto' | 'manual_override'
}
const BRANDS = ['xiaomi', 'apple', 'garmin', 'fitbit'] as const
const MODELS: Record<string, string> = { xiaomi: 'Band 8', apple: 'Watch SE', garmin: 'vívosmart 5', fitbit: 'Charge 6' }
export const FLEET_DEVICES: FleetDevice[] = Array.from({ length: 40 }, (_, i) => {
  const brand = BRANDS[i % 4]
  return {
    id: `DEV-${String(700 + i).padStart(4, '0')}`,
    senior: NAMES[i % NAMES.length],
    brand,
    model: MODELS[brand],
    battery: 20 + ((i * 13) % 80),
    sync: (['ok', 'ok', 'delayed', 'offline'] as const)[i % 4],
    firmware: `v${2 + (i % 3)}.${i % 10}.${i % 5}`,
    mode: i % 6 === 0 ? 'manual_override' : 'auto',
  }
})
export const FLEET_STATS = { total: 941, ok: 872, delayed: 51, offline: 18, overrides: 63 }
export const FLEET_AUDIT = [
  { id: 'AU-1', device: 'DEV-0700', action: 'Zmiana progów HR (48–105)', by: 'dr Maria Lewandowska', role: 'doctor', at: '2026-07-13 09:20' },
  { id: 'AU-2', device: 'DEV-0713', action: 'Reset do trybu auto', by: 'Anna Kowalczyk', role: 'coordinator', at: '2026-07-12 16:44' },
  { id: 'AU-3', device: 'DEV-0725', action: 'Parowanie urządzenia', by: 'System', role: 'system', at: '2026-07-11 11:02' },
]

/* ---------- Environment (78 vars) ---------- */
export interface EnvVar {
  key: string
  value: string
  category: string
  secret?: boolean
  modified?: boolean
}
export const ENV_VARS: EnvVar[] = [
  { key: 'OPENAI_API_KEY', value: 'sk-••••••••••••', category: 'Providers', secret: true },
  { key: 'AZURE_SPEECH_KEY', value: '••••••••', category: 'Providers', secret: true },
  { key: 'ELEVENLABS_API_KEY', value: '••••••••', category: 'Providers', secret: true },
  { key: 'TWILIO_ACCOUNT_SID', value: 'AC••••••', category: 'Telefonia', secret: true },
  { key: 'ASTERISK_ARI_URL', value: 'http://asterisk:8088/ari', category: 'Telefonia' },
  { key: 'ASTERISK_ARI_USER', value: 'adam', category: 'Telefonia' },
  { key: 'DATABASE_URL', value: 'postgres://•••@db:5432/adam', category: 'Baza danych', secret: true },
  { key: 'REDIS_URL', value: 'redis://redis:6379/0', category: 'Baza danych' },
  { key: 'PINECONE_INDEX', value: 'adam-memory', category: 'Wektory' },
  { key: 'ADAM_VERSION', value: '7.4.2', category: 'Aplikacja', modified: true },
  { key: 'SEMAPHORE_RETRY_COUNT', value: '3', category: 'Semafor', modified: true },
  { key: 'SEMAPHORE_RETRY_INTERVAL_S', value: '20', category: 'Semafor' },
  { key: 'EMERGENCY_NUMBER', value: '112', category: 'Semafor' },
  { key: 'GDPR_RETENTION_DAYS', value: '30', category: 'RODO' },
  { key: 'LOG_LEVEL', value: 'INFO', category: 'Aplikacja' },
]
export const ENV_CATEGORIES = ['Wszystkie', 'Providers', 'Telefonia', 'Baza danych', 'Wektory', 'Aplikacja', 'Semafor', 'RODO']

/* ---------- Docker services ---------- */
export const DOCKER_SERVICES = [
  { id: 'D1', name: 'adam-agent', image: 'adam/agent:7.4.2', status: 'running', cpu: '12%', mem: '340 MB', uptime: '6d 4h' },
  { id: 'D2', name: 'asterisk', image: 'asterisk:20-lts', status: 'running', cpu: '8%', mem: '210 MB', uptime: '6d 4h' },
  { id: 'D3', name: 'postgres', image: 'postgres:16', status: 'running', cpu: '4%', mem: '512 MB', uptime: '6d 4h' },
  { id: 'D4', name: 'redis', image: 'redis:7-alpine', status: 'running', cpu: '1%', mem: '48 MB', uptime: '6d 4h' },
]

/* ---------- Asterisk ---------- */
export const ASTERISK_STATUS = {
  ariConnected: true,
  activeChannels: 14,
  registeredEndpoints: 6,
  modules: ['res_ari', 'chan_pjsip', 'app_stasis', 'res_http_websocket', 'codec_opus'],
}

/* ---------- Models catalog ---------- */
export const MODELS_CATALOG = [
  { id: 'MD1', name: 'GPT-4o', type: 'LLM', provider: 'OpenAI', context: '128K', cost: '$5/1M' },
  { id: 'MD2', name: 'GPT-4o-mini', type: 'LLM', provider: 'OpenAI', context: '128K', cost: '$0.15/1M' },
  { id: 'MD3', name: 'Claude 3.5 Sonnet', type: 'LLM', provider: 'Anthropic', context: '200K', cost: '$3/1M' },
  { id: 'MD4', name: 'Nova-2', type: 'STT', provider: 'Deepgram', context: '—', cost: '$0.0043/min' },
  { id: 'MD5', name: 'Azure Neural pl-PL', type: 'TTS', provider: 'Azure', context: '—', cost: '$16/1M znaków' },
  { id: 'MD6', name: 'ElevenLabs Multilingual v2', type: 'TTS', provider: 'ElevenLabs', context: '—', cost: '$0.30/1K znaków' },
]

/* ---------- Live logs ---------- */
export const LOG_LINES = [
  { level: 'INFO', at: '14:22:01', msg: 'welfare-morning: call SR-01042 started (channel PJSIP/adam-0001)' },
  { level: 'INFO', at: '14:22:04', msg: 'STT stream opened · Deepgram Nova-2 · pl-PL' },
  { level: 'DEBUG', at: '14:22:09', msg: 'tool_call: get_medications(senior_id=SR-01042)' },
  { level: 'INFO', at: '14:22:12', msg: 'semaphore evaluated → GREEN (mood=0.71, adherence=0.94)' },
  { level: 'WARN', at: '14:23:47', msg: 'wearable-alert: SR-02341 HR=118 > threshold 110 · escalating' },
  { level: 'ERROR', at: '14:24:02', msg: 'crisis-detect: SR-03190 AFib symptoms · PURPLE · auto-112 triggered' },
  { level: 'INFO', at: '14:24:03', msg: 'emergency-112 dialplan invoked · coordinator Piotr Zieliński notified' },
]

/* ---------- Setup wizard steps ---------- */
export const WIZARD_STEPS = [
  { id: 1, title: 'Organizacja', desc: 'Dane SilverTech, dzielnice, koordynatorzy' },
  { id: 2, title: 'Telefonia', desc: 'Asterisk ARI + Twilio SIP trunk' },
  { id: 3, title: 'Providers AI', desc: 'OpenAI, STT/TTS, klucze API' },
  { id: 4, title: 'Agenci', desc: 'Import 12 agentów welfare + semafor' },
  { id: 5, title: 'Uruchomienie', desc: 'Weryfikacja i pierwsza kampania' },
]
