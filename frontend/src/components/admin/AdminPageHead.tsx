import type { ReactNode } from 'react'
import { Search } from 'lucide-react'

export function AdminPageHead({
  eyebrow,
  title,
  subtitle,
  actions,
  search,
  onSearch,
  searchPlaceholder = 'Szukaj…',
}: {
  eyebrow?: string
  title: string
  subtitle?: string
  actions?: ReactNode
  search?: string
  onSearch?: (v: string) => void
  searchPlaceholder?: string
}) {
  return (
    <div className="mb-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          {eyebrow && <span className="eyebrow">{eyebrow}</span>}
          <h1 className="font-serif text-h3 text-granat-900 leading-tight">{title}</h1>
          {subtitle && <p className="text-body text-ink-500 mt-1">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {onSearch && (
            <div className="flex items-center gap-2 bg-white border border-line rounded-md px-3 py-2">
              <Search size={15} className="text-ink-400" />
              <input
                value={search}
                onChange={(e) => onSearch(e.target.value)}
                placeholder={searchPlaceholder}
                className="bg-transparent outline-none text-label w-40 text-ink-700"
              />
            </div>
          )}
          {actions}
        </div>
      </div>
    </div>
  )
}
