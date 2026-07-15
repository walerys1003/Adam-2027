import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'

/* ============================================================
   ADAM · LiveAnnouncer (WP-3 · a11y WCAG)
   Globalny region aria-live do ogłaszania zmian stanu (np. alerty
   semafora RED/PURPLE) czytnikom ekranu — niezależnie od tego, czy
   wizualny komponent jest w danym momencie widoczny/skupiony.

   Użycie:
     const announce = useAnnounce()
     announce('Semafor RED: Halina — brak odbioru', 'assertive')
   ============================================================ */

type Politeness = 'polite' | 'assertive'

interface AnnouncerApi {
  announce: (message: string, politeness?: Politeness) => void
}

const AnnouncerContext = createContext<AnnouncerApi | null>(null)

export function LiveAnnouncerProvider({ children }: { children: ReactNode }) {
  const [polite, setPolite] = useState('')
  const [assertive, setAssertive] = useState('')
  const timer = useRef<ReturnType<typeof setTimeout>>()

  const announce = useCallback((message: string, politeness: Politeness = 'polite') => {
    const setter = politeness === 'assertive' ? setAssertive : setPolite
    // Reset → set, by ten sam komunikat powtórzony był ponownie odczytany.
    setter('')
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => setter(message), 60)
  }, [])

  const api = useMemo<AnnouncerApi>(() => ({ announce }), [announce])

  return (
    <AnnouncerContext.Provider value={api}>
      {children}
      {/* Dwa regiony: uprzejmy (polite) i natarczywy (assertive/alarmy). */}
      <div aria-live="polite" aria-atomic="true" className="sr-only" data-testid="live-polite">
        {polite}
      </div>
      <div role="alert" aria-live="assertive" aria-atomic="true" className="sr-only" data-testid="live-assertive">
        {assertive}
      </div>
    </AnnouncerContext.Provider>
  )
}

export function useAnnounce(): (message: string, politeness?: Politeness) => void {
  const ctx = useContext(AnnouncerContext)
  if (!ctx) {
    // Bezpieczny no-op poza providerem (np. w testach jednostkowych).
    return () => {}
  }
  return ctx.announce
}
