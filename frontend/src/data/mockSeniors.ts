import type { Senior, SeniorDetail, WearableInfo } from '@/types/domain'

function trend(base: number): number[] {
  return Array.from({ length: 7 }, (_, i) =>
    Math.max(0, Math.min(1, base + (Math.sin(i) * 0.08) - i * 0.01)),
  ).map((v) => Number(v.toFixed(2)))
}

const xiaomiBand: WearableInfo = {
  brand: 'xiaomi',
  model: 'Band 8',
  pairedAt: '2026-05-02T10:00:00Z',
  batteryPct: 68,
  syncStatus: 'ok',
  lastSyncAt: '2026-07-14T07:40:00Z',
  vitals: {
    heartRate: 72,
    spo2: 97,
    stepsToday: 2140,
    sleepLastNight: { totalMinutes: 402, deepMinutes: 78, remMinutes: 92, awakenings: 3, score: 74 },
  },
  thresholds: { hrLow: 50, hrHigh: 110, spo2Low: 92, mode: 'auto' },
  calibration: { status: 'stable', daysSinceStable: 40 },
}

const appleWatch: WearableInfo = {
  brand: 'apple',
  model: 'Watch SE',
  pairedAt: '2026-06-20T09:00:00Z',
  batteryPct: 41,
  syncStatus: 'delayed',
  lastSyncAt: '2026-07-14T05:10:00Z',
  vitals: {
    heartRate: 88,
    spo2: 95,
    stepsToday: 890,
    sleepLastNight: { totalMinutes: 331, deepMinutes: 45, remMinutes: 60, awakenings: 6, score: 58 },
  },
  thresholds: {
    hrLow: 48,
    hrHigh: 105,
    spo2Low: 93,
    mode: 'manual_override',
    overriddenBy: {
      userId: 'C-01',
      userName: 'dr Maria Lewandowska',
      role: 'doctor',
      reason: 'Migotanie przedsionków w wywiadzie',
      overriddenAt: '2026-06-25T12:00:00Z',
    },
  },
  calibration: { status: 'calibrating', day: 9, totalDays: 14 },
}

export const MOCK_SENIORS: Senior[] = [
  {
    id: 'HW-01247',
    firstName: 'Halina',
    lastName: 'Wiśniewska',
    age: 78,
    district: 'Wilda',
    address: 'ul. Kwiatowa 12/4',
    package: 'premium',
    semaphore: 'green',
    semaphoreReason: 'Poranny welfare-check OK',
    mood: 0.72,
    moodTrend7d: trend(0.7),
    adherence30d: 94,
    heartRate: 72,
    spo2: 97,
    wearable: xiaomiBand,
    lastCall: { timestamp: '2026-07-14T07:35:00Z', duration: 214, agent: 'welfare-morning v7.4.2' },
    coordinator: { id: 'C-02', name: 'Anna Kowalczyk' },
    pulseAvatar: false,
  },
  {
    id: 'MN-02341',
    firstName: 'Marek',
    lastName: 'Nowak',
    age: 81,
    district: 'Grunwald',
    address: 'ul. Grunwaldzka 88',
    package: 'family',
    semaphore: 'red',
    semaphoreReason: 'Wykryto upadek · Apple Watch SE',
    mood: 0.34,
    moodTrend7d: trend(0.4),
    adherence30d: 61,
    heartRate: 118,
    spo2: 94,
    wearable: appleWatch,
    lastCall: { timestamp: '2026-07-14T06:22:00Z', duration: 0, agent: 'welfare-morning v7.4.2' },
    coordinator: { id: 'C-02', name: 'Anna Kowalczyk' },
    pulseAvatar: true,
  },
  {
    id: 'ZK-00812',
    firstName: 'Zofia',
    lastName: 'Kaczmarek',
    age: 74,
    district: 'Jeżyce',
    package: 'basic',
    semaphore: 'yellow',
    semaphoreReason: 'Nastrój poniżej 0.5 · samotność',
    mood: 0.46,
    moodTrend7d: trend(0.5),
    adherence30d: 82,
    heartRate: 76,
    lastCall: { timestamp: '2026-07-13T18:05:00Z', duration: 341, agent: 'welfare-evening v7.4.2' },
    coordinator: null,
    pulseAvatar: false,
  },
  {
    id: 'TB-03190',
    firstName: 'Tadeusz',
    lastName: 'Baran',
    age: 86,
    district: 'Stare Miasto',
    package: 'premium',
    semaphore: 'purple',
    semaphoreReason: 'AFib z objawami · dzwonię 112',
    mood: 0.28,
    moodTrend7d: trend(0.35),
    adherence30d: 55,
    heartRate: 142,
    spo2: 89,
    lastCall: { timestamp: '2026-07-14T08:01:00Z', duration: 12, agent: 'crisis-detect v7.4.2' },
    coordinator: { id: 'C-03', name: 'Piotr Zieliński' },
    pulseAvatar: true,
  },
  {
    id: 'IW-04455',
    firstName: 'Irena',
    lastName: 'Wójcik',
    age: 79,
    district: 'Winogrady',
    package: 'family',
    semaphore: 'green',
    semaphoreReason: 'Leki przyjęte · nastrój stabilny',
    mood: 0.68,
    moodTrend7d: trend(0.66),
    adherence30d: 98,
    heartRate: 70,
    lastCall: { timestamp: '2026-07-14T07:50:00Z', duration: 189, agent: 'welfare-morning v7.4.2' },
    coordinator: { id: 'C-02', name: 'Anna Kowalczyk' },
    pulseAvatar: false,
  },
]

