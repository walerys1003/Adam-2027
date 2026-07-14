import { Pill, Clock, Info } from 'lucide-react'
import { cn } from '@/lib/cn'
import type { Medication } from '@/types/domain'
import { RadialGauge } from '@/components/ui/RadialGauge'

export interface MedicationListProps {
  medications: Medication[]
  variant?: 'summary' | 'schedule' | 'calendar'
  className?: string
}

function adherenceTone(v: number) {
  if (v >= 85) return 'text-sem-green'
  if (v >= 60) return 'text-zloto-700'
  return 'text-sem-red'
}

export function MedicationList({ medications, variant = 'summary', className }: MedicationListProps) {
  if (variant === 'summary') {
    const avg = medications.length
      ? Math.round(medications.reduce((s, m) => s + m.adherence30d, 0) / medications.length)
      : 0
    return (
      <div className={cn('adam-card p-5 flex items-center gap-5', className)}>
        <RadialGauge value={avg} size={88} sublabel="30 dni" />
        <div>
          <span className="eyebrow">Leki</span>
          <h3 className="text-h4 font-serif text-granat-900">Przyjmowanie leków</h3>
          <p className="text-label text-ink-500 mt-1">
            {medications.length} {medications.length === 1 ? 'lek' : 'leki/leków'} · średnia adherencja {avg}%
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className={cn('adam-card divide-y divide-line', className)}>
      <div className="px-5 py-4">
        <span className="eyebrow">Leki</span>
        <h3 className="text-h4 font-serif text-granat-900">Harmonogram leków</h3>
      </div>
      {medications.map((med) => (
        <div key={med.id} className="px-5 py-4 flex items-start gap-4">
          <div className="mt-0.5 w-9 h-9 rounded-md bg-granat-50 text-granat-700 flex items-center justify-center shrink-0">
            <Pill size={18} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <h4 className="text-body font-medium text-granat-900">{med.name}</h4>
              <span className={cn('kpi text-h4', adherenceTone(med.adherence30d))}>{med.adherence30d}%</span>
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1 text-label text-ink-500">
              <span className="inline-flex items-center gap-1">
                <Clock size={12} /> {med.scheduleTimes.join(' · ')}
              </span>
              <span>{med.frequency}</span>
            </div>
            {med.notes && (
              <p className="inline-flex items-start gap-1 mt-1.5 text-label text-ink-400">
                <Info size={12} className="mt-0.5 shrink-0" /> {med.notes}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
