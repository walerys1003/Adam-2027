import { useMemo, useState } from 'react'
import { Download, FileAudio } from 'lucide-react'
import { AdminPageHead, DataTable, StatTile } from '@/components/admin'
import type { Column } from '@/components/admin'
import { Button, SemaphoreBadge, Badge } from '@/components/ui'
import { ADMIN_CALLS, ADMIN_KPIS } from '@/data/mockAdmin'
import type { AdminCall } from '@/data/mockAdmin'
import type { SemaphoreLevel } from '@/types/domain'

export function AdminCalls() {
  const [q, setQ] = useState('')
  const rows = useMemo(
    () => ADMIN_CALLS.filter((c) => !q || `${c.senior} ${c.agent} ${c.id}`.toLowerCase().includes(q.toLowerCase())),
    [q],
  )

  const cols: Column<AdminCall>[] = [
    { key: 'id', header: 'ID', render: (r) => <span className="font-mono text-caption text-ink-500">{r.id}</span> },
    { key: 'senior', header: 'Senior', render: (r) => <span className="font-medium text-granat-900">{r.senior}</span> },
    { key: 'agent', header: 'Agent', render: (r) => <Badge tone="granat">{r.agent}</Badge> },
    { key: 'startedAt', header: 'Start', align: 'center' },
    { key: 'duration', header: 'Czas', align: 'center' },
    { key: 'toolsUsed', header: 'Tools', align: 'center' },
    { key: 'outcome', header: 'Wynik', render: (r) => <SemaphoreBadge level={r.outcome as SemaphoreLevel} size="xs" showLabel={false} /> },
    { key: 'actions', header: '', align: 'right', render: () => <Button size="sm" variant="ghost"><FileAudio size={14} /> Transkrypt</Button> },
  ]

  return (
    <>
      <AdminPageHead
        eyebrow="Overview"
        title="Historia rozmów"
        subtitle={`${ADMIN_KPIS.callsTotal.toLocaleString('pl-PL')} rozmów łącznie`}
        search={q}
        onSearch={setQ}
        searchPlaceholder="Szukaj w transkryptach…"
        actions={<Button variant="secondary"><Download size={16} /> Eksport CSV</Button>}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatTile label="Rozmowy 24h" value={ADMIN_KPIS.calls24h} accent="gold" />
        <StatTile label="Śr. czas" value="3:14" accent="granat" />
        <StatTile label="Skuteczność" value={ADMIN_KPIS.successRatePct} unit="%" accent="green" />
        <StatTile label="Eskalacje" value={47} accent="red" />
      </div>

      <DataTable columns={cols} rows={rows} />
    </>
  )
}
