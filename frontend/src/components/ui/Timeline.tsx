import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import type { SemaphoreLevel } from '@/types/domain'

export interface TimelineItem {
  id: string
  title: string
  time: string
  description?: ReactNode
  level?: SemaphoreLevel
  icon?: ReactNode
}

const DOT: Record<SemaphoreLevel, string> = {
  green: 'bg-sem-green',
  yellow: 'bg-sem-yellow',
  red: 'bg-sem-red',
  purple: 'bg-sem-purple',
}

/** Pionowa oś czasu — alerty, zdarzenia, historia. */
export function Timeline({ items, className }: { items: TimelineItem[]; className?: string }) {
  if (!items.length) {
    return <p className={cn('text-body text-ink-400 py-6 text-center', className)}>Brak zdarzeń.</p>
  }
  return (
    <ol className={cn('relative', className)}>
      {items.map((it, i) => {
        const pulse = it.level === 'red' || it.level === 'purple'
        return (
          <li key={it.id} className="relative flex gap-4 pb-6 last:pb-0">
            {/* line */}
            {i < items.length - 1 && (
              <span className="absolute left-[7px] top-4 bottom-0 w-px bg-line" aria-hidden />
            )}
            {/* dot */}
            <span
              className={cn(
                'relative mt-1 w-3.5 h-3.5 rounded-full shrink-0 ring-4 ring-paper',
                it.level ? DOT[it.level] : 'bg-granat-300',
                pulse && 'animate-sem-dot-pulse',
              )}
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <h4 className="text-body font-medium text-granat-900 flex items-center gap-2">
                  {it.icon}
                  {it.title}
                </h4>
                <time className="text-caption text-ink-400 shrink-0">{it.time}</time>
              </div>
              {it.description && (
                <div className="text-label text-ink-500 mt-0.5">{it.description}</div>
              )}
            </div>
          </li>
        )
      })}
    </ol>
  )
}
