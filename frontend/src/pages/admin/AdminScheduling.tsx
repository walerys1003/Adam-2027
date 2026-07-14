import { AdminPageHead, DataTable } from '@/components/admin'
import type { Column } from '@/components/admin'
import { Card, CardBody, Badge, Button } from '@/components/ui'
import { CAMPAIGNS, SCHEDULE_HEATMAP } from '@/data/mockAdmin'

const DAYS = ['Pon', 'Wt', 'Śr', 'Czw', 'Pt', 'Sob', 'Nd']

type Campaign = (typeof CAMPAIGNS)[number]

export function AdminScheduling() {
  const cols: Column<Campaign>[] = [
    { key: 'name', header: 'Kampania', render: (r) => <span className="font-medium text-granat-900">{r.name}</span> },
    { key: 'window', header: 'Okno czasowe' },
    { key: 'seniors', header: 'Seniorzy', align: 'right' },
    { key: 'agent', header: 'Agent', render: (r) => <Badge tone="granat">{r.agent}</Badge> },
    { key: 'status', header: 'Status', render: (r) => <Badge tone={r.status === 'active' ? 'green' : 'neutral'}>{r.status === 'active' ? 'Aktywna' : 'Wstrzymana'}</Badge> },
  ]

  return (
    <>
      <AdminPageHead eyebrow="Overview" title="Harmonogram rozmów" subtitle="Kampanie welfare-check i mapa natężenia połączeń"
        actions={<Button variant="gold">Nowa kampania</Button>} />

      <div className="mb-6">
        <DataTable columns={cols} rows={CAMPAIGNS} />
      </div>

      <Card>
        <CardBody>
          <span className="eyebrow">Natężenie połączeń</span>
          <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-4">Mapa 24h × 7 dni</h3>
          <div className="overflow-x-auto">
            <div className="min-w-[640px]">
              <div className="flex gap-1 mb-1 pl-10">
                {Array.from({ length: 24 }, (_, h) => (
                  <span key={h} className="flex-1 text-center text-[9px] text-ink-400">{h}</span>
                ))}
              </div>
              {DAYS.map((day, d) => (
                <div key={day} className="flex items-center gap-1 mb-1">
                  <span className="w-9 text-caption text-ink-500 text-right pr-1">{day}</span>
                  {Array.from({ length: 24 }, (_, h) => {
                    const cell = SCHEDULE_HEATMAP[d * 24 + h]
                    return (
                      <span
                        key={h}
                        title={`${day} ${h}:00 · natężenie ${Math.round(cell.value * 100)}%`}
                        className="flex-1 aspect-square rounded-sm bg-granat-700"
                        style={{ opacity: 0.12 + cell.value * 0.88 }}
                      />
                    )
                  })}
                </div>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2 mt-3 text-caption text-ink-400">
            <span>mniej</span>
            <span className="w-3 h-3 rounded-sm bg-granat-700" style={{ opacity: 0.15 }} />
            <span className="w-3 h-3 rounded-sm bg-granat-700" style={{ opacity: 0.5 }} />
            <span className="w-3 h-3 rounded-sm bg-granat-700" style={{ opacity: 1 }} />
            <span>więcej</span>
          </div>
        </CardBody>
      </Card>
    </>
  )
}
