/* Testy adaptera realApi (ETAP 10) — mapowanie kontraktu backendu → typy domenowe. */
import { describe, it, expect } from 'vitest'
import {
  mapDistrict,
  moodFromSemaphore,
  adherencePct,
  moodTrend,
  mapSenior,
  mapOrder,
  mapRole,
  createRealApi,
  type BackendSenior,
  type BackendSeniorList,
  type BackendAdherence,
  type BackendOrder,
} from './realApi'

const BSENIOR: BackendSenior = {
  id: 1,
  external_id: 'SR-ABC123',
  first_name: 'Jan',
  last_name: 'Kowalski',
  birth_date: '1945-03-01',
  address: 'ul. Sołacka 5',
  district: 'Jeżyce',
  package: 'family',
  semaphore: 'green',
  active: true,
  age: 80,
  created_at: '2027-01-01T10:00:00',
}

describe('mapDistrict', () => {
  it('zwraca znaną dzielnicę', () => {
    expect(mapDistrict('Jeżyce')).toBe('Jeżyce')
  })
  it('fallback dla nieznanej/null', () => {
    expect(mapDistrict('NieistniejącaDzielnica')).toBe('Stare Miasto')
    expect(mapDistrict(null)).toBe('Stare Miasto')
  })
})

describe('moodFromSemaphore', () => {
  it('malejący nastrój wraz z poziomem', () => {
    expect(moodFromSemaphore('green')).toBeGreaterThan(moodFromSemaphore('yellow'))
    expect(moodFromSemaphore('yellow')).toBeGreaterThan(moodFromSemaphore('red'))
    expect(moodFromSemaphore('red')).toBeGreaterThan(moodFromSemaphore('purple'))
  })
})

describe('adherencePct', () => {
  it('liczy taken/total', () => {
    const a: BackendAdherence = { senior_id: 1, total_doses: 20, taken: 18, missed: 1, late: 1, skipped: 0 }
    expect(adherencePct(a)).toBe(90)
  })
  it('0 przy braku dawek / null', () => {
    expect(adherencePct(null)).toBe(0)
    expect(adherencePct({ senior_id: 1, total_doses: 0, taken: 0, missed: 0, late: 0, skipped: 0 })).toBe(0)
  })
})

describe('moodTrend', () => {
  it('7 punktów w zakresie [0,1]', () => {
    const t = moodTrend(0.8)
    expect(t).toHaveLength(7)
    t.forEach((v) => {
      expect(v).toBeGreaterThanOrEqual(0)
      expect(v).toBeLessThanOrEqual(1)
    })
  })
  it('deterministyczny (te same wejścia → te same wyjścia)', () => {
    expect(moodTrend(0.5)).toEqual(moodTrend(0.5))
  })
})

describe('mapSenior', () => {
  it('mapuje external_id → id, imię/nazwisko, wiek, dzielnica', () => {
    const s = mapSenior(BSENIOR)
    expect(s.id).toBe('SR-ABC123')
    expect(s.firstName).toBe('Jan')
    expect(s.age).toBe(80)
    expect(s.district).toBe('Jeżyce')
    expect(s.semaphore).toBe('green')
    expect(s.moodTrend7d).toHaveLength(7)
    expect(s.adherence30d).toBe(0) // brak raportu
  })
  it('wstrzykuje adherence z raportu', () => {
    const a: BackendAdherence = { senior_id: 1, total_doses: 10, taken: 8, missed: 2, late: 0, skipped: 0 }
    expect(mapSenior(BSENIOR, a).adherence30d).toBe(80)
  })
})

describe('mapOrder', () => {
  it('mapuje status backendu → domenowy + cena', () => {
    const b: BackendOrder = {
      id: 42, service_id: 7, senior_id: 1, status: 'created',
      amount_pln: 25, can_cancel: true, cancellable_until: '2027-01-01T10:30:00',
    }
    const o = mapOrder(b)
    expect(o.orderId).toBe('42')
    expect(o.status).toBe('waiting_manual_confirm')
    expect(o.estimatedPrice).toBe('25.00 zł')
  })
  it('cancelled i completed', () => {
    expect(mapOrder({ id: 1, service_id: 1, senior_id: 1, status: 'cancelled', amount_pln: 0, can_cancel: false }).status).toBe('cancelled')
    expect(mapOrder({ id: 2, service_id: 1, senior_id: 1, status: 'completed', amount_pln: 0, can_cancel: false }).status).toBe('confirmed')
  })
})

