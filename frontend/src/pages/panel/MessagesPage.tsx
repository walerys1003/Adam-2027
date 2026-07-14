import { useEffect, useMemo, useState } from 'react'
import { Send, AlertTriangle, FileText, UserCog, Bell, Search } from 'lucide-react'
import type { Thread } from '@/types/domain'
import { api } from '@/lib/api/client'
import { PageHead } from '@/components/panel/PageHead'
import { Avatar, Button, Badge } from '@/components/ui'
import { cn } from '@/lib/cn'

type Filter = 'all' | 'alert' | 'report' | 'coordinator' | 'system'

const FILTERS: { id: Filter; label: string; icon: any }[] = [
  { id: 'all', label: 'Wszystkie', icon: Bell },
  { id: 'alert', label: 'Alerty', icon: AlertTriangle },
  { id: 'report', label: 'Raporty', icon: FileText },
  { id: 'coordinator', label: 'Koordynator', icon: UserCog },
  { id: 'system', label: 'System', icon: Bell },
]

const CAT_TONE: Record<Thread['category'], 'red' | 'info' | 'granat' | 'neutral'> = {
  alert: 'red',
  report: 'info',
  coordinator: 'granat',
  system: 'neutral',
}

function fmtTime(iso: string) {
  const diff = Date.now() - new Date(iso).getTime()
  if (diff < 3600_000) return `${Math.floor(diff / 60000)} min`
  if (diff < 86400_000) return `${Math.floor(diff / 3600000)} godz.`
  return new Date(iso).toLocaleDateString('pl-PL', { day: 'numeric', month: 'short' })
}

export function MessagesPage() {
  const [threads, setThreads] = useState<Thread[]>([])
  const [filter, setFilter] = useState<Filter>('all')
  const [activeId, setActiveId] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [draft, setDraft] = useState('')

  useEffect(() => {
    api.listThreads().then((t) => {
      setThreads(t)
      setActiveId(t[0]?.id ?? null)
    })
  }, [])

  const filtered = useMemo(
    () =>
      threads.filter(
        (t) =>
          (filter === 'all' || t.category === filter) &&
          (!query || t.subject.toLowerCase().includes(query.toLowerCase())),
      ),
    [threads, filter, query],
  )

  const active = threads.find((t) => t.id === activeId) ?? null

  const send = async () => {
    if (!draft.trim() || !active) return
    const updated = await api.sendMessage(active.id, draft.trim())
    setThreads((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
    setDraft('')
  }

  return (
    <>
      <PageHead eyebrow="Komunikacja" title="Wiadomości" subtitle="Alerty, raporty i kontakt z koordynatorem" />

      <div className="adam-card overflow-hidden grid lg:grid-cols-[220px_320px_1fr] min-h-[560px]">
        {/* Col 1 — filters */}
        <div className="border-r border-line p-3 space-y-1 hidden lg:block">
          {FILTERS.map((f) => {
            const Icon = f.icon
            const count = threads.filter((t) => (f.id === 'all' ? true : t.category === f.id)).reduce((s, t) => s + t.unread, 0)
            return (
              <button
                key={f.id}
                onClick={() => setFilter(f.id)}
                className={cn(
                  'w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-label transition-colors',
                  filter === f.id ? 'bg-granat-700 text-white' : 'text-ink-700 hover:bg-granat-50',
                )}
              >
                <Icon size={16} />
                <span className="flex-1 text-left">{f.label}</span>
                {count > 0 && (
                  <span className="text-caption rounded-full bg-zloto-500 text-granat-900 px-1.5">{count}</span>
                )}
              </button>
            )
          })}
        </div>

        {/* Col 2 — thread list */}
        <div className="border-r border-line flex flex-col">
          <div className="p-3 border-b border-line">
            <div className="flex items-center gap-2 bg-paper-2 rounded-md px-3 py-2">
              <Search size={15} className="text-ink-400" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Szukaj…"
                className="bg-transparent outline-none text-label flex-1 text-ink-700"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto divide-y divide-line">
            {filtered.map((t) => (
              <button
                key={t.id}
                onClick={() => setActiveId(t.id)}
                className={cn(
                  'w-full text-left px-4 py-3 transition-colors',
                  activeId === t.id ? 'bg-zloto-50/50' : 'hover:bg-paper-2',
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <Badge tone={CAT_TONE[t.category]}>{t.category}</Badge>
                  <span className="text-caption text-ink-400">{fmtTime(t.lastMessageAt)}</span>
                </div>
                <p className={cn('text-body mt-1 line-clamp-2', t.unread ? 'font-medium text-granat-900' : 'text-ink-700')}>
                  {t.subject}
                </p>
                {t.unread > 0 && <span className="inline-block mt-1 w-2 h-2 rounded-full bg-zloto-500" />}
              </button>
            ))}
            {!filtered.length && <p className="p-4 text-label text-ink-400">Brak wiadomości.</p>}
          </div>
        </div>

        {/* Col 3 — thread view */}
        <div className="flex flex-col min-h-[400px]">
          {active ? (
            <>
              <div className="px-5 py-4 border-b border-line">
                <h3 className="text-body font-medium text-granat-900">{active.subject}</h3>
                {active.seniorName && <p className="text-caption text-ink-500">{active.seniorName}</p>}
              </div>
              <div className="flex-1 overflow-y-auto p-5 space-y-4">
                {active.messages.map((m) => {
                  const mine = m.from === 'me'
                  return (
                    <div key={m.id} className={cn('flex gap-3', mine && 'flex-row-reverse')}>
                      <Avatar firstName={m.authorName.split(' ')[0] ?? 'A'} lastName={m.authorName.split(' ')[1] ?? ''} size="sm" />
                      <div className={cn('max-w-[75%]', mine && 'text-right')}>
                        <div className="flex items-center gap-2 text-caption text-ink-400" >
                          <span className="font-medium text-ink-600">{m.authorName}</span>
                          <span>{fmtTime(m.timestamp)}</span>
                        </div>
                        <div
                          className={cn(
                            'mt-1 rounded-lg px-3.5 py-2.5 text-body inline-block text-left',
                            mine ? 'bg-granat-700 text-white' : 'bg-paper-2 text-ink-700',
                          )}
                        >
                          {m.body}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
              <div className="p-3 border-t border-line flex items-center gap-2">
                <input
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && send()}
                  placeholder="Napisz wiadomość…"
                  className="flex-1 bg-paper-2 rounded-md px-3.5 py-2.5 text-body outline-none text-ink-700"
                />
                <Button onClick={send} disabled={!draft.trim()}>
                  <Send size={16} />
                </Button>
              </div>
            </>
          ) : (
            <div className="flex-1 grid place-items-center text-ink-400 text-body">Wybierz wątek</div>
          )}
        </div>
      </div>
    </>
  )
}
