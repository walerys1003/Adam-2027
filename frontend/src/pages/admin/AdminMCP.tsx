import { AdminPageHead } from '@/components/admin'
import { Card, CardBody, Badge, Button } from '@/components/ui'
import { MCP_SERVERS, MCP_CATALOG } from '@/data/mockAdmin'
import { Plug, Plus } from 'lucide-react'

export function AdminMCP() {
  return (
    <>
      <AdminPageHead eyebrow="Konfiguracja" title="MCP Servers" subtitle="Serwery Model Context Protocol — 3 aktywne, 6 w katalogu" />

      <h3 className="font-serif text-h4 text-granat-900 mb-3">Aktywne serwery</h3>
      <div className="grid gap-4 sm:grid-cols-3 mb-8">
        {MCP_SERVERS.map((m) => (
          <Card key={m.id}>
            <CardBody>
              <div className="flex items-center justify-between">
                <span className="w-9 h-9 rounded-md bg-granat-50 text-granat-700 flex items-center justify-center"><Plug size={17} /></span>
                <Badge tone="green">Połączony</Badge>
              </div>
              <h4 className="text-body font-mono text-granat-900 mt-3">{m.name}</h4>
              <p className="text-label text-ink-500 mt-1">{m.tools} narzędzi · {m.transport}</p>
            </CardBody>
          </Card>
        ))}
      </div>

      <h3 className="font-serif text-h4 text-granat-900 mb-3">Katalog</h3>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {MCP_CATALOG.map((name) => (
          <Card key={name}>
            <CardBody className="flex items-center justify-between">
              <span className="font-mono text-body text-ink-700">{name}</span>
              <Button size="sm" variant="secondary"><Plus size={14} /> Dodaj</Button>
            </CardBody>
          </Card>
        ))}
      </div>
    </>
  )
}
