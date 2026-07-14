import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

export interface StatProps {
  label: string
  value: ReactNode
  unit?: string
  trend?: 'up' | 'down' | 'flat'
  trendLabel?: string
  icon?: ReactNode
  className?: string
}

const TREND_META = {
  up: { color: 'text-sem-green', symbol: '↑' },
  down: { color: 'text-sem-red', symbol: '↓' },
  flat: { color: 'text-ink-400', symbol: '→' },
}

/** KPI stat — numeral rendered in Fraunces (Adam signature). */
export function Stat({ label, value, unit, trend, trendLabel, icon, className }: StatProps) {
  return (
    <div className={cn('flex flex-col gap-1', className)}>
      <div className="flex items-center gap-2 text-ink-500 text-label">
        {icon}
        <span className="eyebrow">{label}</span>
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className="kpi text-h2 text-granat-800">{value}</span>
        {unit && <span className="text-body text-ink-500">{unit}</span>}
      </div>
      {trend && (
        <div className={cn('flex items-center gap-1 text-label', TREND_META[trend].color)}>
          <span>{TREND_META[trend].symbol}</span>
          {trendLabel && <span>{trendLabel}</span>}
        </div>
      )}
    </div>
  )
}
