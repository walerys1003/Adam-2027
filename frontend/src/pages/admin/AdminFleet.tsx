import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Watch, Wifi, WifiOff, Lock } from 'lucide-react'
import { AdminPageHead, DataTable, StatTile } from '@/components/admin'
import type { Column } from '@/components/admin'
import { Badge } from '@/components/ui'
import { FLEET_DEVICES, FLEET_STATS } from '@/data/mockAdmin'
import type { FleetDevice } from '@/data/mockAdmin'

const BRAND_LABEL = { xiaomi: 'Xiaomi', apple: 'Apple', garmin: 'Garmin', fitbit: 'Fitbit' }
const SYNC_TONE = { ok: 'green', delayed: 'gold', offline: 'red' } as const
const SYNC_LABEL = { ok: 'OK', delayed: 'Opóźniony', offline: 'Offline' }

export function AdminFleet() {
  const navigate = useNavigate()
  const [q, setQ] = useState('')
  const rows = useMemo(
    () => FLEET_DEVICES.filter((d) => !q || `${d.senior} ${d.id} ${d.brand}`.toLowerCase().includes(q.toLowerCase())),
    [q],
  )

  const cols: Column<FleetDevice>[] = [
    { key: 'id', header: 'Urządzenie', render: (r) => <span className="font-mono text-caption text-ink-500">{r.id}</span> },
    { key: 'senior', header: 'Senior', render: (r) => <span className="font-medium text-granat-900">{r.senior}</span> },
    { key: 'brand', header: 'Marka', render: (r) => `${BRAND_LABEL[r.brand]} ${r.model}` },
    { key: 'battery', header: 'Bateria', align: 'center', render: (r) => <span className={r.battery < 25 ? 'text-sem-red' : 'text-ink-700'}>{r.battery}%</span> },
    { key: 'firmware', header: 'Firmware', align: 'center', render: (r) => <span className="font-mono text-caption text-ink-500">{r.firmware}</span> },
    { key: 'mode', header: 'Tryb', render: (r) => r.mode === 'manual_override' ? <Badge tone="gold"><Lock size={10} className="mr-1 inline" />override</Badge> : <Badge tone="neutral">auto</Badge> },
    { key: 'sync', header: 'Sync', render: (r) => <Badge tone={SYNC_TONE[r.sync]}>{SYNC_LABEL[r.sync]}</Badge> },
  ]

  return (
    <>
      <AdminPageHead
        eyebrow="Konfiguracja · NEW"
        title="Wearables Fleet"
        subtitle={`${FLEET_STATS.total} urządzeń w 4 markach`}
        search={q}
        onSearch={setQ}
        searchPlaceholder="Szukaj urządzenia…"
      />

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        <StatTile label="Wszystkie" value={FLEET_STATS.total} icon={<Watch size={18} />} accent="granat" />
        <StatTile label="Zsynchr." value={FLEET_STATS.ok} icon={<Wifi size={18} />} accent="green" />
        <StatTile label="Opóźnione" value={FLEET_STATS.delayed} accent="gold" />
        <StatTile label="Offline" value={FLEET_STATS.offline} icon={<WifiOff size={18} />} accent="red" />
        <StatTile label="Override" value={FLEET_STATS.overrides} icon={<Lock size={18} />} accent="gold" />
      </div>

      <DataTable columns={cols} rows={rows} onRowClick={(r) => navigate(`/admin/fleet/${r.id}`)} />
    </>
  )
}
