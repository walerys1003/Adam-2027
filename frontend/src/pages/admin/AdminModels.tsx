import { useMemo, useState } from 'react'
import { Brain, Mic, Volume2, Coins } from 'lucide-react'
import { AdminPageHead } from '@/components/admin'
import { Card, CardBody, Badge, Tabs } from '@/components/ui'
import type { TabItem } from '@/components/ui'
import { MODELS_CATALOG } from '@/data/mockAdmin'

const TYPE_META: Record<string, { tone: 'granat' | 'gold' | 'info'; icon: React.ReactNode }> = {
  LLM: { tone: 'granat', icon: <Brain size={16} /> },
  STT: { tone: 'info', icon: <Mic size={16} /> },
  TTS: { tone: 'gold', icon: <Volume2 size={16} /> },
}

export function AdminModels() {
  const [type, setType] = useState('all')

  const rows = useMemo(
    () => MODELS_CATALOG.filter((m) => type === 'all' || m.type === type),
    [type],
  )

  const tabs: TabItem[] = [
    { id: 'all', label: 'Wszystkie', count: MODELS_CATALOG.length },
    { id: 'LLM', label: 'LLM', count: MODELS_CATALOG.filter((m) => m.type === 'LLM').length },
    { id: 'STT', label: 'STT', count: MODELS_CATALOG.filter((m) => m.type === 'STT').length },
    { id: 'TTS', label: 'TTS', count: MODELS_CATALOG.filter((m) => m.type === 'TTS').length },
  ]

  return (
    <>
      <AdminPageHead
        eyebrow="System"
        title="Katalog modeli"
        subtitle="Dostępne modele LLM / STT / TTS i ich koszty"
      />

      <div className="mb-5">
        <Tabs items={tabs} value={type} onChange={setType} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {rows.map((m) => {
          const meta = TYPE_META[m.type]
          return (
            <Card key={m.id} interactive>
              <CardBody className="space-y-3">
                <div className="flex items-start justify-between">
                  <span className="w-9 h-9 rounded-md bg-granat-50 text-granat-700 flex items-center justify-center">
                    {meta.icon}
                  </span>
                  <Badge tone={meta.tone}>{m.type}</Badge>
                </div>
                <div>
                  <h3 className="font-serif text-h4 text-granat-900">{m.name}</h3>
                  <p className="text-caption text-ink-400 mt-0.5">{m.provider}</p>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-line text-label">
                  <span className="text-ink-500">Kontekst: <span className="text-ink-700 font-medium">{m.context}</span></span>
                  <span className="flex items-center gap-1 text-zloto-700 font-medium">
                    <Coins size={13} /> {m.cost}
                  </span>
                </div>
              </CardBody>
            </Card>
          )
        })}
      </div>
    </>
  )
}
