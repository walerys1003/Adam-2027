import { useCallback, useEffect, useRef, useState } from 'react'

/* ============================================================
   ADAM · useApi (WP-1)
   Uniwersalny hook do wywołań przez fasadę `api` z lib/api/client.
   Zapewnia jednolitą obsługę stanów: loading / error / empty / data
   oraz ręczny refetch. Wspiera zarówno tryb mock jak i realny backend
   (przełącznik żyje w client.ts – tu jest agnostyczny).
   ============================================================ */

export interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: Error | null
  /** true gdy zakończono ładowanie, brak błędu i wynik jest pusty */
  empty: boolean
  refetch: () => void
}

/** Heurystyka pustego wyniku: null/undefined, [] lub {} bez kluczy. */
export function isEmptyResult(value: unknown): boolean {
  if (value === null || value === undefined) return true
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value as object).length === 0
  return false
}

export interface UseApiOptions {
  /** Automatyczne wywołanie przy montażu (domyślnie true). */
  immediate?: boolean
}

/**
 * Wykonuje asynchroniczną funkcję (zwykle metodę `api.*`) i śledzi stan.
 *
 * @example
 *   const { data, loading, error, empty, refetch } = useApi(() => api.listOrders())
 */
export function useApi<T>(
  fn: () => Promise<T>,
  deps: unknown[] = [],
  options: UseApiOptions = {},
): UseApiState<T> {
  const { immediate = true } = options
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState<boolean>(immediate)
  const [error, setError] = useState<Error | null>(null)

  // Zapamiętujemy fn w ref, by zależności hooka nie wymuszały cyklu.
  const fnRef = useRef(fn)
  fnRef.current = fn
  const mounted = useRef(true)

  const run = useCallback(() => {
    setLoading(true)
    setError(null)
    fnRef
      .current()
      .then((res) => {
        if (!mounted.current) return
        setData(res)
      })
      .catch((err: unknown) => {
        if (!mounted.current) return
        setError(err instanceof Error ? err : new Error(String(err)))
      })
      .finally(() => {
        if (!mounted.current) return
        setLoading(false)
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    mounted.current = true
    if (immediate) run()
    return () => {
      mounted.current = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return {
    data,
    loading,
    error,
    empty: !loading && !error && isEmptyResult(data),
    refetch: run,
  }
}
