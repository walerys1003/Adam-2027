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
} from '@/types/domain'

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

  return { getMySeniors, getSenior, getMood, listOrders, cancelOrder }
}

export type RealApi = ReturnType<typeof createRealApi>
