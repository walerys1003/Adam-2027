import { useEffect, useState } from 'react'
import { Download, FileJson, Sparkles, TrendingUp } from 'lucide-react'
import type { MoodPoint } from '@/types/domain'
import { api } from '@/lib/api/client'
import { PageHead } from '@/components/panel/PageHead'
import { MoodChart } from '@/components/senior'
import { Card, CardBody, Button, Badge, Heatmap, Stat } from '@/components/ui'
import type { HeatCell } from '@/components/ui'

// 26 weeks × 7 days adherence heatmap
function buildHeat(): HeatCell[] {
  const cells: HeatCell[] = []
  const today = new Date()
  for (let i = 26 * 7 - 1; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const seed = (i * 13 + 41) % 100
    const status = seed > 82 ? 'ok' : seed > 45 ? (seed % 2 ? 'ok' : 'partial') : seed > 30 ? 'missed' : 'ok'
    cells.push({ date: d.toLocaleDateString('pl-PL'), value: seed / 100, status })
  }
  return cells
}

export function ReportsPage() {
  const [mood, setMood] = useState<{ data: MoodPoint[]; markers: any[] }>({ data: [], markers: [] })
  const heat = buildHeat()

  useEffect(() => {
    api.getMood('HW-01247', '90d').then(setMood)
  }, [])

  return (
    <>
      <PageHead eyebrow="Analityka" title="Raporty" subtitle="Trendy, raport miesięczny i eksport medyczny (FHIR)" />

      {/* KPI */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card className="p-5"><Stat label="Śr. nastrój 90d" value={68} unit="%" trend="up" trendLabel="+4" /></Card>
        <Card className="p-5"><Stat label="Adherencja 90d" value={91} unit="%" trend="flat" /></Card>
        <Card className="p-5"><Stat label="Rozmowy" value={174} icon={<TrendingUp size={14} />} /></Card>
        <Card className="p-5"><Stat label="Alerty" value={6} trend="down" trendLabel="-2" /></Card>
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        {/* Trend 90d */}
        <MoodChart data={mood.data} markers={mood.markers} range="90d" className="lg:col-span-2" />

        {/* Featured report */}
        <Card>
          <CardBody>
            <span className="eyebrow flex items-center gap-1.5"><Sparkles size={13} /> Wyróżniony</span>
            <h3 className="text-h4 font-serif text-granat-900 mt-1">Raport · Czerwiec 2026</h3>
            <p className="text-body text-ink-600 mt-2 leading-relaxed">
              Halina utrzymała stabilny nastrój (70%) i wysoką adherencję leków (93%).
              Odnotowano 2 alerty żółte (sen &lt; 6h). Rekomendacja: rozmowa o higienie snu.
            </p>
            <div className="mt-4 space-y-2">
              <Button variant="secondary" fullWidth><Download size={15} /> Pobierz PDF</Button>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Heatmap 26 weeks */}
      <Card className="mt-5">
        <CardBody>
          <span className="eyebrow">Adherencja · 26 tygodni</span>
          <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-4">Kalendarz przyjmowania leków</h3>
          <div className="overflow-x-auto">
            <div className="min-w-[520px]">
              <Heatmap cells={heat} columns={26} legend />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* FHIR export */}
      <Card className="mt-5">
        <CardBody>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="eyebrow flex items-center gap-1.5"><FileJson size={13} /> Interoperacyjność</span>
              <h3 className="text-h4 font-serif text-granat-900 mt-1">Eksport FHIR R4</h3>
              <p className="text-body text-ink-500 mt-1 max-w-xl">
                Dane zdrowotne w standardzie HL7 FHIR R4 (Observation, MedicationStatement) —
                do przekazania lekarzowi lub systemowi P1 (e-zdrowie).
              </p>
              <div className="flex gap-2 mt-2">
                <Badge tone="info">FHIR R4</Badge>
                <Badge tone="neutral">HL7</Badge>
                <Badge tone="neutral">P1 / e-zdrowie</Badge>
              </div>
            </div>
            <Button variant="gold" className="shrink-0"><Download size={15} /> Eksport FHIR (.json)</Button>
          </div>
        </CardBody>
      </Card>
    </>
  )
}
