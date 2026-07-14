import { AdminPageHead } from '@/components/admin'
import { Card, CardBody, SemaphoreBadge, Button, Badge } from '@/components/ui'
import { ADMIN_ALERTS, ESCALATION_LADDER } from '@/data/mockAdmin'
import type { SemaphoreLevel } from '@/types/domain'
import { ArrowDown } from 'lucide-react'

export function AdminAlerts() {
  return (
    <>
      <AdminPageHead eyebrow="Overview" title="Alerty" subtitle="Aktywne zdarzenia semafora i drabina eskalacji" />

      <div className="grid gap-5 lg:grid-cols-3">
        {/* Active alerts */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="font-serif text-h4 text-granat-900">Aktywne alerty ({ADMIN_ALERTS.length})</h3>
          {ADMIN_ALERTS.map((a) => (
            <Card key={a.id} accent={a.level === 'purple' ? 'purple' : a.level === 'red' ? 'red' : 'gold'}>
              <CardBody>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <SemaphoreBadge level={a.level as SemaphoreLevel} size="sm" />
                      <span className="text-caption text-ink-400">{a.age}</span>
                    </div>
                    <h4 className="text-body font-medium text-granat-900 mt-2">{a.senior}</h4>
                    <p className="text-label text-ink-500">{a.reason}</p>
                    <p className="text-label text-ink-600 mt-1">
                      Etap: <b>{a.stage}</b> · koordynator: {a.coordinator}
                    </p>
                  </div>
                  <div className="flex flex-col gap-2 shrink-0">
                    <Button size="sm" variant="primary">Podejmij</Button>
                    <Button size="sm" variant="secondary">Historia</Button>
                  </div>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>

        {/* Escalation ladder */}
        <Card>
          <CardBody>
            <span className="eyebrow">Protokół</span>
            <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-4">Drabina eskalacji</h3>
            <ol className="space-y-3">
              {ESCALATION_LADDER.map((s, i) => (
                <li key={s.step}>
                  <div className="flex items-start gap-3">
                    <span className="w-6 h-6 rounded-full bg-granat-700 text-white text-caption flex items-center justify-center shrink-0">{s.step}</span>
                    <div>
                      <p className="text-body font-medium text-granat-900">{s.label}</p>
                      <p className="text-label text-ink-500">{s.detail}</p>
                    </div>
                  </div>
                  {i < ESCALATION_LADDER.length - 1 && (
                    <div className="pl-3 text-ink-300"><ArrowDown size={14} /></div>
                  )}
                </li>
              ))}
            </ol>
            <Badge tone="red" className="mt-4">PURPLE zawsze → 112</Badge>
          </CardBody>
        </Card>
      </div>
    </>
  )
}
