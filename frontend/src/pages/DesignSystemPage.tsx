import { useState } from 'react'
import { Phone, Bell, Shield, Activity } from 'lucide-react'
import {
  SemaphoreBadge,
  Button,
  Card,
  Badge,
  PackageBadge,
  Avatar,
  Stat,
  RadialGauge,
  Sparkline,
} from '@/components/ui'
import { SeniorCard, MoodChart, MedicationList, WearableWidget } from '@/components/senior'
import {
  MOCK_SENIORS,
  MOCK_SENIOR_DETAIL,
  MOCK_MOOD_30D,
  MOCK_MOOD_MARKERS,
} from '@/data/mockSeniors'
import type { SemaphoreLevel } from '@/types/domain'

function Section({ id, title, eyebrow, children }: { id: string; title: string; eyebrow: string; children: React.ReactNode }) {
  return (
    <section id={id} className="scroll-mt-24">
      <div className="mb-6">
        <span className="eyebrow">{eyebrow}</span>
        <h2 className="text-h2 font-serif text-granat-900">{title}</h2>
      </div>
      {children}
    </section>
  )
}

const LEVELS: SemaphoreLevel[] = ['green', 'yellow', 'red', 'purple']

export function DesignSystemPage() {
  const [range, setRange] = useState<'7d' | '14d' | '30d' | '90d'>('30d')

  return (
    <div className="min-h-screen bg-paper">
      {/* Top bar */}
      <header id="ds-header" className="sticky top-0 z-20 bg-paper/90 backdrop-blur border-b border-line">
        <div className="container flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-md bg-granat-700 text-zloto-400 flex items-center justify-center font-serif text-h4">
              A
            </div>
            <div className="leading-tight">
              <p className="font-serif text-h4 text-granat-900">Adam</p>
              <p className="text-caption text-ink-500">Design System · v1.0</p>
            </div>
          </div>
          <Badge tone="gold">SilverTech · Poznań</Badge>
        </div>
      </header>

      <main className="container py-12 space-y-16">
        {/* Intro */}
        <section id="ds-intro" className="max-w-3xl">
          <span className="eyebrow">Nordic humanism × Medical-premium</span>
          <h1 className="text-display font-serif text-granat-900 leading-tight mt-2">
            Cyfrowy <em className="text-italic-accent">opiekun</em> seniora
          </h1>
          <p className="text-body-l text-ink-700 mt-4">
            Biblioteka komponentów Adama — granat, matowe złoto i 4-poziomowy semafor.
            Wszystko zbudowane na tokenach z <code className="font-mono text-label">tokens.css</code>.
          </p>
        </section>

        {/* Colors */}
        <Section id="ds-colors" eyebrow="Fundament" title="Paleta">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: 'Granat 700', var: 'var(--granat-700)', hex: '#1a2744', text: 'text-white' },
              { name: 'Złoto 500', var: 'var(--zloto-500)', hex: '#c8963e', text: 'text-granat-900' },
              { name: 'Paper', var: 'var(--paper)', hex: '#fbfaf7', text: 'text-granat-900' },
              { name: 'Ink 900', var: 'var(--ink-900)', hex: '#0e1a2e', text: 'text-white' },
            ].map((c) => (
              <div key={c.name} className="rounded-lg overflow-hidden border border-line shadow-e1">
                <div className="h-24 flex items-end p-3" style={{ background: c.var }}>
                  <span className={`text-label font-medium ${c.text}`}>{c.name}</span>
                </div>
                <div className="px-3 py-2 bg-white font-mono text-caption text-ink-500">{c.hex}</div>
              </div>
            ))}
          </div>
        </Section>

        {/* Semaphore */}
        <Section id="ds-semaphore" eyebrow="Sygnatura" title="Semafor 4-poziomowy">
          <Card className="p-6">
            <p className="text-body text-ink-700 mb-4">
              Pulsowanie <strong>tylko</strong> dla <span className="text-sem-red">red</span> i{' '}
              <span className="text-sem-purple">purple</span>. Green/Yellow są statyczne (ambient).
            </p>
            <div className="flex flex-wrap gap-3">
              {LEVELS.map((l) => (
                <SemaphoreBadge key={l} level={l} size="md" />
              ))}
            </div>
            <div className="flex flex-wrap gap-3 mt-4">
              {(['xs', 'sm', 'md', 'lg'] as const).map((s) => (
                <SemaphoreBadge key={s} level="red" size={s} label={`Alarm ${s}`} />
              ))}
            </div>
          </Card>
        </Section>

        {/* Buttons */}
        <Section id="ds-buttons" eyebrow="Akcje" title="Przyciski">
          <Card className="p-6 flex flex-wrap items-center gap-3">
            <Button variant="primary"><Phone size={16} /> Zadzwoń teraz</Button>
            <Button variant="secondary"><Bell size={16} /> Powiadom rodzinę</Button>
            <Button variant="gold"><Shield size={16} /> Premium</Button>
            <Button variant="danger"><Activity size={16} /> Eskaluj alarm</Button>
            <Button variant="ghost">Anuluj</Button>
          </Card>
        </Section>

        {/* Data viz primitives */}
        <Section id="ds-dataviz" eyebrow="Dane" title="Wizualizacje">
          <div className="grid md:grid-cols-3 gap-4">
            <Card className="p-6 flex items-center justify-center">
              <RadialGauge value={94} sublabel="adherencja" />
            </Card>
            <Card className="p-6 flex flex-col items-center justify-center gap-3">
              <span className="eyebrow">Nastrój 7d</span>
              <Sparkline data={[0.7, 0.65, 0.6, 0.5, 0.55, 0.48, 0.46]} width={160} height={48} />
            </Card>
            <Card className="p-6 flex items-center justify-around">
              <Stat label="Rozmowy" value="58" trend="up" trendLabel="+6" />
              <Stat label="Alarmy" value="2" trend="down" trendLabel="-1" />
            </Card>
          </div>
        </Section>

        {/* Avatars + badges */}
        <Section id="ds-avatars" eyebrow="Tożsamość" title="Awatary i etykiety">
          <Card className="p-6 flex flex-wrap items-center gap-6">
            <Avatar firstName="Halina" lastName="Wiśniewska" size="xl" />
            <Avatar firstName="Marek" lastName="Nowak" size="lg" pulse="red" />
            <Avatar firstName="Tadeusz" lastName="Baran" size="lg" pulse="purple" />
            <div className="flex flex-col gap-2">
              <PackageBadge package="basic" />
              <PackageBadge package="family" />
              <PackageBadge package="premium" />
            </div>
          </Card>
        </Section>

        {/* Senior cards */}
        <Section id="ds-seniorcards" eyebrow="Panel Opiekuna" title="Karty seniorów">
          <div className="grid md:grid-cols-2 gap-4">
            {MOCK_SENIORS.map((s) => (
              <SeniorCard
                key={s.id}
                senior={s}
                onClick={() => {}}
                onCall={() => {}}
              />
            ))}
          </div>
        </Section>

        {/* Mood chart */}
        <Section id="ds-mood" eyebrow="Analityka" title="Wykres nastroju">
          <MoodChart
            data={MOCK_MOOD_30D}
            range={range}
            onRangeChange={(r) => setRange(r as typeof range)}
            markers={MOCK_MOOD_MARKERS}
          />
        </Section>

        {/* Medications + wearable */}
        <Section id="ds-med-wear" eyebrow="Zdrowie" title="Leki i wearable">
          <div className="grid lg:grid-cols-2 gap-4">
            <div className="space-y-4">
              <MedicationList medications={MOCK_SENIOR_DETAIL.meds} variant="summary" />
              <MedicationList medications={MOCK_SENIOR_DETAIL.meds} variant="schedule" />
            </div>
            <div className="space-y-4">
              {MOCK_SENIORS[0].wearable && (
                <WearableWidget device={MOCK_SENIORS[0].wearable} showLive readOnlyThresholds />
              )}
              {MOCK_SENIORS[1].wearable && (
                <WearableWidget device={MOCK_SENIORS[1].wearable} readOnlyThresholds />
              )}
            </div>
          </div>
        </Section>
      </main>

      <footer className="border-t border-line py-8">
        <div className="container text-caption text-ink-400 flex items-center justify-between">
          <span>Adam · SilverTech © 2026</span>
          <span className="font-mono">Design System v1.0 · Fraunces + Geist</span>
        </div>
      </footer>
    </div>
  )
}
