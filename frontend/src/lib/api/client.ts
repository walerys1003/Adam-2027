/* ============================================================
   ADAM · API client facade
   Currently routes to the in-memory mock. When a real backend
   is available set VITE_API_URL and flip USE_MOCK to false;
   the real fetch implementations plug in here with identical
   signatures.
   ============================================================ */

import * as mock from './mockApi'
import type { LoginPayload } from './mockApi'
import { createRealApi } from './realApi'

/* ------------------------------------------------------------------
   Tryb API (WP-1): jawny przełącznik VITE_API_MODE.
     - 'mock' → zawsze mock (nawet gdy VITE_API_URL ustawione)
     - 'real' → zawsze realny backend (wymaga VITE_API_URL)
     - (brak) → auto: real gdy VITE_API_URL ustawione, w innym wypadku mock
   Zachowuje kompatybilność wsteczną z dotychczasowym VITE_API_URL.
   ------------------------------------------------------------------ */
const API_MODE = (import.meta.env.VITE_API_MODE as 'mock' | 'real' | undefined) ?? undefined

function resolveUseMock(): boolean {
  if (API_MODE === 'mock') return true
  if (API_MODE === 'real') return false
  return !import.meta.env.VITE_API_URL
}

const USE_MOCK = resolveUseMock()

/** Eksport dla UI/diagnostyki — pozwala ekranom pokazać baner trybu. */
export const apiMode: 'mock' | 'real' = USE_MOCK ? 'mock' : 'real'
export const isMockMode = USE_MOCK

// Token storage keys
const ACCESS_KEY = 'adam.accessToken'
const REFRESH_KEY = 'adam.refreshToken'

export const tokenStore = {
  get: () => localStorage.getItem(ACCESS_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  set: (access: string, refresh: string) => {
    localStorage.setItem(ACCESS_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear: () => {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

export async function realFetch(path: string, init?: RequestInit) {
  const base = import.meta.env.VITE_API_URL
  const token = tokenStore.get()
  const apiKey = import.meta.env.VITE_API_KEY
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(apiKey ? { 'X-API-Key': apiKey } : {}),
      ...init?.headers,
    },
  })
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`)
  // 204 No Content → brak ciała
  if (res.status === 204) return null
  return res.json()
}

// Adapter backendu ETAP 9 (mapuje kontrakt FastAPI → typy domenowe).
const real = createRealApi(realFetch)

export const api = {
  // Auth — ETAP 21: realne /api/auth/login|refresh|me gdy VITE_API_URL ustawione.
  login: (payload: LoginPayload) => (USE_MOCK ? mock.login(payload) : real.login(payload)),
  refresh: (refreshToken: string) =>
    USE_MOCK
      ? Promise.resolve({ accessToken: 'refresh-demo', refreshToken: 'refresh-demo' })
      : real.refresh(refreshToken),
  me: () => (USE_MOCK ? Promise.resolve(null) : real.me()),
  decodeToken: mock.decodeToken,

  // Seniors — obsłużone przez adapter realApi (F1 + adherence F6).
  getMySeniors: () => (USE_MOCK ? mock.getMySeniors() : real.getMySeniors()),
  getSenior: (id: string) => (USE_MOCK ? mock.getSenior(id) : real.getSenior(id)),
  getMood: (id: string, range: '7d' | '14d' | '30d' | '90d' = '30d') =>
    USE_MOCK ? mock.getMood(id, range) : real.getMood(id),

  // Orders — F11 marketplace.
  createOrder: (input: { seniorId: string; categoryId: string; requestSource: 'adam-call' | 'caregiver-panel' }) =>
    USE_MOCK
      ? mock.createOrder(input)
      : realFetch('/api/marketplace/orders', {
          method: 'POST',
          body: JSON.stringify({ senior_id: Number(input.seniorId), service_id: Number(input.categoryId) }),
        }),
  cancelOrder: (id: string) => (USE_MOCK ? mock.cancelOrder(id) : real.cancelOrder(id)),
  listOrders: () => (USE_MOCK ? mock.listOrders() : real.listOrders()),

  // Messages / Account — ETAP 22: realne /api/account gdy VITE_API_URL ustawione.
  listThreads: () => (USE_MOCK ? mock.listThreads() : real.listThreads()),
  sendMessage: (threadId: string, body: string) =>
    USE_MOCK ? mock.sendMessage(threadId, body) : real.sendMessage(threadId, body),
  listInvoices: () => (USE_MOCK ? mock.listInvoices() : real.listInvoices()),
  listSessions: () => (USE_MOCK ? mock.listSessions() : real.listSessions()),
}

export type { LoginPayload }
