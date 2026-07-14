/* ============================================================
   ADAM · Real API adapter (ETAP 10)
   Mapuje kontrakt backendu FastAPI (adam_modules/api, ETAP 9)
   na frontendowe typy domenowe (src/types/domain.ts).

   Backend zwraca węższy model (bez mood/adherence per-punkt),
   więc adapter uzupełnia brakujące pola sensownymi wartościami
   pochodnymi (np. adherence z /medications/adherence, mood z
   heurystyki na podstawie poziomu semafora), zachowując 100%
   zgodność sygnatur z mockApi.
   ============================================================ */

import type {
  Senior,
  SeniorDetail,
  MoodPoint,
  AlertMarker,
  District,
  Package,
  SemaphoreLevel,
  Order,
  User,
  Role,
  Thread,
  Message,
  Invoice,
  Session,
} from '@/types/domain'
import type { LoginPayload, LoginResult } from './mockApi'

/* ---------- surowe kształty backendu (ETAP 9) ---------- */

export interface BackendSenior {
  id: number
  external_id: string
  first_name: string
  last_name: string
  birth_date?: string | null
  address?: string | null
  district?: string | null
  package: Package
  semaphore: SemaphoreLevel
  active: boolean
  age?: number | null
  pesel_masked?: string | null
  phone_masked?: string | null
  created_at?: string | null
}

export interface BackendSeniorList {
  items: BackendSenior[]
  total: number
  limit: number
  offset: number
}

export interface BackendAdherence {
  senior_id: number
  total_doses: number
  taken: number
  missed: number
  late: number
  skipped: number
}

export interface BackendOrder {
  id: number
  service_id: number
  senior_id: number
  status: string
  amount_pln: number
  note?: string | null
  cancellable_until?: string | null
  can_cancel: boolean
}

/** Kontrakt backendu ETAP 11 — /api/auth/login|refresh (TokenOut). */
export interface BackendTokenOut {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  role: string
  senior_ids: string[]
}

/** Kontrakt backendu ETAP 11 — GET /api/auth/me (MeOut). */
export interface BackendMe {
  email: string
  role: string
  senior_ids: string[]
}

/** Backend Role (family|coordinator|admin) → frontend Role. */
export function mapRole(backendRole: string): Role {
  switch (backendRole) {
    case 'admin': return 'admin'
    case 'coordinator': return 'caregiver'
    case 'family': return 'family_member'
    default: return 'caregiver'
  }
}

/* ---------- kształty backendu ETAP 22 (/api/account) ---------- */

export interface BackendMessage {
  id: string
  from: Message['from']
  author_name: string
  body: string
  timestamp: string
  read: boolean
}

export interface BackendThread {
  id: string
  subject: string
  senior_id?: string | null
  senior_name?: string | null
  category: Thread['category']
  last_message_at: string
  unread: number
  messages: BackendMessage[]
}

export interface BackendInvoice {
  id: string
  period: string
  amount: string
  status: Invoice['status']
}

export interface BackendSession {
  id: string
  device: string
  location: string
  last_active: string
  current: boolean
}

export function mapMessage(m: BackendMessage): Message {
  return {
    id: m.id,
    from: m.from,
    authorName: m.author_name,
    body: m.body,
    timestamp: m.timestamp,
    read: m.read,
  }
}

export function mapThread(t: BackendThread): Thread {
  return {
    id: t.id,
    subject: t.subject,
    seniorId: t.senior_id ?? undefined,
    seniorName: t.senior_name ?? undefined,
    category: t.category,
    lastMessageAt: t.last_message_at,
    unread: t.unread,
    messages: t.messages.map(mapMessage),
  }
}

export function mapInvoice(b: BackendInvoice): Invoice {
  return { id: b.id, period: b.period, amount: b.amount, status: b.status }
}

export function mapSession(b: BackendSession): Session {
  return {
    id: b.id,
    device: b.device,
    location: b.location,
    lastActive: b.last_active,
    current: b.current,
  }
}

/* ---------- helpery mapujące ---------- */

const KNOWN_DISTRICTS: District[] = [
  'Wilda', 'Grunwald', 'Jeżyce', 'Stare Miasto', 'Winogrady', 'Nowe Miasto',
]

export function mapDistrict(d?: string | null): District {
  const found = KNOWN_DISTRICTS.find((k) => k === d)
  return found ?? 'Stare Miasto'
}

/** Heurystyczny nastrój 0..1 z poziomu semafora (gdy backend nie ma metryki). */
export function moodFromSemaphore(level: SemaphoreLevel): number {
  switch (level) {
    case 'green': return 0.82
    case 'yellow': return 0.58
    case 'red': return 0.34
    case 'purple': return 0.18
  }
}

/** Adherence 0..100 z raportu dawek (taken/total). */
export function adherencePct(a?: BackendAdherence | null): number {
  if (!a || a.total_doses <= 0) return 0
  return Math.round((a.taken / a.total_doses) * 100)
}

/** Deterministyczny trend 7-dniowy wokół wartości bazowej (bez losowości). */
export function moodTrend(base: number): number[] {
  const deltas = [-0.06, -0.03, 0.0, 0.02, -0.01, 0.03, 0.01]
  return deltas.map((d) => Math.max(0, Math.min(1, +(base + d).toFixed(2))))
}

export function mapSenior(b: BackendSenior, adherence?: BackendAdherence | null): Senior {
  const mood = moodFromSemaphore(b.semaphore)
  return {
    id: b.external_id,
    firstName: b.first_name,
    lastName: b.last_name,
    age: b.age ?? 0,
    district: mapDistrict(b.district),
    address: b.address ?? undefined,
    package: b.package,
    semaphore: b.semaphore,
    mood,
    moodTrend7d: moodTrend(mood),
    adherence30d: adherencePct(adherence),
    lastCall: { timestamp: b.created_at ?? new Date().toISOString(), duration: 0, agent: 'Adam' },
    coordinator: null,
  }
}

