import { cn } from '@/lib/cn'

export interface RadialGaugeProps {
  /** 0–100 */
  value: number
  size?: number
  strokeWidth?: number
  label?: string
  sublabel?: string
  color?: string
  className?: string
}

/** Circular progress gauge — used for adherence / mood %. */
export function RadialGauge({
  value,
  size = 96,
  strokeWidth = 8,
  label,
  sublabel,
  color,
  className,
}: RadialGaugeProps) {
  const clamped = Math.max(0, Math.min(100, value))
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (clamped / 100) * circumference

  // Auto-color by value if not provided
  const strokeColor =
    color ??
    (clamped >= 85 ? 'var(--sem-green)' : clamped >= 60 ? 'var(--zloto-500)' : 'var(--sem-red)')

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--paper-3)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-slow ease-adam-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="kpi text-h4 text-granat-800">{label ?? `${Math.round(clamped)}%`}</span>
        {sublabel && <span className="text-caption text-ink-500">{sublabel}</span>}
      </div>
    </div>
  )
}