export const MOCK_SENIOR_DETAIL: SeniorDetail = {
  ...MOCK_SENIORS[0],
  calls: [
    { id: 'CL-1', timestamp: '2026-07-14T07:35:00Z', duration: 214, agent: 'welfare-morning v7.4.2', summary: 'Dobre samopoczucie, przyjęła leki, planuje spacer.', semaphoreOutcome: 'green' },
    { id: 'CL-2', timestamp: '2026-07-13T07:33:00Z', duration: 198, agent: 'welfare-morning v7.4.2', summary: 'Lekkie zmęczenie, sen 6h.', semaphoreOutcome: 'green' },
    { id: 'CL-3', timestamp: '2026-07-12T18:10:00Z', duration: 256, agent: 'welfare-evening v7.4.2', summary: 'Rozmowa o wnukach, nastrój dobry.', semaphoreOutcome: 'green' },
  ],
  meds: [
    { id: 'M-1', name: 'Metformina 500 mg', scheduleTimes: ['07:15', '19:15'], frequency: '2×/dzień', notes: 'Z posiłkiem', adherence30d: 96, medGuardId: 'MG-1001' },
    { id: 'M-2', name: 'Ramipril 5 mg', scheduleTimes: ['08:00'], frequency: '1×/dzień', adherence30d: 92 },
    { id: 'M-3', name: 'Atorwastatyna 20 mg', scheduleTimes: ['21:00'], frequency: '1×/dzień', notes: 'Wieczorem', adherence30d: 88 },
  ],
  alerts: [
    { id: 'A-1', seniorId: 'HW-01247', level: 'yellow', reason: 'Sen poniżej 6h (3 dni)', timestamp: '2026-07-10T08:00:00Z', resolvedAt: '2026-07-11T08:00:00Z' },
  ],
  reports: [
    { id: 'R-1', seniorId: 'HW-01247', period: 'Czerwiec 2026', generatedAt: '2026-07-01T00:00:00Z', moodAvg: 0.7, adherenceAvg: 93, callsCount: 58, alertsCount: 2 },
  ],
}

export const MOCK_MOOD_30D = Array.from({ length: 30 }, (_, i) => {
  const d = new Date('2026-06-15T00:00:00Z')
  d.setDate(d.getDate() + i)
  const base = 0.6 + Math.sin(i / 4) * 0.15 - (i > 20 ? 0.1 : 0)
  return { timestamp: d.toISOString(), value: Number(Math.max(0.2, Math.min(0.95, base)).toFixed(2)) }
})

export const MOCK_MOOD_MARKERS = [
  { timestamp: MOCK_MOOD_30D[6].timestamp, level: 'yellow' as const, reason: 'Samotność w rozmowie' },
  { timestamp: MOCK_MOOD_30D[22].timestamp, level: 'red' as const, reason: 'Pominięte leki 2×' },
]
