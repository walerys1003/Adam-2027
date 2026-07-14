import { Users, PhoneCall, Bot, Watch, Siren, Activity, Gauge, CheckCircle2 } from 'lucide-react'
import { AdminPageHead, StatTile } from '@/components/admin'
import { Card, CardBody, SemaphoreBadge } from '@/components/ui'
import { ADMIN_KPIS, SEMAPHORE_DISTRIBUTION, ADMIN_ALERTS } from '@/data/mockAdmin'
import type { SemaphoreLevel } from '@/types/domain'

export function AdminDashboard() {
  const total = SEMAPHORE_DISTRIBUTION.reduce((s, d) => s + d.count, 0)
  return (
    <>
      <AdminPageHead eyebrow="Overview" title="Dashboard systemowy" subtitle="Stan całej floty Adama w czasie rzeczywistym" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatTile label="Seniorzy aktywni" value={ADMIN_KPIS.seniorsActive} icon={<Users size={18} />} trend="up" trendLabel={`z ${ADMIN_KPIS.seniorsTotal}`} />
        <StatTile label="Rozmowy 24h" value={ADMIN_KPIS.calls24h} icon={<PhoneCall size={18} />} accent="gold" trend="up" trendLabel="+8%" />
        <StatTile label="Agenci aktywni" value={ADMIN_KPIS.agentsActive} icon={<Bot size={18} />} accent="granat" />
        <StatTile label="Urządzenia" value={ADMIN_KPIS.devicesTotal} icon={<Watch size={18} />} accent="granat" />
        <StatTile label="Alerty otwarte" value={ADMIN_KPIS.alertsOpen} icon={<Siren size={18} />} accent="red" trend="down" trendLabel="-3" />
        <StatTile label="Uptime" value={ADMIN_KPIS.uptimePct} unit="%" icon={<Activity size={18} />} accent="green" />
        <StatTile label="Śr. latencja" value={ADMIN_KPIS.avgLatencyMs} unit="ms" icon={<Gauge size={18} />} accent="gold" />
        <StatTile label="Skuteczność" value={ADMIN_KPIS.successRatePct} unit="%" icon={<CheckCircle2 size={18} />} accent="green" />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        {/* Semaphore distribution */}
        <Card className="lg:col-span-1">
          <CardBody>
            <span className="eyebrow">Rozkład semafora</span>
            <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-4">Cała flota</h3>
            <div className="space-y-3">
              {SEMAPHORE_DISTRIBUTION.map((d) => {
                const pct = Math.round((d.count / total) * 100)
                const color =
                  d.level === 'green' ? 'var(--sem-green)' : d.level === 'yellow' ? 'var(--sem-yellow)' : d.level === 'red' ? 'var(--sem-red)' : 'var(--sem-purple)'
                return (
                  <div key={d.level}>
                    <div className="flex items-center justify-between mb-1">
                      <SemaphoreBadge level={d.level as SemaphoreLevel} size="xs" />
                      <span className="text-label text-ink-600">{d.count} · {pct}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-paper-3 overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${pct}%`, background: color }} />
                    </div>
                  </div>
                )
              })}
            </div>
          </CardBody>
        </Card>

        {/* Active critical alerts */}
        <Card className="lg:col-span-2">
          <CardBody>
            <span className="eyebrow">Alerty krytyczne</span>
            <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-4">Wymagają uwagi</h3>
            <div className="divide-y divide-line">
              {ADMIN_ALERTS.map((a) => (
                <div key={a.id} className="py-3 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    <SemaphoreBadge level={a.level as SemaphoreLevel} size="xs" showLabel={false} />
                    <div className="min-w-0">
                      <p className="text-body font-medium text-granat-900 truncate">{a.senior}</p>
                      <p className="text-label text-ink-500 truncate">{a.reason} · {a.stage}</p>
                    </div>
                  </div>
                  <span className="text-caption text-ink-400 shrink-0">{a.age}</span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>
    </>
  )
}
