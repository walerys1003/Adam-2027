import { useMemo, useState } from 'react'
import { Eye, EyeOff, KeyRound, Pencil, ShieldAlert } from 'lucide-react'
import { AdminPageHead, DataTable } from '@/components/admin'
import type { Column } from '@/components/admin'
import { Badge } from '@/components/ui'
import { ENV_VARS, ENV_CATEGORIES } from '@/data/mockAdmin'
import type { EnvVar } from '@/data/mockAdmin'
import { cn } from '@/lib/cn'

export function AdminEnvironment() {
  const [cat, setCat] = useState('Wszystkie')
  const [q, setQ] = useState('')
  const [revealed, setRevealed] = useState<Record<string, boolean>>({})

  const rows = useMemo(
    () =>
      ENV_VARS.filter(
        (v) => (cat === 'Wszystkie' || v.category === cat) && (!q || v.key.toLowerCase().includes(q.toLowerCase())),
      ).map((v) => ({ ...v, id: v.key })),
    [cat, q],
  )

  const cols: Column<EnvVar & { id: string }>[] = [
    {
      key: 'key',
      header: 'Zmienna',
      render: (r) => (
        <span className="flex items-center gap-2">
          {r.secret && <KeyRound size={13} className="text-zloto-600" />}
          <span className="font-mono text-caption text-granat-900">{r.key}</span>
        </span>
      ),
    },
    {
      key: 'value',
      header: 'Wartość',
      render: (r) => (
        <span className="flex items-center gap-2">
          <span className="font-mono text-caption text-ink-700">
            {r.secret && !revealed[r.key] ? '••••••••••••' : r.value}
          </span>
          {r.secret && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                setRevealed((s) => ({ ...s, [r.key]: !s[r.key] }))
              }}
              className="text-ink-400 hover:text-granat-700"
            >
              {revealed[r.key] ? <EyeOff size={13} /> : <Eye size={13} />}
            </button>
          )}
        </span>
      ),
    },
    { key: 'category', header: 'Kategoria', render: (r) => <Badge tone="neutral">{r.category}</Badge> },
    {
      key: 'modified',
      header: '',
      align: 'right',
      render: (r) =>
        r.modified ? (
          <Badge tone="gold">
            <Pencil size={10} className="mr-1 inline" /> zmieniona
          </Badge>
        ) : null,
    },
  ]

  return (
    <>
      <AdminPageHead
        eyebrow="System"
        title="Zmienne środowiskowe"
        subtitle="78 zmiennych · sekrety maskowane, edycja audytowana"
        search={q}
        onSearch={setQ}
        searchPlaceholder="Szukaj zmiennej…"
      />

      <div className="mb-5 flex items-start gap-2 rounded-md bg-sem-red-bg border border-sem-red/20 p-3">
        <ShieldAlert size={16} className="text-sem-red mt-0.5 shrink-0" />
        <p className="text-caption text-ink-700">
          Zmiany sekretów wymagają 2FA i są zapisywane w dzienniku audytu (RODO). Nigdy nie ujawniaj kluczy poza tym panelem.
        </p>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {ENV_CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => setCat(c)}
            className={cn(
              'rounded-full border px-3 py-1 text-label transition-colors',
              cat === c
                ? 'bg-granat-700 text-white border-granat-700'
                : 'bg-white text-ink-500 border-line hover:border-line-strong',
            )}
          >
            {c}
          </button>
        ))}
      </div>

      <DataTable columns={cols} rows={rows} />
    </>
  )
}
