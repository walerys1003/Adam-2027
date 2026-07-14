import { useMemo, useState } from 'react'
import { Play, Pause, Filter, Radio } from 'lucide-react'
import { AdminPageHead } from '@/components/admin'
import { cn } from '@/lib/cn'
import { LOG_LINES } from '@/data/mockAdmin'

const LEVELS = ['ALL', 'DEBUG', 'INFO', 'WARN', 'ERROR'] as const
const LEVEL_COLOR: Record<string, string> = {
  DEBUG: 'text-ink-400',
  INFO: 'text-sem-green',
  WARN: 'text-zloto-500',
  ERROR: 'text-sem-red',
}

export function AdminLogs() {
  const [level, setLevel] = useState<string>('ALL')
  const [live, setLive] = useState(true)

  const rows = useMemo(() => LOG_LINES.filter((l) => level === 'ALL' || l.level === level), [level])

  return (
    <>
      <AdminPageHead
        eyebrow="System"
        title="Dziennik na żywo"
        subtitle="Strumień logów agenta, telefonii i semafora"
        actions={
          <button
            onClick={() => setLive((v) => !v)}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-md border px-3 py-2 text-label font-medium transition-colors',
              live
                ? 'bg-sem-green-bg text-sem-green border-sem-green/20'
                : 'bg-white text-ink-500 border-line hover:border-line-strong',
            )}
          >
            {live ? <Pause size={14} /> : <Play size={14} />}
            {live ? 'Pauza' : 'Wznów'}
          </button>
        }
      />

      <div className="mb-4 flex items-center gap-2">
        <Filter size={14} className="text-ink-400" />
        {LEVELS.map((l) => (
          <button
            key={l}
            onClick={() => setLevel(l)}
            className={cn(
              'rounded-full border px-3 py-1 text-caption font-medium transition-colors',
              level === l
                ? 'bg-granat-700 text-white border-granat-700'
                : 'bg-white text-ink-500 border-line hover:border-line-strong',
            )}
          >
            {l}
          </button>
        ))}
      </div>

      <div className="rounded-lg border border-line bg-granat-950 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-2 border-b border-granat-800">
          <span className="flex items-center gap-2 text-caption text-granat-200 font-mono">
            <Radio size={12} className={live ? 'text-sem-green animate-sem-dot-pulse' : 'text-ink-400'} />
            adam-agent · stdout
          </span>
          <span className="text-caption text-granat-300 font-mono">{rows.length} linii</span>
        </div>
        <div className="p-4 font-mono text-caption leading-relaxed max-h-[60vh] overflow-y-auto">
          {rows.map((l, i) => (
            <div key={i} className="flex gap-3 py-0.5 hover:bg-granat-900/60 rounded px-1">
              <span className="text-granat-300 shrink-0">{l.at}</span>
              <span className={cn('shrink-0 w-14 font-semibold', LEVEL_COLOR[l.level])}>{l.level}</span>
              <span className="text-granat-100 break-all">{l.msg}</span>
            </div>
          ))}
          {live && (
            <div className="flex gap-3 py-0.5 px-1">
              <span className="w-2 h-4 bg-sem-green/70 animate-sem-dot-pulse rounded-sm" />
            </div>
          )}
        </div>
      </div>
    </>
  )
}
