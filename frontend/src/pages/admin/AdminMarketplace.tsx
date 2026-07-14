import { useState } from 'react'
import { AdminPageHead, DataTable } from '@/components/admin'
import type { Column } from '@/components/admin'
import { Tabs, Badge, Card, CardBody } from '@/components/ui'
import type { TabItem } from '@/components/ui'
import { MARKET_ORDERS, MARKET_CATALOG, MARKET_PARTNERS, SERVICE_GAPS } from '@/data/mockAdmin'

const MODE_TONE = { AUTO: 'green', HYBRID: 'gold', MANUAL: 'neutral' } as const
const STATUS_LABEL: Record<string, string> = {
  confirmed: 'Potwierdzone',
  waiting_manual_confirm: 'Oczekuje',
  auto_confirmed: 'Auto',
}

export function AdminMarketplace() {
  const [tab, setTab] = useState('orders')
  const tabs: TabItem[] = [
    { id: 'orders', label: 'Zamówienia', count: MARKET_ORDERS.length },
    { id: 'catalog', label: 'Katalog', count: MARKET_CATALOG.length },
    { id: 'partners', label: 'Partnerzy', count: MARKET_PARTNERS.length },
    { id: 'gaps', label: 'Service Gaps', count: SERVICE_GAPS.length },
  ]

  const orderCols: Column<any>[] = [
    { key: 'id', header: 'ID', render: (r) => <span className="font-mono text-caption text-ink-500">{r.id}</span> },
    { key: 'senior', header: 'Senior', render: (r) => <span className="font-medium text-granat-900">{r.senior}</span> },
    { key: 'category', header: 'Kategoria' },
    { key: 'partner', header: 'Partner' },
    { key: 'amount', header: 'Kwota', align: 'right' },
    { key: 'status', header: 'Status', render: (r) => <Badge tone={r.status === 'confirmed' ? 'green' : r.status === 'waiting_manual_confirm' ? 'gold' : 'granat'}>{STATUS_LABEL[r.status]}</Badge> },
  ]
  const partnerCols: Column<any>[] = [
    { key: 'name', header: 'Partner', render: (r) => <span className="font-medium text-granat-900">{r.name}</span> },
    { key: 'nip', header: 'NIP', render: (r) => <span className="font-mono text-caption text-ink-500">{r.nip}</span> },
    { key: 'category', header: 'Kategoria' },
    { key: 'rating', header: 'Ocena', align: 'center', render: (r) => `★ ${r.rating}` },
    { key: 'status', header: 'Status', render: (r) => <Badge tone={r.status === 'active' ? 'green' : 'gold'}>{r.status === 'active' ? 'Aktywny' : 'Weryfikacja'}</Badge> },
  ]

  return (
    <>
      <AdminPageHead eyebrow="Overview · NEW" title="Marketplace" subtitle="Zamówienia, katalog usług, partnerzy i luki rynkowe" />
      <Tabs items={tabs} value={tab} onChange={setTab} className="mb-5" />

      {tab === 'orders' && <DataTable columns={orderCols} rows={MARKET_ORDERS} />}

      {tab === 'catalog' && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {MARKET_CATALOG.map((c) => (
            <Card key={c.id}>
              <CardBody>
                <div className="flex items-center justify-between">
                  <h4 className="text-body font-medium text-granat-900">{c.name}</h4>
                  <Badge tone={MODE_TONE[c.mode as keyof typeof MODE_TONE]}>{c.mode}</Badge>
                </div>
                <p className="text-label text-ink-500 mt-2">{c.partners} partnerów</p>
                <p className="kpi text-h4 text-granat-800 mt-1">{c.orders30d}</p>
                <p className="text-caption text-ink-400">zamówień / 30 dni</p>
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {tab === 'partners' && <DataTable columns={partnerCols} rows={MARKET_PARTNERS} />}

      {tab === 'gaps' && (
        <div className="space-y-4">
          {SERVICE_GAPS.map((g, i) => (
            <Card key={i} accent="gold">
              <CardBody className="flex items-center justify-between gap-3">
                <div>
                  <h4 className="text-body font-medium text-granat-900">{g.category}</h4>
                  <p className="text-label text-ink-500">{g.district} · popyt: {g.demand}</p>
                </div>
                <Badge tone={g.partners === 0 ? 'red' : 'gold'}>{g.partners} partnerów</Badge>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </>
  )
}
