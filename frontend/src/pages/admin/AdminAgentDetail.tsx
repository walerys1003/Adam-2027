import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'
import { AdminPageHead } from '@/components/admin'
import { Tabs, Card, CardBody, Button, Badge, Toggle } from '@/components/ui'
import type { TabItem } from '@/components/ui'
import { ADMIN_AGENTS } from '@/data/mockAdmin'

const TABS: TabItem[] = [
  { id: 'prompt', label: 'Prompt YAML' },
  { id: 'tools', label: 'Tools' },
  { id: 'voice', label: 'Głos' },
  { id: 'guardrails', label: 'Guardrails' },
  { id: 'ab', label: 'A/B Testing' },
  { id: 'metrics', label: 'Metryki' },
  { id: 'deploy', label: 'Deploy' },
]

const SAMPLE_YAML = `name: welfare-morning
version: 7.4.2
role: Poranny welfare-check
model: gpt-4o
temperature: 0.6
system_prompt: |
  Jesteś Adamem — ciepłym, cierpliwym towarzyszem seniora.
  Mów wolno i wyraźnie. Zapytaj o samopoczucie, sen i leki.
  Jeśli wykryjesz niepokój → ustaw semafor i eskaluj.
semaphore:
  triggers:
    fall_detected: purple
    no_response: red
    mood_below: 0.5 -> yellow`

export function AdminAgentDetail() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const agent = ADMIN_AGENTS.find((a) => a.id === id) ?? ADMIN_AGENTS[0]
  const [tab, setTab] = useState('prompt')

  return (
    <>
      <button onClick={() => navigate('/admin/agents')} className="inline-flex items-center gap-1.5 text-label text-ink-500 hover:text-granat-700 mb-4">
        <ArrowLeft size={15} /> Powrót do agentów
      </button>
      <AdminPageHead
        eyebrow={`Agent · ${agent.id}`}
        title={agent.name}
        subtitle={`${agent.role} · ${agent.model} · ${agent.voice}`}
        actions={<Button variant="primary"><Save size={16} /> Zapisz</Button>}
      />

      <Tabs items={TABS} value={tab} onChange={setTab} className="mb-5" />

      {tab === 'prompt' && (
        <Card><CardBody>
          <span className="eyebrow">Prompt YAML</span>
          <pre className="mt-3 bg-granat-900 text-paper rounded-lg p-4 overflow-x-auto text-caption font-mono leading-relaxed">{SAMPLE_YAML}</pre>
        </CardBody></Card>
      )}

      {tab === 'tools' && (
        <Card><CardBody>
          <span className="eyebrow">Przypisane narzędzia</span>
          <div className="flex flex-wrap gap-2 mt-3">
            {['get_senior_profile', 'log_mood', 'set_semaphore', 'get_medications', 'escalate_alert', 'call_112'].map((t) => (
              <Badge key={t} tone="granat">{t}</Badge>
            ))}
          </div>
        </CardBody></Card>
      )}

      {tab === 'voice' && (
        <Card><CardBody>
          <span className="eyebrow">Konfiguracja głosu</span>
          <div className="mt-3 space-y-2 text-body text-ink-700">
            <p>Głos: <b>{agent.voice}</b></p>
            <p>Profil audio: <Badge tone="gold">Senior-Clear</Badge></p>
            <p>Tempo: 0.9× · Wysokość: +2 · Pauzy: rozszerzone</p>
          </div>
        </CardBody></Card>
      )}

      {tab === 'guardrails' && (
        <Card><CardBody>
          <span className="eyebrow">Guardrails (F4/F5)</span>
          <div className="mt-3 space-y-3">
            {['Blokada porad medycznych', 'Ochrona przed manipulacją (scam-shield)', 'Filtr treści wrażliwych', 'Wymuszona eskalacja przy słowach-kluczach kryzysu'].map((g) => (
              <div key={g} className="flex items-center justify-between">
                <span className="text-body text-ink-700">{g}</span>
                <Toggle checked onChange={() => {}} />
              </div>
            ))}
          </div>
        </CardBody></Card>
      )}

      {tab === 'ab' && (
        <Card><CardBody>
          <span className="eyebrow">A/B Testing</span>
          <p className="text-body text-ink-500 mt-2">Wariant A (70%) vs Wariant B (30%) · metryka: skuteczność welfare-check.</p>
          <div className="grid grid-cols-2 gap-4 mt-4">
            <div className="rounded-lg border border-line p-4"><p className="eyebrow">Wariant A</p><p className="kpi text-h3 text-granat-800">97%</p></div>
            <div className="rounded-lg border border-zloto-300 bg-zloto-50 p-4"><p className="eyebrow">Wariant B</p><p className="kpi text-h3 text-zloto-700">98%</p></div>
          </div>
        </CardBody></Card>
      )}

      {tab === 'metrics' && (
        <Card><CardBody>
          <span className="eyebrow">Metryki 30 dni</span>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-3">
            <div><p className="eyebrow">Rozmowy</p><p className="kpi text-h3 text-granat-800">{agent.calls30d.toLocaleString('pl-PL')}</p></div>
            <div><p className="eyebrow">Skuteczność</p><p className="kpi text-h3 text-sem-green">{agent.successRate}%</p></div>
            <div><p className="eyebrow">Śr. czas</p><p className="kpi text-h3 text-granat-800">3:12</p></div>
            <div><p className="eyebrow">Eskalacje</p><p className="kpi text-h3 text-zloto-700">1.2%</p></div>
          </div>
        </CardBody></Card>
      )}

      {tab === 'deploy' && (
        <Card><CardBody>
          <span className="eyebrow">Wdrożenie</span>
          <p className="text-body text-ink-500 mt-2">Wersja produkcyjna: <b>v7.4.2</b> · ostatni deploy 3 dni temu.</p>
          <div className="flex gap-2 mt-4">
            <Button variant="primary">Wdróż wersję</Button>
            <Button variant="secondary">Rollback</Button>
          </div>
        </CardBody></Card>
      )}
    </>
  )
}
