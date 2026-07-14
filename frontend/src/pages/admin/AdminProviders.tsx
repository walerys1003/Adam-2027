import { AdminPageHead } from '@/components/admin'
import { Card, CardBody, Badge, Button } from '@/components/ui'
import { PROVIDERS } from '@/data/mockAdmin'

export function AdminProviders() {
  return (
    <>
      <AdminPageHead eyebrow="Konfiguracja" title="Providers" subtitle="7 zewnętrznych dostawców AI i telefonii"
        actions={<Button variant="gold">Dodaj providera</Button>} />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {PROVIDERS.map((p) => (
          <Card key={p.id}>
            <CardBody>
              <div className="flex items-center justify-between">
                <h4 className="text-body font-medium text-granat-900">{p.name}</h4>
                <Badge tone={p.status === 'connected' ? 'green' : 'neutral'}>{p.status === 'connected' ? 'Połączony' : 'Standby'}</Badge>
              </div>
              <Badge tone="granat" className="mt-2">{p.type}</Badge>
              <p className="text-label text-ink-500 mt-3">{p.models}</p>
              <p className="text-caption text-ink-400 mt-1">Latencja: {p.latency}</p>
              <Button size="sm" variant="secondary" fullWidth className="mt-3">Konfiguruj</Button>
            </CardBody>
          </Card>
        ))}
      </div>
    </>
  )
}
