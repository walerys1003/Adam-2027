import { cn } from '@/lib/cn'

export interface HeatCell {
  date: string
  value: number // 0..1 lub status
  status?: 'ok' | 'partial' | 'missed' | 'none'
}

const STATUS_COLOR: Record<NonNullable<HeatCell['status']>, string> = {
  ok: 'bg-sem-green',
  partial: 'bg-zloto-400',
  missed: 'bg-sem-red',
  none: 'bg-paper-3',
}

/** Kalendarz-heatmap (np. adherence 30d = 7 kolumn × N tygodni). */
export function Heatmap({
  cells,
  columns = 7,
  className,
  legend = true,
}: {
  cells: HeatCell[]
  columns?: number
  className?: string
  legend?: boolean
}) {
  return (
    <div className={className}>
      <div className="grid gap-1.5" style={{ gridTemplateColumns: `repeat(${columns}, minmax(0,1fr))` }}>
        {cells.map((c, i) => (
          <div
            key={i}
            title={`${c.date}`}
            className={cn(
              'aspect-square rounded-sm',
              c.status ? STATUS_COLOR[c.status] : 'bg-sem-green',
            )}
            style={c.status ? undefined : { opacity: 0.25 + c.value * 0.75 }}
          />
        ))}
      </div>
      {legend && (
        <div className="flex items-center gap-4 mt-3 text-caption text-ink-500">
          <span className="inline-flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-sem-green" /> OK</span>
          <span className="inline-flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-zloto-400" /> Częściowo</span>
          <span className="inline-flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-sem-red" /> Pominięte</span>
        </div>
      )}
    </div>
  )
}
