import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import type { Package } from '@/types/domain'

type Tone = 'neutral' | 'granat' | 'gold' | 'info' | 'green' | 'red'

const TONES: Record<Tone, string> = {
  neutral: 'bg-paper-2 text-ink-700 border-line',
  granat: 'bg-granat-50 text-granat-700 border-granat-200',
  gold: 'bg-zloto-50 text-zloto-700 border-zloto-200',
  info: 'bg-info-blue-bg text-info-blue border-info-blue/20',
  green: 'bg-sem-green-bg text-sem-green border-sem-green/20',
  red: 'bg-sem-red-bg text-sem-red border-sem-red/20',
}

export function Badge({
  tone = 'neutral',
  children,
  className,
}: {
  tone?: Tone
  children: ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-label font-medium',
        TONES[tone],
        className,
      )}
    >
      {children}
    </span>
  )
}

const PACKAGE_META: Record<Package, { tone: Tone; label: string }> = {
  basic: { tone: 'neutral', label: 'Basic' },
  family: { tone: 'info', label: 'Family' },
  premium: { tone: 'gold', label: 'Premium' },
}

export function PackageBadge({ package: pkg, className }: { package: Package; className?: string }) {
  const meta = PACKAGE_META[pkg]
  return (
    <Badge tone={meta.tone} className={className}>
      {meta.label}
    </Badge>
  )
}
