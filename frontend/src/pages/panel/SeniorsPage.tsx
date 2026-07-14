import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search } from 'lucide-react'
import type { Senior, SemaphoreLevel } from '@/types/domain'
import { api } from '@/lib/api/client'
import { PageHead } from '@/components/panel/PageHead'
import { SeniorCard } from '@/components/senior'
import { SemaphoreBadge } from '@/components/ui'
import { cn } from '@/lib/cn'

const FILTERS: { id: SemaphoreLevel | 'all'; label: string }[] = [
  { id: 'all', label: 'Wszyscy' },
  { id: 'red', label: 'Czerwony' },
  { id: 'purple', label: 'Fioletowy' },
  { id: 'yellow', label: 'Żółty' },
  { id: 'green', label: 'Zielony' },
]

export function SeniorsPage() {
  const navigate = useNavigate()
  const [seniors, setSeniors] = useState<Senior[]>([])
  const [filter, setFilter] = useState<SemaphoreLevel | 'all'>('all')
  const [query, setQuery] = useState('')

  useEffect(() => {
    api.getMySeniors().then((r) => setSeniors(r.seniors))
  }, [])

  const filtered = useMemo(
    () =>
      seniors.filter(
        (s) =>
          (filter === 'all' || s.semaphore === filter) &&
          (!query || `${s.firstName} ${s.lastName} ${s.id}`.toLowerCase().includes(query.toLowerCase())),
      ),
    [seniors, filter, query],
  )

  return (
    <>
      <PageHead eyebrow="Podopieczni" title="Moi bliscy" subtitle={`${seniors.length} osób pod opieką Adama`} />

      <div className="flex flex-col sm:flex-row gap-3 mb-5">
        <div className="flex items-center gap-2 bg-white border border-line rounded-md px-3 py-2 flex-1 max-w-sm">
          <Search size={16} className="text-ink-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Szukaj po imieniu lub ID…"
            className="bg-transparent outline-none text-body flex-1 text-ink-700"
          />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {FILTERS.map((f) => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={cn(
                'px-3 py-2 rounded-md text-label border transition-colors',
                filter === f.id ? 'bg-granat-700 text-white border-granat-700' : 'bg-white border-line text-ink-600 hover:border-line-strong',
              )}
            >
              {f.id !== 'all' ? (
                <SemaphoreBadge level={f.id} label={f.label} size="xs" />
              ) : (
                f.label
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {filtered.map((s) => (
          <SeniorCard key={s.id} senior={s} onClick={() => navigate(`/panel/senior/${s.id}`)} onCall={() => {}} />
        ))}
        {!filtered.length && <p className="text-body text-ink-400">Brak wyników.</p>}
      </div>
    </>
  )
}
