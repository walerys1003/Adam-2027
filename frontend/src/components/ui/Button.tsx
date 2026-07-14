import { forwardRef } from 'react'
import type { ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'gold'
type Size = 'sm' | 'md' | 'lg'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  fullWidth?: boolean
}

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-granat-700 text-white hover:bg-granat-800 active:bg-granat-900 shadow-e1',
  secondary: 'bg-white text-granat-700 border border-line hover:bg-paper-2 hover:border-line-strong',
  ghost: 'bg-transparent text-granat-700 hover:bg-granat-50',
  danger: 'bg-sem-red text-white hover:brightness-110 shadow-red',
  gold: 'bg-zloto-500 text-granat-900 hover:bg-zloto-600 shadow-gold',
}

const SIZES: Record<Size, string> = {
  sm: 'text-label px-3 py-1.5 rounded-md gap-1.5',
  md: 'text-body px-4 py-2.5 rounded-md gap-2',
  lg: 'text-body-l px-6 py-3 rounded-lg gap-2.5',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = 'primary', size = 'md', fullWidth, className, children, ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center font-medium transition-all duration-200 ease-adam-out',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        VARIANTS[variant],
        SIZES[size],
        fullWidth && 'w-full',
        className,
      )}
      {...props}
    >
      {children}
    </button>
  )
})
