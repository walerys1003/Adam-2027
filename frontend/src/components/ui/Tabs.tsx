import { cn } from '@/lib/cn'

export interface TabItem {
  id: string
  label: string
  count?: number
}

export function Tabs({
  items,
  value,
  onChange,
  className,
}: {
  items: TabItem[]
  value: string
  onChange: (id: string) => void
  className?: string
}) {
  return (
    <div className={cn('border-b border-line overflow-x-auto', className)}>
      <div className="flex gap-1 min-w-max" role="tablist">
        {items.map((t) => {
          const active = t.id === value
          return (
            <button
              key={t.id}
              role="tab"
              aria-selected={active}
              onClick={() => onChange(t.id)}
              className={cn(
                'relative px-4 py-3 text-body whitespace-nowrap transition-colors',
                active ? 'text-granat-900 font-medium' : 'text-ink-500 hover:text-granat-700',
              )}
            >
              {t.label}
              {t.count != null && (
                <span
                  className={cn(
                    'ml-2 text-caption rounded-full px-1.5 py-0.5',
                    active ? 'bg-granat-700 text-white' : 'bg-paper-3 text-ink-500',
                  )}
                >
                  {t.count}
                </span>
              )}
              {active && <span className="absolute bottom-0 inset-x-0 h-0.5 bg-zloto-500 rounded-full" />}
            </button>
          )
        })}
      </div>
    </div>
  )
}
