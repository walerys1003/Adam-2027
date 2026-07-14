import type { ReactNode } from 'react'

export function ChapterHead({
  num,
  label,
  title,
  sub,
}: {
  num: string
  label: string
  title: ReactNode
  sub?: string
}) {
  return (
    <div className="grid md:grid-cols-[220px_1fr] gap-10 md:gap-20 mb-16 md:mb-24 items-start">
      <div>
        <div className="font-serif italic text-[96px] leading-none tracking-[-0.04em] text-zloto-500">{num}</div>
        <div className="font-mono text-caption tracking-[0.16em] uppercase text-ink-500 mt-2">{label}</div>
      </div>
      <div>
        <h2 className="font-serif font-normal text-[clamp(40px,6vw,64px)] leading-none tracking-[-0.03em] text-granat-900">
          {title}
        </h2>
        {sub && <p className="text-body-l text-ink-700 mt-7 max-w-[620px] leading-relaxed">{sub}</p>}
      </div>
    </div>
  )
}
