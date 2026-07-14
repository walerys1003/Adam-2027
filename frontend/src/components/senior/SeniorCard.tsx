import { Phone, ChevronRight, MapPin, Heart } from 'lucide-react'
import { cn } from '@/lib/cn'
import type { Senior } from '@/types/domain'
import { Card } from '@/components/ui/Card'
import { Avatar } from '@/components/ui/Avatar'
import { SemaphoreBadge } from '@/components/ui/SemaphoreBadge'
import { PackageBadge } from '@/components/ui/Badge'
import { Sparkline } from '@/components/ui/Sparkline'
import { Button } from '@/components/ui/Button'

export interface SeniorCardProps {
  senior: Senior
  variant?: 'compact' | 'full'
  onClick?: (senior: Senior) => void
  onCall?: (senior: Senior) => void
  showActions?: boolean
  className?: string
}

const ACCENT_MAP = {
  green: 'none',
  yellow: 'gold',
  red: 'red',
  purple: 'purple',
} as const

export function SeniorCard({
  senior,
  variant = 'full',
  onClick,
  onCall,
  showActions = true,
  className,
}: SeniorCardProps) {
  const pulse = senior.pulseAvatar
    ? senior.semaphore === 'purple'
      ? 'purple'
      : senior.semaphore === 'red'
        ? 'red'
        : 'none'
    : 'none'

  return (
    <Card
      accent={ACCENT_MAP[senior.semaphore]}
      interactive={!!onClick}
      onClick={() => onClick?.(senior)}
      className={cn('p-4', className)}
    >
      <div className="flex items-start gap-3">
        <Avatar firstName={senior.firstName} lastName={senior.lastName} size="lg" pulse={pulse} />

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <h3 className="text-h4 font-serif text-granat-900 truncate">
                {senior.firstName} {senior.lastName}
              </h3>
              <div className="flex items-center gap-2 text-label text-ink-500 mt-0.5">
                <span>{senior.age} lat</span>
                <span aria-hidden>·</span>
                <span className="inline-flex items-center gap-1">
                  <MapPin size={12} /> {senior.district}
                </span>
              </div>
            </div>
            <PackageBadge package={senior.package} />
          </div>

          <div className="mt-3">
            <SemaphoreBadge
              level={senior.semaphore}
              label={senior.semaphoreReason}
              size="sm"
            />
          </div>

          {variant === 'full' && (
            <div className="flex items-center justify-between mt-3 gap-4">
              <div className="flex items-center gap-4">
                <div className="flex flex-col">
                  <span className="text-caption text-ink-400 uppercase tracking-wide">Nastrój</span>
                  <Sparkline data={senior.moodTrend7d} width={72} height={22} />
                </div>
                <div className="flex flex-col">
                  <span className="text-caption text-ink-400 uppercase tracking-wide">Leki 30d</span>
                  <span className="kpi text-h4 text-granat-800">{senior.adherence30d}%</span>
                </div>
                {senior.heartRate && (
                  <div className="flex flex-col">
                    <span className="text-caption text-ink-400 uppercase tracking-wide inline-flex items-center gap-1">
                      <Heart size={10} /> Tętno
                    </span>
                    <span className="kpi text-h4 text-granat-800">{senior.heartRate}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {showActions && variant === 'full' && (
        <div className="flex items-center justify-between mt-4 pt-3 border-t border-line">
          <Button
            variant="secondary"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              onCall?.(senior)
            }}
          >
            <Phone size={14} /> Zadzwoń
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              onClick?.(senior)
            }}
          >
            Szczegóły <ChevronRight size={14} />
          </Button>
        </div>
      )}
    </Card>
  )
}
