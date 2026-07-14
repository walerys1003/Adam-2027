import { cn } from '@/lib/cn'

export interface AvatarProps {
  firstName: string
  lastName: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  /** Pulse ring — only for RED/PURPLE seniors */
  pulse?: 'none' | 'red' | 'purple'
  imageUrl?: string
  className?: string
}

const SIZES = {
  sm: 'w-8 h-8 text-label',
  md: 'w-10 h-10 text-body',
  lg: 'w-14 h-14 text-h4',
  xl: 'w-20 h-20 text-h3',
}

const PULSE_RING = {
  none: '',
  red: 'ring-2 ring-sem-red ring-offset-2 ring-offset-white',
  purple: 'ring-2 ring-sem-purple ring-offset-2 ring-offset-white',
}

export function Avatar({ firstName, lastName, size = 'md', pulse = 'none', imageUrl, className }: AvatarProps) {
  const initials = `${firstName[0] ?? ''}${lastName[0] ?? ''}`.toUpperCase()

  return (
    <div className={cn('relative inline-flex', className)}>
      {pulse !== 'none' && (
        <span
          className={cn(
            'absolute inset-0 rounded-full animate-sem-pulse-ring',
            pulse === 'red' ? 'bg-sem-red' : 'bg-sem-purple',
          )}
          aria-hidden="true"
        />
      )}
      <div
        className={cn(
          'relative inline-flex items-center justify-center rounded-full font-serif font-medium overflow-hidden',
          'bg-gradient-to-br from-granat-600 to-granat-800 text-zloto-300',
          SIZES[size],
          pulse !== 'none' && PULSE_RING[pulse],
        )}
      >
        {imageUrl ? (
          <img src={imageUrl} alt={`${firstName} ${lastName}`} className="w-full h-full object-cover" />
        ) : (
          initials
        )}
      </div>
    </div>
  )
}
