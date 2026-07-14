import { AdminPageHead } from '@/components/admin'
import { Card, CardBody, Badge, Button } from '@/components/ui'
import { AlertTriangle } from 'lucide-react'

const LEGACY_CONTEXTS = [
  { id: 'ctx-1', name: 'default-context', agents: 8, note: 'Migracja do Pipelines zalecana' },
  { id: 'ctx-2', name: 'crisis-context', agents: 1, note: 'Migracja do Pipelines zalecana' },
  { id: 'ctx-3', name: 'companion-context', agents: 3, note: 'Migracja do Pipelines zalecana' },
]

export function AdminContexts() {
  return (
    <>
      <AdminPageHead eyebrow="Konfiguracja · Legacy" title="Contexts" subtitle="Starszy mechanizm konfiguracji (przed Pipelines)" />

      <Card accent="gold" className="mb-5">
        <CardBody className="flex items-start gap-3">
          <AlertTriangle size={20} className="text-zloto-600 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-body font-medium text-granat-900">Mechanizm przestarzały</h4>
            <p className="text-label text-ink-600 mt-0.5">
              Contexts zostaną wycofane w AVA v8. Zmigruj konfiguracje do <b>Pipelines</b> (STT→LLM→TTS).
            </p>
            <Button size="sm" variant="gold" className="mt-3">Migruj wszystkie do Pipelines</Button>
          </div>
        </CardBody>
      </Card>

      <div className="space-y-3">
        {LEGACY_CONTEXTS.map((c) => (
          <Card key={c.id}>
            <CardBody className="flex items-center justify-between">
              <div>
                <h4 className="text-body font-mono text-granat-900">{c.name}</h4>
                <p className="text-label text-ink-500">{c.agents} agentów · {c.note}</p>
              </div>
              <Badge tone="neutral">legacy</Badge>
            </CardBody>
          </Card>
        ))}
      </div>
    </>
  )
}