const ORDER_STATUS_MAP: Record<string, Order['status']> = {
  created: 'waiting_manual_confirm',
  confirmed: 'confirmed',
  cancelled: 'cancelled',
  in_progress: 'confirmed',
  completed: 'confirmed',
  disputed: 'cancelled',
}

export function mapOrder(b: BackendOrder): Order {
  return {
    orderId: String(b.id),
    seniorId: String(b.senior_id),
    categoryId: String(b.service_id),
    status: ORDER_STATUS_MAP[b.status] ?? 'waiting_manual_confirm',
    requestSource: 'caregiver-panel',
    cancellationWindowEndsAt: b.cancellable_until ?? undefined,
    estimatedPrice: `${b.amount_pln.toFixed(2)} zł`,
    createdAt: new Date().toISOString(),
  }
}

/* ---------- fabryka klienta (fetch wstrzykiwany dla testów) ---------- */

type Fetcher = (path: string, init?: RequestInit) => Promise<any>

export function createRealApi(fetcher: Fetcher) {
  /* ---------- Auth (ETAP 21 — realne /api/auth) ---------- */

  async function login(payload: LoginPayload): Promise<LoginResult> {
    const tok: BackendTokenOut = await fetcher('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: payload.email, password: payload.password }),
    })
    const role = mapRole(tok.role)
    // Backend nie zwraca name w TokenOut → używamy email jako etykiety
    // (pełny profil dostępny przez /api/auth/me po zalogowaniu).
    const email = payload.email.toLowerCase()
    const user: User = {
      id: email,
      email,
      name: email.split('@')[0],
      role,
    }
    return { accessToken: tok.access_token, refreshToken: tok.refresh_token, user }
  }

  async function refresh(refreshToken: string): Promise<{ accessToken: string; refreshToken: string }> {
    const tok: BackendTokenOut = await fetcher('/api/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    return { accessToken: tok.access_token, refreshToken: tok.refresh_token }
  }

  async function me(): Promise<User> {
    const m: BackendMe = await fetcher('/api/auth/me')
    return {
      id: m.email,
      email: m.email,
      name: m.email.split('@')[0],
      role: mapRole(m.role),
    }
  }

  async function getMySeniors(): Promise<{ seniors: Senior[]; total: number }> {
    const list: BackendSeniorList = await fetcher('/api/seniors?limit=200')
    const seniors = list.items.map((b) => mapSenior(b))
    return { seniors, total: list.total }
  }

  async function getSenior(id: string): Promise<SeniorDetail> {
    const b: BackendSenior = await fetcher(`/api/seniors/by-external/${encodeURIComponent(id)}`)
    let adherence: BackendAdherence | null = null
    try {
      adherence = await fetcher(`/api/seniors/${b.id}/medications/adherence?days=30`)
    } catch {
      adherence = null
    }
    const base = mapSenior(b, adherence)
    return { ...base, calls: [], meds: [], alerts: [], reports: [] }
  }

  async function getMood(
    id: string,
    _range: '7d' | '14d' | '30d' | '90d' = '30d',
  ): Promise<{ data: MoodPoint[]; markers: AlertMarker[] }> {
    // Backend nie utrzymuje serii nastroju — budujemy z trendu bazowego.
    const b: BackendSenior = await fetcher(`/api/seniors/by-external/${encodeURIComponent(id)}`)
    const base = moodFromSemaphore(b.semaphore)
    const now = Date.now()
    const data: MoodPoint[] = moodTrend(base).map((value, i) => ({
      timestamp: new Date(now - (6 - i) * 86400000).toISOString(),
      value,
    }))
    return { data, markers: [] }
  }

  async function listOrders(): Promise<Order[]> {
    // Backend grupuje zamówienia per-senior; agregujemy po liście seniorów.
    const list: BackendSeniorList = await fetcher('/api/seniors?limit=200')
    const all: Order[] = []
    for (const s of list.items) {
      try {
        const orders: BackendOrder[] = await fetcher(`/api/marketplace/seniors/${s.id}/orders`)
        all.push(...orders.map(mapOrder))
      } catch {
        /* pomiń seniora bez zamówień */
      }
    }
    return all
  }

  async function cancelOrder(id: string): Promise<{ ok: boolean }> {
    await fetcher(`/api/marketplace/orders/${id}/cancel`, { method: 'POST' })
    return { ok: true }
  }

  /* ---------- Messages / Account (ETAP 22 — /api/account) ---------- */

  async function listThreads(): Promise<Thread[]> {
    const threads: BackendThread[] = await fetcher('/api/account/threads')
    return threads.map(mapThread)
  }

  async function sendMessage(threadId: string, body: string): Promise<Thread> {
    // threadId = external_id seniora (backend grupuje wątki per senior)
    const thread: BackendThread = await fetcher(
      `/api/account/threads/${encodeURIComponent(threadId)}/messages`,
      { method: 'POST', body: JSON.stringify({ body }) },
    )
    return mapThread(thread)
  }

  async function listInvoices(): Promise<Invoice[]> {
    const invoices: BackendInvoice[] = await fetcher('/api/account/invoices')
    return invoices.map(mapInvoice)
  }

  async function listSessions(): Promise<Session[]> {
    const sessions: BackendSession[] = await fetcher('/api/account/sessions')
    return sessions.map(mapSession)
  }

  return {
    login, refresh, me,
    getMySeniors, getSenior, getMood, listOrders, cancelOrder,
    listThreads, sendMessage, listInvoices, listSessions,
  }
}

export type RealApi = ReturnType<typeof createRealApi>