describe('createRealApi', () => {
  it('getMySeniors mapuje listę', async () => {
    const list: BackendSeniorList = { items: [BSENIOR], total: 1, limit: 200, offset: 0 }
    const api = createRealApi(async (path) => {
      expect(path).toContain('/api/seniors')
      return list
    })
    const res = await api.getMySeniors()
    expect(res.total).toBe(1)
    expect(res.seniors[0].id).toBe('SR-ABC123')
  })

  it('getSenior pobiera po external_id i dokleja adherence', async () => {
    const calls: string[] = []
    const api = createRealApi(async (path) => {
      calls.push(path)
      if (path.includes('by-external')) return BSENIOR
      if (path.includes('adherence')) return { senior_id: 1, total_doses: 4, taken: 3, missed: 1, late: 0, skipped: 0 }
      return null
    })
    const detail = await api.getSenior('SR-ABC123')
    expect(detail.adherence30d).toBe(75)
    expect(detail.meds).toEqual([])
    expect(calls.some((c) => c.includes('by-external'))).toBe(true)
  })

  it('getSenior toleruje brak adherence (404)', async () => {
    const api = createRealApi(async (path) => {
      if (path.includes('by-external')) return BSENIOR
      throw new Error('API 404: adherence')
    })
    const detail = await api.getSenior('SR-ABC123')
    expect(detail.adherence30d).toBe(0)
  })

  it('listOrders agreguje zamówienia po seniorach', async () => {
    const list: BackendSeniorList = { items: [BSENIOR], total: 1, limit: 200, offset: 0 }
    const orders: BackendOrder[] = [
      { id: 1, service_id: 5, senior_id: 1, status: 'created', amount_pln: 30, can_cancel: true },
    ]
    const api = createRealApi(async (path) => {
      if (path.includes('marketplace/seniors')) return orders
      return list
    })
    const res = await api.listOrders()
    expect(res).toHaveLength(1)
    expect(res[0].orderId).toBe('1')
  })

  it('cancelOrder woła POST /cancel', async () => {
    let called = ''
    const api = createRealApi(async (path, init) => {
      called = `${init?.method} ${path}`
      return null
    })
    const res = await api.cancelOrder('99')
    expect(res.ok).toBe(true)
    expect(called).toBe('POST /api/marketplace/orders/99/cancel')
  })

  it('getMood zwraca { data, markers } (kontrakt jak mock)', async () => {
    const api = createRealApi(async () => BSENIOR)
    const mood = await api.getMood('SR-ABC123')
    expect(mood).toHaveProperty('data')
    expect(mood).toHaveProperty('markers')
    expect(mood.data).toHaveLength(7)
    expect(Array.isArray(mood.markers)).toBe(true)
    // każdy punkt: timestamp + value w zakresie 0..1
    for (const p of mood.data) {
      expect(typeof p.timestamp).toBe('string')
      expect(p.value).toBeGreaterThanOrEqual(0)
      expect(p.value).toBeLessThanOrEqual(1)
    }
  })
})

/* ---------- ETAP 21: auth (login/refresh/me + mapRole) ---------- */

describe('mapRole', () => {
  it('mapuje role backendu na frontend', () => {
    expect(mapRole('admin')).toBe('admin')
    expect(mapRole('coordinator')).toBe('caregiver')
    expect(mapRole('family')).toBe('family_member')
  })
  it('fallback dla nieznanej roli → caregiver', () => {
    expect(mapRole('nieznana')).toBe('caregiver')
  })
})

describe('createRealApi.login', () => {
  it('mapuje TokenOut → LoginResult (tokeny + user)', async () => {
    let sent: { path: string; body: any } | null = null
    const api = createRealApi(async (path, init) => {
      sent = { path, body: init?.body ? JSON.parse(init.body as string) : null }
      return {
        access_token: 'acc-1', refresh_token: 'ref-1', token_type: 'bearer',
        expires_in: 900, role: 'coordinator', senior_ids: ['SR-1'],
      }
    })
    const res = await api.login({ email: 'Anna@silvertech.pl', password: 'x' })
    expect(sent!.path).toBe('/api/auth/login')
    expect(sent!.body).toEqual({ email: 'Anna@silvertech.pl', password: 'x' })
    expect(res.accessToken).toBe('acc-1')
    expect(res.refreshToken).toBe('ref-1')
    expect(res.user.role).toBe('caregiver')
    expect(res.user.email).toBe('anna@silvertech.pl')
    expect(res.user.name).toBe('anna')
  })
})

