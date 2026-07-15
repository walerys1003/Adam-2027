import { cn } from '@/lib/cn'
import type { SemaphoreLevel } from '@/types/domain'

/* ============================================================
   <SemaphoreBadge /> — sygnatura Adama.
   Reguła KRYTYCZNA: pulsuje TYLKO red i purple.
   Green/Yellow są ambient (statyczne).
   ============================================================ */

export interface SemaphoreBadgeProps {
  level: SemaphoreLevel
  label?: string
  size?: 'xs' | 'sm' | 'md' | 'lg'
  showLabel?: boolean
  ariaLive?: 'off' | 'polite' | 'assertive'
  className?: string
}

const LEVEL_META: Record<
  SemaphoreLevel,
  { dot: string; text: string; bg: string; ring: string; defaultLabel: string; pulse: boolean }
> = {
  green: {
    dot: 'bg-sem-green',
    text: 'text-sem-green',
    bg: 'bg-sem-green-bg',
    ring: 'bg-sem-green',
    defaultLabel: 'Wszystko OK',
    pulse: false,
  },
  yellow: {
    dot: 'bg-sem-yellow',
    text: 'text-sem-yellow',
    bg: 'bg-sem-yellow-bg',
    ring: 'bg-sem-yellow',
    defaultLabel: 'Uwaga',
    pulse: false,
  },
  red: {
    dot: 'bg-sem-red',
    text: 'text-sem-red',
    bg: 'bg-sem-red-bg',
    ring: 'bg-sem-red',
    defaultLabel: 'Alarm',
    pulse: true,
  },
  purple: {
    dot: 'bg-sem-purple',
    text: 'text-sem-purple',
    bg: 'bg-sem-purple-bg',
    ring: 'bg-sem-purple',
    defaultLabel: 'Zagrożenie życia',
    pulse: true,
  },
}

const SIZE_META = {
  xs: { dot: 'w-1.5 h-1.5', text: 'text-caption', gap: 'gap-1.5', pad: 'px-2 py-0.5' },
  sm: { dot: 'w-2 h-2', text: 'text-label', gap: 'gap-2', pad: 'px-2.5 py-1' },
  md: { dot: 'w-2.5 h-2.5', text: 'text-body', gap: 'gap-2', pad: 'px-3 py-1.5' },
  lg: { dot: 'w-3 h-3', text: 'text-body-l', gap: 'gap-2.5', pad: 'px-4 py-2' },
}

export function SemaphoreBadge({
  level,
  label,
  size = 'md',
  showLabel = true,
  ariaLive,
  className,
}: SemaphoreBadgeProps) {
  const meta = LEVEL_META[level]
  const sz = SIZE_META[size]
  const text = label ?? meta.defaultLabel
  const live = ariaLive ?? (level === 'red' || level === 'purple' ? 'assertive' : level === 'yellow' ? 'polite' : 'off')

  return (
    <span
      role="status"
      aria-live={live}
      // WCAG 1.4.1 — poziom nie może być przekazywany wyłącznie kolorem:
      // gdy etykieta jest ukryta wizualnie, udostępniamy ją czytnikom ekranu.
      aria-label={showLabel ? undefined : `Semafor: ${text}`}
      className={cn(
        'inline-flex items-center rounded-full font-medium',
        sz.gap,
        sz.pad,
        sz.text,
        meta.bg,
        meta.text,
        className,
      )}
    >
      <span className="relative inline-flex">
        {meta.pulse && (
          <span
            className={cn('absolute inline-flex rounded-full opacity-70', sz.dot, meta.ring, 'animate-sem-pulse-ring')}
            aria-hidden="true"
          />
        )}
        <span
          className={cn(
            'relative inline-flex rounded-full',
            sz.dot,
            meta.dot,
            meta.pulse && 'animate-sem-dot-pulse',
          )}
          aria-hidden="true"
        />
      </span>
      {showLabel && <span className="whitespace-nowrap">{text}</span>}
    </span>
  )
}
