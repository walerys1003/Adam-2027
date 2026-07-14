import { AdminPageHead } from '@/components/admin'
import { Card, CardBody, Badge, Button, RadialGauge } from '@/components/ui'
import { AUDIO_PROFILES } from '@/data/mockAdmin'

export function AdminAudio() {
  return (
    <>
      <AdminPageHead eyebrow="Konfiguracja" title="Audio Profiles" subtitle="Profile brzmienia dostosowane do seniorów (F13)"
        actions={<Button variant="gold">Nowy profil</Button>} />
      <div className="grid gap-4 lg:grid-cols-3">
        {AUDIO_PROFILES.map((p) => (
          <Card key={p.id}>
            <CardBody className="flex items-center gap-5">
              <RadialGauge value={p.effectiveness} size={88} sublabel="skuteczność" />
              <div>
                <h4 className="text-body font-medium text-granat-900">{p.name}</h4>
                <p className="text-label text-ink-500 mt-1">{p.desc}</p>
                <Badge tone="granat" className="mt-2">{p.usedBy} agentów</Badge>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>
    </>
  )
}
