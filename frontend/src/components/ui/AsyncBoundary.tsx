import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import { Button } from './Button'

/* ============================================================
   ADAM · AsyncBoundary (WP-1)
   Jednolita prezentacja stanów loading / error / empty dla ekranów
   spiętych z fasadą `api` przez hook useApi. Zgodne z Adam Design
   System (light-only, granat/zloto) i przygotowane pod a11y (WP-3):
   komunikaty w aria-live, czytelne dla czytników ekranu.
   ============================================================ */

export interface AsyncBoundaryProps {
  loading: boolean
  error: Error | null
  empty?: boolean
  /** Ponów wywołanie (z useApi.refetch). */
  onRetry?: () => void
  /** Treść pustego stanu (domyślnie ogólny komunikat). */
  emptyLabel?: string
  /** Etykieta ładowania (dla screen readerów). */
  loadingLabel?: string
  className?: string
  children: ReactNode
}

export function AsyncBoundary({
  loading,
  error,
  empty = false,
  onRetry,
  emptyLabel = 'Brak danych do wyświetlenia.',
  loadingLabel = 'Ładowanie danych…',
  className,
  children,
}: AsyncBoundaryProps) {
  if (loading) {
    return (
      <div
        role="status"
        aria-live="polite"
        aria-busy="true"
        className={cn('flex flex-col items-center justify-center gap-3 py-16 text-ink-500', className)}
      >
        <span
          className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-line border-t-granat-700"
          aria-hidden="true"
        />
        <p className="text-body">{loadingLabel}</p>
      </div>
    )
  }

  if (error) {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className={cn(
          'flex flex-col items-center justify-center gap-4 rounded-lg border border-sem-red/30 bg-sem-red/5 py-14 px-6 text-center',
          className,
        )}
      >
        <span className="text-h3 text-sem-red" aria-hidden="true">⚠</span>
        <div>
          <p className="text-h4 text-ink-900">Nie udało się wczytać danych</p>
          <p className="mt-1 text-body text-ink-500">{error.message}</p>
        </div>
        {onRetry && (
          <Button variant="secondary" onClick={onRetry}>
            Spróbuj ponownie
          </Button>
        )}
      </div>
    )
  }

  if (empty) {
    return (
      <div
        role="status"
        aria-live="polite"
        className={cn(
          'flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-line py-14 px-6 text-center text-ink-500',
          className,
        )}
      >
        <span className="text-h3 text-ink-300" aria-hidden="true">◦</span>
        <p className="text-body">{emptyLabel}</p>
      </div>
    )
  }

  return <>{children}</>
}
