import { Siren, Phone } from 'lucide-react'
import { cn } from '@/lib/cn'
import type { Senior } from '@/types/domain'
import { Button } from '@/components/ui'

export function CriticalAlertBanner({ seniors }: { seniors: Senior[] }) {
  const critical = seniors.filter((s) => s.semaphore === 'red' || s.semaphore === 'purple')
  if (critical.length === 0) return null
  const hasPurple = critical.some((s) => s.semaphore === 'purple')

  return (
    <div
      className={cn(
        'rounded-lg border-l-4 p-4 mb-6 flex items-center gap-4',
        hasPurple ? 'bg-sem-purple-bg border-l-sem-purple' : 'bg-sem-red-bg border-l-sem-red',
      )}
    >
      <span className={cn('grid place-items-center w-10 h-10 rounded-full', hasPurple ? 'bg-sem-purple text-white' : 'bg-sem-red text-white')}>
        <Siren size={20} className="animate-sem-dot-pulse" />
      </span>
      <div className="flex-1 min-w-0">
        <p className={cn('font-serif text-h4', hasPurple ? 'text-sem-purple' : 'text-sem-red')}>
          {hasPurple ? 'Zagrożenie życia — trwa eskalacja' : 'Alarm krytyczny'}
        </p>
        <p className="text-body text-ink-700 truncate">
          {critical.map((s) => `${s.firstName} ${s.lastName} — ${s.semaphoreReason}`).join(' · ')}
        </p>
      </div>
      <Button variant="danger" size="sm">
        <Phone size={14} /> Reaguj
      </Button>
    </div>
  )
}
