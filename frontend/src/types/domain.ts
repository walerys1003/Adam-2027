/* ============================================================
   ADAM · Domain types
   Źródło: design-system/DEVELOPER-HANDOFF.md (kontrakty komponentów + API)
   ============================================================ */

export type SemaphoreLevel = 'green' | 'yellow' | 'red' | 'purple'

export type Package = 'basic' | 'family' | 'premium'

export type District =
  | 'Wilda'
  | 'Grunwald'
  | 'Jeżyce'
  | 'Stare Miasto'
  | 'Winogrady'
  | 'Nowe Miasto'

export type WearableBrand = 'xiaomi' | 'apple' | 'garmin' | 'fitbit'

export type Role = 'admin' | 'caregiver' | 'family_member'

/* ---------- Sleep / Wearable ---------- */

export interface SleepData {
  totalMinutes: number
  deepMinutes: number
  remMinutes: number
  awakenings: number
  score: number // 0–100
}

export interface WearableInfo {
  brand: WearableBrand
  model: string
  pairedAt: string
  batteryPct: number
  syncStatus: 'ok' | 'delayed' | 'offline'
  lastSyncAt: string
  vitals: {
    heartRate: number
    spo2: number
    stepsToday: number
    sleepLastNight: SleepData
  }
  thresholds: {
    hrLow: number
    hrHigh: number
    spo2Low: number
    mode: 'auto' | 'manual_override'
    overriddenBy?: {
      userId: string
      userName: string
      role: 'coordinator' | 'doctor'
      reason: string
      overriddenAt: string
    }
  }
  calibration: {
    status: 'calibrating' | 'stable'
    day?: number
    totalDays?: number
    daysSinceStable?: number
  }
}

/* ---------- Senior ---------- */

export interface Senior {
  id: string // np. "HW-01247"
  firstName: string
  lastName: string
  age: number
  district: District
  address?: string
  package: Package
  semaphore: SemaphoreLevel
  semaphoreReason?: string
  mood: number // 0.0 – 1.0
  moodTrend7d: number[]
  adherence30d: number // 0 – 100
  heartRate?: number
  spo2?: number
  wearable?: WearableInfo
  lastCall: {
    timestamp: string
    duration: number
    agent: string
  }
  coordinator?: { id: string; name: string } | null
  pulseAvatar?: boolean
}

/* ---------- Mood ---------- */

export interface MoodPoint {
  timestamp: string
  value: number // 0.0 – 1.0
}

export interface AlertMarker {
  timestamp: string
  level: SemaphoreLevel
  reason: string
}

/* ---------- Medication ---------- */

export interface Medication {
  id: string
  name: string
  scheduleTimes: string[]
  frequency: string
  notes?: string
  adherence30d: number
  medGuardId?: string
}

/* ---------- Calls / Alerts / Reports ---------- */

export interface CallLog {
  id: string
  timestamp: string
  duration: number
  agent: string
  summary?: string
  transcriptUrl?: string
  semaphoreOutcome: SemaphoreLevel
}

export interface Alert {
  id: string
  seniorId: string
  level: SemaphoreLevel
  reason: string
  timestamp: string
  acknowledgedAt?: string
  acknowledgedBy?: string
  resolvedAt?: string
}

export interface ReportSummary {
  id: string
  seniorId: string
  period: string
  generatedAt: string
  moodAvg: number
  adherenceAvg: number
  callsCount: number
  alertsCount: number
  pdfUrl?: string
  fhirUrl?: string
}

export interface SeniorDetail extends Senior {
  calls: CallLog[]
  meds: Medication[]
  alerts: Alert[]
  reports: ReportSummary[]
}

/* ---------- Marketplace ---------- */

export interface Order {
  orderId: string
  seniorId: string
  categoryId: string
  status: 'auto_confirmed' | 'waiting_manual_confirm' | 'confirmed' | 'cancelled'
  requestSource: 'adam-call' | 'caregiver-panel'
  cancellationWindowEndsAt?: string
  partner?: { name: string; nip: string; rating: number }
  estimatedPrice?: string
  estimatedDelivery?: string
  createdAt: string
}

export interface OrderCategory {
  id: string
  label: string
  icon: string // lucide icon name
  examples: string
}

/* ---------- Messages ---------- */

export interface Message {
  id: string
  from: 'adam' | 'coordinator' | 'system' | 'me'
  authorName: string
  body: string
  timestamp: string
  read: boolean
}

export interface Thread {
  id: string
  subject: string
  seniorId?: string
  seniorName?: string
  category: 'alert' | 'report' | 'coordinator' | 'system'
  lastMessageAt: string
  unread: number
  messages: Message[]
}

/* ---------- Account ---------- */

export interface Invoice {
  id: string
  period: string
  amount: string
  status: 'paid' | 'pending' | 'overdue'
  pdfUrl?: string
}

export interface Session {
  id: string
  device: string
  location: string
  lastActive: string
  current: boolean
}

/* ---------- Auth ---------- */

export interface User {
  id: string
  email: string
  name: string
  role: Role
  avatarUrl?: string
}
