import {
  Phone,
  FileText,
  Download,
  ShieldCheck,
  UserPlus,
  Trash2,
  Clock,
  AlertTriangle,
} from 'lucide-react'
import type { SeniorDetail } from '@/types/domain'
import { MoodChart, MedicationList, WearableWidget } from '@/components/senior'
import {
  Card,
  CardBody,
  Badge,
  Heatmap,
  Timeline,
  Button,
  SemaphoreBadge,
} from '@/components/ui'
import type { HeatCell, TimelineItem } from '@/components/ui'
import { useAuth } from '@/lib/auth/AuthContext'

function fmt(iso: string) {
  return new Date(iso).toLocaleString('pl-PL', { dateStyle: 'medium', timeStyle: 'short' })
}
function fmtDur(sec: number) {
  if (!sec) return 'nieodebrane'
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

/* ---------- 1. Przegląd ---------- */
export function TabOverview({ senior, mood }: { senior: SeniorDetail; mood: { data: any[]; markers: any[] } }) {
  return (
    <div className="grid gap-5 lg:grid-cols-3">
      <MoodChart data={mood.data} markers={mood.markers} range="30d" className="lg:col-span-2" />
      <MedicationList medications={senior.meds} variant="summary" />
      {senior.wearable && <WearableWidget device={senior.wearable} showLive className="lg:col-span-2" />}
      <Card>
        <CardBody>
          <span className="eyebrow">Ostatnia rozmowa</span>
          <h3 className="text-h4 font-serif text-granat-900 mt-1">{fmtDur(senior.lastCall.duration)}</h3>
          <p className="text-label text-ink-500 mt-1">{fmt(senior.lastCall.timestamp)}</p>
          <p className="text-caption text-ink-400 mt-2">{senior.lastCall.agent}</p>
        </CardBody>
      </Card>
    </div>
  )
}

/* ---------- 2. Rozmowy ---------- */
export function TabCalls({ senior }: { senior: SeniorDetail }) {
  return (
    <div className="adam-card divide-y divide-line">
      {senior.calls.map((c) => (
        <div key={c.id} className="px-5 py-4 flex items-start gap-4">
          <div className="mt-0.5 w-9 h-9 rounded-md bg-granat-50 text-granat-700 flex items-center justify-center shrink-0">
            <Phone size={17} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <h4 className="text-body font-medium text-granat-900">{fmt(c.timestamp)}</h4>
              <SemaphoreBadge level={c.semaphoreOutcome} size="xs" showLabel={false} />
            </div>
            <p className="text-label text-ink-500 mt-0.5">
              {fmtDur(c.duration)} · {c.agent}
            </p>
            {c.summary && <p className="text-body text-ink-600 mt-1.5">{c.summary}</p>}
          </div>
        </div>
      ))}
    </div>
  )
}

/* ---------- 3. Leki ---------- */
export function TabMeds({ senior }: { senior: SeniorDetail }) {
  // 30-day adherence heatmap (deterministic pseudo from adherence)
  const cells: HeatCell[] = Array.from({ length: 30 }, (_, i) => {
    const seed = (senior.adherence30d + i * 7) % 100
    const status = seed > 88 ? 'ok' : seed > 55 ? 'partial' : seed > 40 ? 'missed' : 'ok'
    const d = new Date()
    d.setDate(d.getDate() - (29 - i))
    return { date: d.toLocaleDateString('pl-PL'), value: seed / 100, status }
  })
  return (
    <div className="grid gap-5 lg:grid-cols-3">
      <MedicationList medications={senior.meds} variant="schedule" className="lg:col-span-2" />
      <Card>
        <CardBody>
          <span className="eyebrow">Adherencja · 30 dni</span>
          <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-4">Kalendarz przyjmowania</h3>
          <Heatmap cells={cells} columns={7} />
        </CardBody>
      </Card>
    </div>
  )
}

/* ---------- 4. Wearable ---------- */
export function TabWearable({ senior }: { senior: SeniorDetail }) {
  if (!senior.wearable) {
    return <p className="text-body text-ink-400 py-8 text-center">Brak sparowanego urządzenia.</p>
  }
  return <WearableWidget device={senior.wearable} showLive readOnlyThresholds />
}

/* ---------- 5. Alerty ---------- */
export function TabAlerts({ senior }: { senior: SeniorDetail }) {
  const items: TimelineItem[] = senior.alerts.map((a) => ({
    id: a.id,
    title: a.reason,
    time: fmt(a.timestamp),
    level: a.level,
    description: a.resolvedAt
      ? `Rozwiązano ${fmt(a.resolvedAt)}`
      : a.acknowledgedAt
        ? `Potwierdzono ${fmt(a.acknowledgedAt)}`
        : 'Oczekuje na reakcję',
    icon: <AlertTriangle size={15} className="text-zloto-600" />,
  }))
  return (
    <Card>
      <CardBody>
        <span className="eyebrow">Historia alertów</span>
        <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-4">Oś czasu semafora</h3>
        <Timeline items={items} />
      </CardBody>
    </Card>
  )
}

/* ---------- 6. Raporty ---------- */
export function TabReports({ senior }: { senior: SeniorDetail }) {
  return (
    <div className="adam-card divide-y divide-line">
      {senior.reports.map((r) => (
        <div key={r.id} className="px-5 py-4 flex items-center gap-4">
          <div className="w-9 h-9 rounded-md bg-granat-50 text-granat-700 flex items-center justify-center shrink-0">
            <FileText size={17} />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-body font-medium text-granat-900">{r.period}</h4>
            <p className="text-label text-ink-500">
              Nastrój {Math.round(r.moodAvg * 100)}% · Leki {r.adherenceAvg}% · {r.callsCount} rozmów · {r.alertsCount} alertów
            </p>
          </div>
          <Button size="sm" variant="secondary">
            <Download size={14} /> PDF
          </Button>
        </div>
      ))}
    </div>
  )
}

/* ---------- 7. Rodzina (RBAC) ---------- */
export function TabFamily({ senior }: { senior: SeniorDetail }) {
  const { can } = useAuth()
  const members = [
    { name: 'Magdalena C.', relation: 'Córka', role: 'family_member', access: 'Pełny' },
    { name: 'Krzysztof W.', relation: 'Syn', role: 'family_member', access: 'Tylko odczyt' },
  ]
  return (
    <Card>
      <CardBody>
        <div className="flex items-center justify-between mb-4">
          <div>
            <span className="eyebrow">Rodzina i dostęp</span>
            <h3 className="text-h4 font-serif text-granat-900 mt-1">Osoby z dostępem</h3>
          </div>
          {can('family:invite') && (
            <Button size="sm" variant="gold">
              <UserPlus size={14} /> Zaproś
            </Button>
          )}
        </div>
        <div className="divide-y divide-line">
          {members.map((m) => (
            <div key={m.name} className="py-3 flex items-center justify-between">
              <div>
                <p className="text-body font-medium text-granat-900">{m.name}</p>
                <p className="text-caption text-ink-500">
                  {m.relation} · koordynator: {senior.coordinator?.name ?? '—'}
                </p>
              </div>
              <Badge tone={m.access === 'Pełny' ? 'green' : 'neutral'}>{m.access}</Badge>
            </div>
          ))}
        </div>
        {!can('family:invite') && (
          <p className="text-caption text-ink-400 mt-3">
            Zapraszanie nowych osób wymaga uprawnień opiekuna.
          </p>
        )}
      </CardBody>
    </Card>
  )
}

/* ---------- 8. RODO ---------- */
export function TabGdpr({ senior }: { senior: SeniorDetail }) {
  const consents = [
    { label: 'Nagrywanie rozmów', granted: true, date: '2026-05-02' },
    { label: 'Przetwarzanie danych zdrowotnych (art. 9 RODO)', granted: true, date: '2026-05-02' },
    { label: 'Udostępnianie danych rodzinie', granted: true, date: '2026-05-02' },
    { label: 'Marketing SilverTech', granted: false, date: '—' },
  ]
  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <Card>
        <CardBody>
          <span className="eyebrow flex items-center gap-1.5">
            <ShieldCheck size={13} /> Zgody
          </span>
          <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-3">Rejestr zgód</h3>
          <div className="divide-y divide-line">
            {consents.map((c) => (
              <div key={c.label} className="py-2.5 flex items-center justify-between gap-3">
                <span className="text-body text-ink-700">{c.label}</span>
                <Badge tone={c.granted ? 'green' : 'neutral'}>
                  {c.granted ? `od ${c.date}` : 'brak'}
                </Badge>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
      <Card>
        <CardBody>
          <span className="eyebrow">Prawa podmiotu</span>
          <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-3">Działania (art. 15–20)</h3>
          <div className="space-y-2">
            <Button variant="secondary" fullWidth>
              <Download size={15} /> Eksport danych ({senior.id})
            </Button>
            <Button variant="secondary" fullWidth>
              <Clock size={15} /> Historia dostępu
            </Button>
            <Button variant="danger" fullWidth>
              <Trash2 size={15} /> Wniosek o usunięcie danych
            </Button>
          </div>
          <p className="text-caption text-ink-400 mt-3">
            Usunięcie danych podlega 30-dniowej retencji zgodnej z RODO i wymaga potwierdzenia koordynatora.
          </p>
        </CardBody>
      </Card>
    </div>
  )
}
