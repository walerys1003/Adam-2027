import { useMemo, useState } from 'react'
import { AdminPageHead } from '@/components/admin'
import { Card, CardBody, Badge, Toggle, Tabs } from '@/components/ui'
import type { TabItem } from '@/components/ui'
import { TOOLS } from '@/data/mockAdmin'

const PHASES = ['F3', 'F6', 'F8', 'F11'] as const
const PHASE_LABEL: Record<string, string> = {
  all: 'Wszystkie',
  F3: 'F3 · Semafor',
  F6: 'F6 · Leki',
  F8: 'F8 · Kryzys',
  F11: 'F11 · Marketplace',
}

export function AdminTools() {
  const [phase, setPhase] = useState('all')
  const [tools, setTools] = useState(TOOLS)

  const tabs: TabItem[] = [
    { id: 'all', label: PHASE_LABEL.all, count: TOOLS.length },
    ...PHASES.map((p) => ({ id: p, label: PHASE_LABEL[p], count: TOOLS.filter((t) => t.phase === p).length })),
  ]
  const filtered = useMemo(() => (phase === 'all' ? tools : tools.filter((t) => t.phase === phase)), [tools, phase])

  const toggle = (id: string) => setTools((ts) => ts.map((t) => (t.id === id ? { ...t, enabled: !t.enabled } : t)))

  return (
    <>
      <AdminPageHead eyebrow="Konfiguracja" title="Tools" subtitle="47 narzędzi wywoływanych przez agentów, w 4 fazach" />
      <Tabs items={tabs} value={phase} onChange={setPhase} className="mb-5" />
      <Card>
        <CardBody className="p-0">
          <div className="divide-y divide-line">
            {filtered.map((t) => (
              <div key={t.id} className="flex items-center justify-between px-5 py-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-body text-granat-900">{t.name}</span>
                  <Badge tone="granat">{t.phase}</Badge>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-caption text-ink-400">{t.enabled ? 'włączone' : 'wyłączone'}</span>
                  <Toggle checked={t.enabled} onChange={() => toggle(t.id)} size="sm" />
                </div>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
    </>
  )
}
