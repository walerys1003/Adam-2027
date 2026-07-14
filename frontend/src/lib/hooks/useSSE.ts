import { useEffect, useRef, useState } from 'react'
import type { SemaphoreLevel } from '@/types/domain'

export interface LiveEvent {
  id: string
  seniorId: string
  seniorName: string
  level: SemaphoreLevel
  message: string
  timestamp: string
}

const MOCK_STREAM: Omit<LiveEvent, 'id' | 'timestamp'>[] = [
  { seniorId: 'HW-01247', seniorName: 'Halina Wiśniewska', level: 'green', message: 'Poranny welfare-check zakończony OK' },
  { seniorId: 'ZK-00812', seniorName: 'Zofia Kaczmarek', level: 'yellow', message: 'Nastrój poniżej 0.5 — obserwujemy' },
  { seniorId: 'IW-04455', seniorName: 'Irena Wójcik', level: 'green', message: 'Leki przyjęte o czasie' },
]

const USE_MOCK = !import.meta.env.VITE_WS_URL

/**
 * Nasłuch zdarzeń live (semafor/alerty).
 * Produkcyjnie: SSE/WebSocket na VITE_WS_URL.
 * W trybie mock: symulowany strumień co `intervalMs`.
 */
export function useSSE(intervalMs = 12000) {
  const [events, setEvents] = useState<LiveEvent[]>([])
  const [connected, setConnected] = useState(false)
  const idx = useRef(0)

  useEffect(() => {
    if (USE_MOCK) {
      setConnected(true)
      const push = () => {
        const base = MOCK_STREAM[idx.current % MOCK_STREAM.length]
        idx.current += 1
        setEvents((prev) =>
          [{ ...base, id: 'ev-' + Date.now(), timestamp: new Date().toISOString() }, ...prev].slice(0, 20),
        )
      }
      const t = setInterval(push, intervalMs)
      return () => {
        clearInterval(t)
        setConnected(false)
      }
    }

    // Real SSE
    const es = new EventSource(import.meta.env.VITE_WS_URL as string)
    es.onopen = () => setConnected(true)
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data) as LiveEvent
        setEvents((prev) => [data, ...prev].slice(0, 20))
      } catch {
        /* ignore malformed */
      }
    }
    es.onerror = () => setConnected(false)
    return () => es.close()
  }, [intervalMs])

  return { events, connected }
}
