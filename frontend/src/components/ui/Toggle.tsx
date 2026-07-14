import { Lock } from 'lucide-react'
import { cn } from '@/lib/cn'

/** Przełącznik on/off. `locked` = wymuszony (np. Purple×Telefon w matrycy powiadomień). */
export function Toggle({
  checked,
  onChange,
  locked = false,
  size = 'md',
  label,
}: {
  checked: boolean
  onChange?: (v: boolean) => void
  locked?: boolean
  size?: 'sm' | 'md'
  label?: string
}) {
  const dims = size === 'sm' ? { w: 'w-8', h: 'h-4.5', dot: 'w-3.5 h-3.5', tx: 'translate-x-3.5' } : { w: 'w-11', h: 'h-6', dot: 'w-5 h-5', tx: 'translate-x-5' }
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      disabled={locked}
      onClick={() => !locked && onChange?.(!checked)}
      className={cn(
        'relative inline-flex items-center rounded-full transition-colors shrink-0',
        dims.w,
        dims.h,
        checked ? 'bg-granat-700' : 'bg-paper-3',
        locked && 'opacity-90 cursor-not-allowed',
      )}
    >
      <span
        className={cn(
          'inline-flex items-center justify-center rounded-full bg-white shadow-e1 transform transition-transform ml-0.5',
          dims.dot,
          checked && dims.tx,
        )}
      >
        {locked && <Lock size={9} className="text-granat-700" />}
      </span>
    </button>
  )
}
