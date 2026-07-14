import { cn } from '@/lib/cn'

export interface SparklineProps {
  data: number[] // 0.0–1.0
  width?: number
  height?: number
  color?: string
  className?: string
}

/** Minimal inline sparkline for mood trend (7d). */
export function Sparkline({ data, width = 96, height = 28, color, className }: SparklineProps) {
  if (data.length < 2) return null

  const max = Math.max(...data, 1)
  const min = Math.min(...data, 0)
  const range = max - min || 1

  const points = data
    .map((v, i) => {
      const x = (i / (data.length - 1)) * width
      const y = height - ((v - min) / range) * height
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')

  const last = data[data.length - 1]
  const stroke = color ?? (last >= 0.6 ? 'var(--sem-green)' : last >= 0.4 ? 'var(--zloto-500)' : 'var(--sem-red)')

  return (
    <svg width={width} height={height} className={cn('overflow-visible', className)}>
      <polyline points={points} fill="none" stroke={stroke} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      {/* last point dot */}
      <circle
        cx={width}
        cy={height - ((last - min) / range) * height}
        r={2.5}
        fill={stroke}
      />
    </svg>
  )
}
