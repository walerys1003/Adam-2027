import type { HTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/cn'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** Elevation level */
  elevation?: 'e1' | 'e2' | 'e3' | 'e4' | 'none'
  /** Left accent band color (semaphore signature) */
  accent?: 'granat' | 'gold' | 'red' | 'purple' | 'none'
  interactive?: boolean
}

const ELEVATIONS = {
  none: '',
  e1: 'shadow-e1',
  e2: 'shadow-e2',
  e3: 'shadow-e3',
  e4: 'shadow-e4',
}

const ACCENTS = {
  none: '',
  granat: 'border-l-4 border-l-granat-700',
  gold: 'border-l-4 border-l-zloto-500',
  red: 'border-l-4 border-l-sem-red',
  purple: 'border-l-4 border-l-sem-purple',
}

export function Card({
  elevation = 'e1',
  accent = 'none',
  interactive = false,
  className,
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        'bg-white border border-line rounded-lg',
        ELEVATIONS[elevation],
        ACCENTS[accent],
        interactive && 'cursor-pointer transition-all duration-200 ease-adam-out hover:shadow-e3 hover:-translate-y-0.5',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn('px-5 pt-5 pb-3', className)}>{children}</div>
}

export function CardBody({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn('px-5 py-3', className)}>{children}</div>
}

export function CardFooter({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn('px-5 pt-3 pb-5 border-t border-line', className)}>{children}</div>
}
