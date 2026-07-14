import { AdminPageHead } from '@/components/admin'
import { Card, CardBody, Badge, Button } from '@/components/ui'
import { PIPELINES } from '@/data/mockAdmin'
import { ArrowRight } from 'lucide-react'

function Stage({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-paper-2 px-3 py-2 text-center">
      <p className="text-caption uppercase tracking-caps text-ink-400">{label}</p>
      <p className="text-label font-medium text-granat-900 mt-0.5">{value}</p>
    </div>
  )
}

export function AdminPipelines() {
  return (
    <>
      <AdminPageHead eyebrow="Konfiguracja" title="Pipelines" subtitle="Routing STT → LLM → TTS dla agentów"
        actions={<Button variant="gold">Nowy pipeline</Button>} />
      <div className="space-y-4">
        {PIPELINES.map((p) => (
          <Card key={p.id}>
            <CardBody>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-body font-medium text-granat-900">{p.name}</h4>
                <Badge tone="granat">{p.usedBy} agentów</Badge>
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <Stage label="STT" value={p.stt} />
                <ArrowRight size={16} className="text-ink-300" />
                <Stage label="LLM" value={p.llm} />
                <ArrowRight size={16} className="text-ink-300" />
                <Stage label="TTS" value={p.tts} />
              </div>
            </CardBody>
          </Card>
        ))}
      </div>
    </>
  )
}
