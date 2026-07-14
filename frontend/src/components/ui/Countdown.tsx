import { useEffect, useState } from 'react'
import { cn } from '@/lib/cn'

/** Odlicza do `endsAt` (ISO). Wywołuje onExpire raz, gdy dojdzie do zera. */
export function Countdown({
  endsAt,
  onExpire,
  className,
  prefix,
}: {
  endsAt: string
  onExpire?: () => void
  className?: string
  prefix?: string
}) {
  const [remaining, setRemaining] = useState(() => Math.max(0, new Date(endsAt).getTime() - Date.now()))

  useEffect(() => {
    const target = new Date(endsAt).getTime()
    const tick = () => {
      const rem = Math.max(0, target - Date.now())
      setRemaining(rem)
      if (rem <= 0) onExpire?.()
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endsAt])

  const totalSec = Math.floor(remaining / 1000)
  const mm = String(Math.floor(totalSec / 60)).padStart(2, '0')
  const ss = String(totalSec % 60).padStart(2, '0')
  const urgent = totalSec <= 60

  return (
    <span className={cn('kpi tabular-nums', urgent ? 'text-sem-red' : 'text-granat-800', className)}>
      {prefix}
      {mm}:{ss}
    </span>
  )
}
