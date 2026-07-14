import { useState } from 'react'
import type { ReactNode } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/cn'

export interface AccordionItem {
  id: string
  question: string
  answer: ReactNode
}

export function Accordion({
  items,
  className,
  defaultOpen,
}: {
  items: AccordionItem[]
  className?: string
  defaultOpen?: string
}) {
  const [open, setOpen] = useState<string | null>(defaultOpen ?? null)
  return (
    <div className={cn('adam-card divide-y divide-line', className)}>
      {items.map((it) => {
        const isOpen = open === it.id
        return (
          <div key={it.id}>
            <button
              onClick={() => setOpen(isOpen ? null : it.id)}
              aria-expanded={isOpen}
              className="w-full flex items-center justify-between gap-4 px-5 py-4 text-left"
            >
              <span className="text-body font-medium text-granat-900">{it.question}</span>
              <ChevronDown
                size={18}
                className={cn('text-ink-400 shrink-0 transition-transform', isOpen && 'rotate-180')}
              />
            </button>
            {isOpen && <div className="px-5 pb-4 text-body text-ink-600 leading-relaxed">{it.answer}</div>}
          </div>
        )
      })}
    </div>
  )
}
