import { Boxes, Cpu, MemoryStick, Clock, RotateCcw, Square, Play } from 'lucide-react'
import { AdminPageHead, StatTile } from '@/components/admin'
import { Card, CardBody, Badge, Button } from '@/components/ui'
import { DOCKER_SERVICES } from '@/data/mockAdmin'

export function AdminDocker() {
  const running = DOCKER_SERVICES.filter((s) => s.status === 'running').length

  return (
    <>
      <AdminPageHead
        eyebrow="System"
        title="Usługi Docker"
        subtitle="Kontenery stacku Adam — status, zasoby, cykl życia"
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatTile label="Kontenery" value={DOCKER_SERVICES.length} icon={<Boxes size={18} />} accent="granat" />
        <StatTile label="Uruchomione" value={running} icon={<Play size={18} />} accent="green" />
        <StatTile label="CPU łącznie" value="25%" icon={<Cpu size={18} />} accent="granat" />
        <StatTile label="RAM łącznie" value="1.1 GB" icon={<MemoryStick size={18} />} accent="gold" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {DOCKER_SERVICES.map((s) => (
          <Card key={s.id} accent={s.status === 'running' ? 'none' : 'red'}>
            <CardBody className="space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-serif text-h4 text-granat-900">{s.name}</h3>
                  <p className="font-mono text-caption text-ink-400 mt-0.5">{s.image}</p>
                </div>
                <Badge tone={s.status === 'running' ? 'green' : 'red'}>
                  <span className={s.status === 'running' ? 'w-1.5 h-1.5 rounded-full bg-sem-green mr-1.5 inline-block' : 'w-1.5 h-1.5 rounded-full bg-sem-red mr-1.5 inline-block'} />
                  {s.status === 'running' ? 'Działa' : 'Zatrzymany'}
                </Badge>
              </div>

              <div className="grid grid-cols-3 gap-3 pt-1">
                <Metric icon={<Cpu size={13} />} label="CPU" value={s.cpu} />
                <Metric icon={<MemoryStick size={13} />} label="RAM" value={s.mem} />
                <Metric icon={<Clock size={13} />} label="Uptime" value={s.uptime} />
              </div>

              <div className="flex gap-2 pt-2 border-t border-line">
                <Button variant="secondary" size="sm">
                  <RotateCcw size={13} className="mr-1" /> Restart
                </Button>
                <Button variant="ghost" size="sm">
                  <Square size={13} className="mr-1" /> Stop
                </Button>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>
    </>
  )
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-md bg-paper-2 p-2 text-center">
      <div className="flex items-center justify-center gap-1 text-ink-400 text-caption">
        {icon} {label}
      </div>
      <div className="font-mono text-body text-granat-900 mt-0.5">{value}</div>
    </div>
  )
}
