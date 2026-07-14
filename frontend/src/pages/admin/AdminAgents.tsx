import { useNavigate } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { AdminPageHead, DataTable } from '@/components/admin'
import type { Column } from '@/components/admin'
import { Button, Badge } from '@/components/ui'
import { ADMIN_AGENTS } from '@/data/mockAdmin'
import type { AdminAgent } from '@/data/mockAdmin'

const STATUS_TONE = { active: 'green', draft: 'gold', paused: 'neutral' } as const
const STATUS_LABEL = { active: 'Aktywny', draft: 'Szkic', paused: 'Wstrzymany' } as const

export function AdminAgents() {
  const navigate = useNavigate()
  const cols: Column<AdminAgent>[] = [
    { key: 'name', header: 'Agent', render: (r) => <span className="font-mono text-body text-granat-900">{r.name}</span> },
    { key: 'role', header: 'Rola' },
    { key: 'model', header: 'Model', render: (r) => <Badge tone="granat">{r.model}</Badge> },
    { key: 'voice', header: 'Głos' },
    { key: 'calls30d', header: 'Rozmowy 30d', align: 'right', render: (r) => r.calls30d.toLocaleString('pl-PL') },
    { key: 'successRate', header: 'Skuteczność', align: 'right', render: (r) => (r.successRate ? `${r.successRate}%` : '—') },
    { key: 'status', header: 'Status', render: (r) => <Badge tone={STATUS_TONE[r.status]}>{STATUS_LABEL[r.status]}</Badge> },
  ]

  return (
    <>
      <AdminPageHead eyebrow="Konfiguracja" title="Agenci" subtitle="12 agentów głosowych Adama"
        actions={<Button variant="gold"><Plus size={16} /> Nowy agent</Button>} />
      <DataTable columns={cols} rows={ADMIN_AGENTS} onRowClick={(r) => navigate(`/admin/agents/${r.id}`)} />
    </>
  )
}
