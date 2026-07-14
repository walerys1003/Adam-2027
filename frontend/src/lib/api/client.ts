/* ============================================================
   ADAM · API client facade
   Currently routes to the in-memory mock. When a real backend
   is available set VITE_API_URL and flip USE_MOCK to false;
   the real fetch implementations plug in here with identical
   signatures.
   ============================================================ */

import * as mock from './mockApi'
import type { LoginPayload } from './mockApi'

const USE_MOCK = !import.meta.env.VITE_API_URL

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

async function realFetch(path: string, init?: RequestInit) {
  const base = import.meta.env.VITE_API_URL
  const token = tokenStore.get()
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  })
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`)
  return res.json()
}

export const api = {
  // Auth
  login: (payload: LoginPayload) =>
    USE_MOCK ? mock.login(payload) : realFetch('/api/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  decodeToken: mock.decodeToken,

  // Seniors
  getMySeniors: () => (USE_MOCK ? mock.getMySeniors() : realFetch('/api/seniors/mine')),
  getSenior: (id: string) => (USE_MOCK ? mock.getSenior(id) : realFetch(`/api/seniors/${id}`)),
  getMood: (id: string, range: '7d' | '14d' | '30d' | '90d' = '30d') =>
    USE_MOCK ? mock.getMood(id, range) : realFetch(`/api/seniors/${id}/mood?range=${range}`),

  // Orders
  createOrder: (input: { seniorId: string; categoryId: string; requestSource: 'adam-call' | 'caregiver-panel' }) =>
    USE_MOCK ? mock.createOrder(input) : realFetch('/api/orders', { method: 'POST', body: JSON.stringify(input) }),
  cancelOrder: (id: string) =>
    USE_MOCK ? mock.cancelOrder(id) : realFetch(`/api/orders/${id}`, { method: 'DELETE' }),
  listOrders: () => (USE_MOCK ? mock.listOrders() : realFetch('/api/orders')),

  // Messages
  listThreads: () => (USE_MOCK ? mock.listThreads() : realFetch('/api/threads')),
  sendMessage: (threadId: string, body: string) =>
    USE_MOCK
      ? mock.sendMessage(threadId, body)
      : realFetch(`/api/threads/${threadId}/messages`, { method: 'POST', body: JSON.stringify({ body }) }),

  // Account
  listInvoices: () => (USE_MOCK ? mock.listInvoices() : realFetch('/api/billing/invoices')),
  listSessions: () => (USE_MOCK ? mock.listSessions() : realFetch('/api/account/sessions')),
}

export type { LoginPayload }
