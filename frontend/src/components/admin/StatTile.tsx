import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

export function StatTile({
  label,
  value,
  unit,
  icon,
  trend,
  trendLabel,
  accent = 'granat',
  className,
}: {
  label: string
  value: ReactNode
  unit?: string
  icon?: ReactNode
  trend?: 'up' | 'down' | 'flat'
  trendLabel?: string
  accent?: 'granat' | 'gold' | 'green' | 'red' | 'purple'
  className?: string
}) {
  const ACCENT: Record<string, string> = {
    granat: 'text-granat-700 bg-granat-50',
    gold: 'text-zloto-700 bg-zloto-50',
    green: 'text-sem-green bg-sem-green-bg',
    red: 'text-sem-red bg-sem-red-bg',
    purple: 'text-sem-purple bg-sem-purple-bg',
  }
  const TREND: Record<string, string> = {
    up: 'text-sem-green',
    down: 'text-sem-red',
    flat: 'text-ink-400',
  }
  const SYM: Record<string, string> = { up: '↑', down: '↓', flat: '→' }

  return (
    <div className={cn('adam-card p-4 flex items-start gap-3', className)}>
      {icon && (
        <span className={cn('w-9 h-9 rounded-md flex items-center justify-center shrink-0', ACCENT[accent])}>
          {icon}
        </span>
      )}
      <div className="min-w-0">
        <p className="eyebrow">{label}</p>
        <div className="flex items-baseline gap-1.5 mt-0.5">
          <span className="kpi text-h3 text-granat-800">{value}</span>
          {unit && <span className="text-body text-ink-500">{unit}</span>}
        </div>
        {trend && (
          <span className={cn('text-label flex items-center gap-1 mt-0.5', TREND[trend])}>
            {SYM[trend]} {trendLabel}
          </span>
        )}
      </div>
    </div>
  )
}
