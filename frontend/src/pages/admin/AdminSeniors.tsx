import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { AdminPageHead, DataTable } from '@/components/admin'
import type { Column } from '@/components/admin'
import { Button, SemaphoreBadge, PackageBadge } from '@/components/ui'
import { ADMIN_SENIORS } from '@/data/mockAdmin'
import type { AdminSenior } from '@/data/mockAdmin'
import type { SemaphoreLevel, Package } from '@/types/domain'

const PAGE = 12

export function AdminSeniors() {
  const navigate = useNavigate()
  const [q, setQ] = useState('')
  const [page, setPage] = useState(0)

  const filtered = useMemo(
    () => ADMIN_SENIORS.filter((s) => !q || `${s.name} ${s.id} ${s.district}`.toLowerCase().includes(q.toLowerCase())),
    [q],
  )
  const pages = Math.ceil(filtered.length / PAGE)
  const rows = filtered.slice(page * PAGE, page * PAGE + PAGE)

  const cols: Column<AdminSenior>[] = [
    { key: 'id', header: 'ID', render: (r) => <span className="font-mono text-caption text-ink-500">{r.id}</span> },
    { key: 'name', header: 'Senior', render: (r) => <span className="font-medium text-granat-900">{r.name}</span> },
    { key: 'age', header: 'Wiek', align: 'center' },
    { key: 'district', header: 'Dzielnica' },
    { key: 'package', header: 'Pakiet', render: (r) => <PackageBadge package={r.package as Package} /> },
    { key: 'semaphore', header: 'Semafor', render: (r) => <SemaphoreBadge level={r.semaphore as SemaphoreLevel} size="xs" /> },
    { key: 'coordinator', header: 'Koordynator' },
    { key: 'adherence', header: 'Leki', align: 'right', render: (r) => `${r.adherence}%` },
    { key: 'lastCall', header: 'Ost. rozmowa', align: 'right', render: (r) => <span className="text-ink-400">{r.lastCall}</span> },
  ]

  return (
    <>
      <AdminPageHead
        eyebrow="Overview"
        title="Seniorzy"
        subtitle={`${filtered.length} z 1247 podopiecznych`}
        search={q}
        onSearch={(v) => { setQ(v); setPage(0) }}
        searchPlaceholder="Szukaj seniora…"
        actions={<Button variant="gold"><Plus size={16} /> Dodaj seniora</Button>}
      />

      <DataTable columns={cols} rows={rows} onRowClick={(r) => navigate(`/admin/seniors/${r.id}`)} />

      <div className="flex items-center justify-between mt-4 text-label text-ink-500">
        <span>Strona {page + 1} z {pages}</span>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>Poprzednia</Button>
          <Button variant="secondary" size="sm" disabled={page >= pages - 1} onClick={() => setPage((p) => p + 1)}>Następna</Button>
        </div>
      </div>
    </>
  )
}