describe('createRealApi.refresh', () => {
  it('wysyła refresh_token i zwraca nową parę', async () => {
    let sent: any = null
    const api = createRealApi(async (path, init) => {
      sent = { path, body: JSON.parse((init!.body as string)) }
      return {
        access_token: 'acc-2', refresh_token: 'ref-2', token_type: 'bearer',
        expires_in: 900, role: 'admin', senior_ids: [],
      }
    })
    const res = await api.refresh('old-refresh')
    expect(sent.path).toBe('/api/auth/refresh')
    expect(sent.body).toEqual({ refresh_token: 'old-refresh' })
    expect(res).toEqual({ accessToken: 'acc-2', refreshToken: 'ref-2' })
  })
})

describe('createRealApi.me', () => {
  it('mapuje MeOut → User', async () => {
    const api = createRealApi(async (path) => {
      expect(path).toBe('/api/auth/me')
      return { email: 'admin@silvertech.pl', role: 'admin', senior_ids: [] }
    })
    const user = await api.me()
    expect(user.email).toBe('admin@silvertech.pl')
    expect(user.role).toBe('admin')
    expect(user.name).toBe('admin')
  })
})

/* ---------- ETAP 22: Messages / Account ---------- */

import { mapThread, mapMessage, mapInvoice, mapSession } from './realApi'

describe('mapThread / mapMessage (ETAP 22)', () => {
  const bThread = {
    id: 'SR-1', subject: 'Alert — Jan', senior_id: 'SR-1', senior_name: 'Jan Kowalski',
    category: 'alert' as const, last_message_at: '2027-01-01T10:00:00', unread: 2,
    messages: [
      { id: 'm1', from: 'coordinator' as const, author_name: 'Anna', body: 'Dzwonię',
        timestamp: '2027-01-01T09:00:00', read: false },
    ],
  }
  it('mapuje snake_case → camelCase', () => {
    const t = mapThread(bThread)
    expect(t.seniorId).toBe('SR-1')
    expect(t.seniorName).toBe('Jan Kowalski')
    expect(t.lastMessageAt).toBe('2027-01-01T10:00:00')
    expect(t.unread).toBe(2)
    expect(t.messages[0].authorName).toBe('Anna')
    expect(t.messages[0].from).toBe('coordinator')
  })
  it('mapMessage zachowuje from i read', () => {
    const m = mapMessage(bThread.messages[0])
    expect(m.from).toBe('coordinator')
    expect(m.read).toBe(false)
  })
})

describe('mapInvoice / mapSession (ETAP 22)', () => {
  it('mapuje fakturę', () => {
    const i = mapInvoice({ id: 'FV/2027/01', period: 'Styczeń 2027', amount: '249 zł', status: 'pending' })
    expect(i.id).toBe('FV/2027/01')
    expect(i.status).toBe('pending')
  })
  it('mapuje sesję (last_active → lastActive)', () => {
    const s = mapSession({ id: 'current', device: 'Sesja API · admin', location: '—',
                           last_active: '2027-01-01T10:00:00', current: true })
    expect(s.lastActive).toBe('2027-01-01T10:00:00')
    expect(s.current).toBe(true)
  })
})

describe('createRealApi.listThreads / sendMessage / listInvoices / listSessions', () => {
  it('listThreads mapuje listę', async () => {
    const api = createRealApi(async (path) => {
      expect(path).toBe('/api/account/threads')
      return [{ id: 'SR-1', subject: 's', category: 'report', last_message_at: 'x',
                unread: 0, messages: [] }]
    })
    const t = await api.listThreads()
    expect(t).toHaveLength(1)
    expect(t[0].id).toBe('SR-1')
  })
  it('sendMessage POST-uje body i zwraca wątek', async () => {
    let sent: any = null
    const api = createRealApi(async (path, init) => {
      sent = { path, body: JSON.parse(init!.body as string), method: init!.method }
      return { id: 'SR-1', subject: 's', category: 'coordinator', last_message_at: 'x',
               unread: 0, messages: [{ id: 'm1', from: 'coordinator', author_name: 'A',
               body: 'hej', timestamp: 't', read: true }] }
    })
    const t = await api.sendMessage('SR-1', 'hej')
    expect(sent.path).toBe('/api/account/threads/SR-1/messages')
    expect(sent.method).toBe('POST')
    expect(sent.body).toEqual({ body: 'hej' })
    expect(t.messages[0].body).toBe('hej')
  })
  it('listInvoices / listSessions mapują', async () => {
    const inv = createRealApi(async () => [{ id: 'FV', period: 'p', amount: '1 zł', status: 'paid' }])
    expect((await inv.listInvoices())[0].id).toBe('FV')
    const ses = createRealApi(async () => [{ id: 'current', device: 'd', location: '—',
                                             last_active: 't', current: true }])
    expect((await ses.listSessions())[0].current).toBe(true)
  })
})
