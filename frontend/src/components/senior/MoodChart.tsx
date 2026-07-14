import { useMemo } from 'react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ReferenceDot,
  CartesianGrid,
} from 'recharts'
import { cn } from '@/lib/cn'
import type { MoodPoint, AlertMarker, SemaphoreLevel } from '@/types/domain'

export interface MoodChartProps {
  data: MoodPoint[]
  range?: '7d' | '14d' | '30d' | '90d'
  showThresholds?: boolean
  markers?: AlertMarker[]
  onRangeChange?: (range: string) => void
  className?: string
}

const RANGES: Array<'7d' | '14d' | '30d' | '90d'> = ['7d', '14d', '30d', '90d']

const MARKER_COLOR: Record<SemaphoreLevel, string> = {
  green: 'var(--sem-green)',
  yellow: 'var(--sem-yellow)',
  red: 'var(--sem-red)',
  purple: 'var(--sem-purple)',
}

function fmtDay(iso: string): string {
  const d = new Date(iso)
  return `${d.getDate()}.${d.getMonth() + 1}`
}

export function MoodChart({
  data,
  range = '30d',
  showThresholds = true,
  markers = [],
  onRangeChange,
  className,
}: MoodChartProps) {
  const chartData = useMemo(
    () => data.map((p) => ({ ...p, day: fmtDay(p.timestamp), value: Number(p.value.toFixed(2)) })),
    [data],
  )

  return (
    <div className={cn('adam-card p-5', className)}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="eyebrow">Nastrój</span>
          <h3 className="text-h4 font-serif text-granat-900">Trend nastroju</h3>
        </div>
        <div className="flex gap-1 bg-paper-2 rounded-md p-1">
          {RANGES.map((r) => (
            <button
              key={r}
              onClick={() => onRangeChange?.(r)}
              className={cn(
                'px-2.5 py-1 text-label rounded-sm transition-colors',
                r === range ? 'bg-white text-granat-800 shadow-e1' : 'text-ink-500 hover:text-granat-700',
              )}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={chartData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="moodGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--zloto-400)" stopOpacity={0.35} />
              <stop offset="100%" stopColor="var(--zloto-400)" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" vertical={false} />
          <XAxis dataKey="day" tick={{ fontSize: 11, fill: 'var(--ink-500)' }} axisLine={false} tickLine={false} />
          <YAxis domain={[0, 1]} tick={{ fontSize: 11, fill: 'var(--ink-500)' }} axisLine={false} tickLine={false} />

          {showThresholds && (
            <>
              <ReferenceLine y={0.5} stroke="var(--sem-yellow)" strokeDasharray="4 4" strokeOpacity={0.6} />
              <ReferenceLine y={0.3} stroke="var(--sem-red)" strokeDasharray="4 4" strokeOpacity={0.6} />
            </>
          )}

          <Tooltip
            contentStyle={{
              background: '#fff',
              border: '1px solid var(--line)',
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(v: number) => [`${(v * 100).toFixed(0)}%`, 'Nastrój']}
          />

          <Area
            type="monotone"
            dataKey="value"
            stroke="var(--zloto-600)"
            strokeWidth={2}
            fill="url(#moodGradient)"
          />

          {markers.map((m, i) => {
            const point = chartData.find((p) => p.timestamp === m.timestamp)
            if (!point) return null
            return (
              <ReferenceDot
                key={i}
                x={point.day}
                y={point.value}
                r={5}
                fill={MARKER_COLOR[m.level]}
                stroke="#fff"
                strokeWidth={2}
              />
            )
          })}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
