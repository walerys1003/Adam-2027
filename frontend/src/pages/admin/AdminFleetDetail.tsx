import { useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Watch, BatteryMedium, Cpu, Wifi, WifiOff, Lock, ShieldCheck, HeartPulse, History } from 'lucide-react'
import { AdminPageHead, StatTile } from '@/components/admin'
import { Card, CardHeader, CardBody, Badge, Button, Timeline } from '@/components/ui'
import type { TimelineItem } from '@/components/ui'
import { FLEET_DEVICES, FLEET_AUDIT } from '@/data/mockAdmin'

const BRAND_LABEL = { xiaomi: 'Xiaomi', apple: 'Apple', garmin: 'Garmin', fitbit: 'Fitbit' }
const SYNC_TONE = { ok: 'green', delayed: 'gold', offline: 'red' } as const
const SYNC_LABEL = { ok: 'Zsynchronizowany', delayed: 'Opóźniony', offline: 'Offline' }
const ROLE_LEVEL: Record<string, TimelineItem['level']> = {
  doctor: 'purple',
  coordinator: 'green',
  system: undefined,
}
const ROLE_LABEL: Record<string, string> = {
  doctor: 'Lekarz',
  coordinator: 'Koordynator',
  system: 'System',
}

export function AdminFleetDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const device = useMemo(() => FLEET_DEVICES.find((d) => d.id === id), [id])

  // Audit trail: zdarzenia tego urządzenia + wpisy globalne dopasowane po id
  const auditItems: TimelineItem[] = useMemo(
    () =>
      FLEET_AUDIT.filter((a) => !device || a.device === device.id || FLEET_AUDIT.length <= 3).map((a) => ({
        id: a.id,
        title: a.action,
        time: a.at,
        level: ROLE_LEVEL[a.role],
        description: (
          <span>
            {a.by} · <span className="text-ink-400">{ROLE_LABEL[a.role] ?? a.role}</span>
            {device && a.device !== device.id && (
              <span className="ml-2 font-mono text-caption text-ink-300">({a.device})</span>
            )}
          </span>
        ),
      })),
    [device],
  )

  if (!device) {
    return (
      <>
        <AdminPageHead eyebrow="Konfiguracja" title="Urządzenie nie znalezione" />
        <Button variant="ghost" onClick={() => navigate('/admin/fleet')}>
          <ArrowLeft size={16} className="mr-1" /> Powrót do floty
        </Button>
      </>
    )
  }

  const syncTone = SYNC_TONE[device.sync]

  return (
    <>
      <button
        onClick={() => navigate('/admin/fleet')}
        className="inline-flex items-center gap-1 text-label text-ink-500 hover:text-granat-700 mb-4"
      >
        <ArrowLeft size={15} /> Wearables Fleet
      </button>

      <AdminPageHead
        eyebrow={`Urządzenie · ${device.id}`}
        title={`${BRAND_LABEL[device.brand]} ${device.model}`}
        subtitle={`Przypisane do: ${device.senior}`}
        actions={
          device.mode === 'manual_override' ? (
            <Badge tone="gold">
              <Lock size={11} className="mr-1 inline" /> Ręczny override
            </Badge>
          ) : (
            <Badge tone="neutral">Tryb automatyczny</Badge>
          )
        }
      />

      {/* KPI urządzenia */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatTile
          label="Bateria"
          value={`${device.battery}%`}
          icon={<BatteryMedium size={18} />}
          accent={device.battery < 25 ? 'red' : 'green'}
        />
        <StatTile label="Firmware" value={device.firmware} icon={<Cpu size={18} />} accent="granat" />
        <StatTile
          label="Synchronizacja"
          value={SYNC_LABEL[device.sync]}
          icon={device.sync === 'offline' ? <WifiOff size={18} /> : <Wifi size={18} />}
          accent={syncTone}
        />
        <StatTile
          label="Tryb pracy"
          value={device.mode === 'manual_override' ? 'Override' : 'Auto'}
          icon={<ShieldCheck size={18} />}
          accent={device.mode === 'manual_override' ? 'gold' : 'granat'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Progi pomiarowe */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <h3 className="font-serif text-h4 text-granat-900 flex items-center gap-2">
                <HeartPulse size={18} className="text-sem-red" /> Progi pomiarowe
              </h3>
            </CardHeader>
            <CardBody className="space-y-3">
              <Threshold label="Tętno (HR)" range="48 – 105 bpm" overridden={device.mode === 'manual_override'} />
              <Threshold label="SpO₂" range="≥ 93%" />
              <Threshold label="Ciśnienie skurczowe" range="100 – 145 mmHg" />
              <Threshold label="Aktywność (kroki)" range="≥ 1 500 / dzień" />
              {device.mode === 'manual_override' && (
                <div className="mt-3 flex items-start gap-2 rounded-md bg-zloto-50 border border-zloto-200 p-3">
                  <Lock size={14} className="text-zloto-700 mt-0.5 shrink-0" />
                  <p className="text-caption text-ink-700">
                    Progi ustawione ręcznie przez personel medyczny — automatyczna kalibracja wstrzymana.
                  </p>
                </div>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="font-serif text-h4 text-granat-900 flex items-center gap-2">
                <Watch size={18} className="text-granat-500" /> Identyfikacja
              </h3>
            </CardHeader>
            <CardBody className="space-y-2 text-label">
              <Row k="ID urządzenia" v={<span className="font-mono">{device.id}</span>} />
              <Row k="Marka" v={BRAND_LABEL[device.brand]} />
              <Row k="Model" v={device.model} />
              <Row k="Firmware" v={<span className="font-mono">{device.firmware}</span>} />
              <Row k="Senior" v={device.senior} />
            </CardBody>
          </Card>
        </div>

        {/* Audit trail */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="font-serif text-h4 text-granat-900 flex items-center gap-2">
                  <History size={18} className="text-granat-500" /> Dziennik audytu
                </h3>
                <Badge tone="neutral">{auditItems.length} zdarzeń</Badge>
              </div>
            </CardHeader>
            <CardBody>
              <Timeline items={auditItems} />
            </CardBody>
          </Card>
        </div>
      </div>
    </>
  )
}

function Threshold({ label, range, overridden }: { label: string; range: string; overridden?: boolean }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-line last:border-0">
      <span className="text-label text-ink-700">{label}</span>
      <span className="flex items-center gap-2">
        <span className="font-mono text-caption text-granat-900">{range}</span>
        {overridden && <Lock size={11} className="text-zloto-600" />}
      </span>
    </div>
  )
}

function Row({ k, v }: { k: string; v: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-1 border-b border-line last:border-0">
      <span className="text-ink-400">{k}</span>
      <span className="text-ink-700 font-medium">{v}</span>
    </div>
  )
}
