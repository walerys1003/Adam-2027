import { useState, useRef, useEffect } from 'react'
import { TerminalSquare, ShieldAlert, CornerDownLeft } from 'lucide-react'
import { AdminPageHead } from '@/components/admin'
import { Badge } from '@/components/ui'

interface Line {
  id: number
  type: 'cmd' | 'out' | 'err'
  text: string
}

const MOTD = 'Adam Ops Console v7.4.2 — sesja audytowana (RODO). Wpisz `help`.'

const COMMANDS: Record<string, string> = {
  help: 'Dostępne: status · agents · semaphore · calls --active · asterisk · clear',
  status: 'adam-agent: OK · asterisk: OK · postgres: OK · redis: OK · uptime 6d 4h',
  agents: '12 agentów welfare aktywnych · 3 w trybie A/B · 0 błędów',
  semaphore: 'GREEN 38 · YELLOW 3 · RED 1 · PURPLE 0 (ostatnia ewaluacja 14:24:12)',
  'calls --active': '14 aktywnych kanałów PJSIP · najdłuższy 04:12 (SR-01042)',
  asterisk: 'ARI connected · 6 endpointów zarejestrowanych · Opus 48kHz',
}

export function AdminTerminal() {
  const [lines, setLines] = useState<Line[]>([{ id: 0, type: 'out', text: MOTD }])
  const [input, setInput] = useState('')
  const idRef = useRef(1)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [lines])

  const run = (raw: string) => {
    const cmd = raw.trim()
    if (!cmd) return
    const next: Line[] = [{ id: idRef.current++, type: 'cmd', text: cmd }]
    if (cmd === 'clear') {
      setLines([])
      return
    }
    const out = COMMANDS[cmd]
    next.push(
      out
        ? { id: idRef.current++, type: 'out', text: out }
        : { id: idRef.current++, type: 'err', text: `nieznana komenda: ${cmd} — wpisz \`help\`` },
    )
    setLines((l) => [...l, ...next])
  }

  return (
    <>
      <AdminPageHead
        eyebrow="System"
        title="Konsola operacyjna"
        subtitle="Bezpieczny terminal read-only do diagnostyki stacku Adam"
        actions={<Badge tone="gold">tylko odczyt · 2FA</Badge>}
      />

      <div className="mb-5 flex items-start gap-2 rounded-md bg-zloto-50 border border-zloto-200 p-3">
        <ShieldAlert size={16} className="text-zloto-700 mt-0.5 shrink-0" />
        <p className="text-caption text-ink-700">
          Konsola ograniczona do komend diagnostycznych. Każda komenda jest rejestrowana w dzienniku audytu.
        </p>
      </div>

      <div className="rounded-lg border border-line bg-granat-950 overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-2 border-b border-granat-800">
          <TerminalSquare size={14} className="text-granat-200" />
          <span className="font-mono text-caption text-granat-200">adam@ops:~$</span>
        </div>

        <div className="p-4 font-mono text-caption leading-relaxed max-h-[52vh] overflow-y-auto">
          {lines.map((l) => (
            <div key={l.id} className="py-0.5">
              {l.type === 'cmd' ? (
                <span className="text-sem-green">
                  <span className="text-granat-300">$ </span>
                  {l.text}
                </span>
              ) : l.type === 'err' ? (
                <span className="text-sem-red">{l.text}</span>
              ) : (
                <span className="text-granat-100">{l.text}</span>
              )}
            </div>
          ))}
          <div ref={endRef} />
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            run(input)
            setInput('')
          }}
          className="flex items-center gap-2 px-4 py-3 border-t border-granat-800"
        >
          <span className="font-mono text-caption text-granat-300 shrink-0">$</span>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="wpisz komendę…"
            autoFocus
            className="flex-1 bg-transparent outline-none font-mono text-caption text-granat-50 placeholder:text-granat-400"
          />
          <button type="submit" className="text-granat-300 hover:text-granat-100">
            <CornerDownLeft size={14} />
          </button>
        </form>
      </div>
    </>
  )
}
