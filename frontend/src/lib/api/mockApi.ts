/* ============================================================
   ADAM · Mock API
   Client-side in-memory implementation of DEVELOPER-HANDOFF API
   contracts. Zero backend required — works with static hosting.
   Swap to real fetch() against VITE_API_URL when backend is live.
   ============================================================ */

import type {
  Senior,
  SeniorDetail,
  MoodPoint,
  AlertMarker,
  Order,
  User,
  Role,
} from '@/types/domain'
import {
  MOCK_SENIORS,
  MOCK_SENIOR_DETAIL,
  MOCK_MOOD_30D,
  MOCK_MOOD_MARKERS,
} from '@/data/mockSeniors'

const LATENCY = 260 // ms — simulate network

function delay<T>(value: T, ms = LATENCY): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms))
}

/* ---------- Auth ---------- */

export interface LoginPayload {
  email: string
  password: string
  otpCode?: string
}

export interface LoginResult {
  accessToken: string
  refreshToken: string
  user: User
}

// Demo accounts — one per role
const DEMO_USERS: Record<string, User> = {
  'admin@silvertech.pl': { id: 'U-ADM', email: 'admin@silvertech.pl', name: 'Ewa Administrator', role: 'admin' },
  'anna@silvertech.pl': { id: 'U-CG1', email: 'anna@silvertech.pl', name: 'Anna Kowalczyk', role: 'caregiver' },
  'rodzina@gmail.com': { id: 'U-FM1', email: 'rodzina@gmail.com', name: 'Magdalena C.', role: 'family_member' },
}

export async function login(payload: LoginPayload): Promise<LoginResult> {
  const user = DEMO_USERS[payload.email.toLowerCase()]
  if (!user) {
    // Any unknown email logs in as caregiver (demo convenience)
    const fallback: User = {
      id: 'U-DEMO',
      email: payload.email,
      name: 'Użytkownik Demo',
      role: 'caregiver',
    }
    return delay({ accessToken: mkToken(fallback), refreshToken: 'refresh-demo', user: fallback })
  }
  return delay({ accessToken: mkToken(user), refreshToken: 'refresh-' + user.id, user })
}

function mkToken(user: User): string {
  // Fake JWT-ish token (base64 of the user) — NOT secure, demo only.
  return 'mock.' + btoa(JSON.stringify({ sub: user.id, role: user.role, email: user.email }))
}

export function decodeToken(token: string): User | null {
  try {
    const [, payload] = token.split('.')
    const data = JSON.parse(atob(payload))
    return {
      id: data.sub,
      email: data.email,
      name: DEMO_USERS[data.email]?.name ?? 'Użytkownik',
      role: data.role as Role,
    }
  } catch {
    return null
  }
}

/* ---------- Seniors ---------- */

export async function getMySeniors(): Promise<{ seniors: Senior[]; total: number }> {
  return delay({ seniors: MOCK_SENIORS, total: MOCK_SENIORS.length })
}

export async function getSenior(id: string): Promise<SeniorDetail> {
  const base = MOCK_SENIORS.find((s) => s.id === id) ?? MOCK_SENIORS[0]
  return delay({ ...MOCK_SENIOR_DETAIL, ...base })
}

export async function getMood(
  _id: string,
  _range: '7d' | '14d' | '30d' | '90d' = '30d',
): Promise<{ data: MoodPoint[]; markers: AlertMarker[] }> {
  return delay({ data: MOCK_MOOD_30D, markers: MOCK_MOOD_MARKERS })
}

/* ---------- Orders (Marketplace) ---------- */

const orders: Order[] = []

export async function createOrder(input: {
  seniorId: string
  categoryId: string
  requestSource: 'adam-call' | 'caregiver-panel'
}): Promise<Order> {
  const order: Order = {
    orderId: 'O-' + Math.floor(1000 + Math.random() * 9000),
    seniorId: input.seniorId,
    categoryId: input.categoryId,
    status: 'auto_confirmed',
    requestSource: input.requestSource,
    cancellationWindowEndsAt: new Date(Date.now() + 30 * 60 * 1000).toISOString(),
    partner: { name: 'DOZ · Apteka św. Marcin', nip: '7831234567', rating: 4.8 },
    estimatedPrice: '34 zł',
    estimatedDelivery: '45 min',
    createdAt: new Date().toISOString(),
  }
  orders.push(order)
  return delay(order)
}

export async function cancelOrder(id: string): Promise<{ ok: boolean }> {
  const order = orders.find((o) => o.orderId === id)
  if (!order) return delay({ ok: false })
  const withinWindow = order.cancellationWindowEndsAt
    ? new Date(order.cancellationWindowEndsAt).getTime() > Date.now()
    : false
  if (withinWindow) {
    order.status = 'cancelled'
    return delay({ ok: true })
  }
  return delay({ ok: false })
}

export async function listOrders(): Promise<Order[]> {
  return delay([...orders])
}
