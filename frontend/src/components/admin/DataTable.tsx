import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

export interface Column<T> {
  key: string
  header: string
  render?: (row: T) => ReactNode
  align?: 'left' | 'right' | 'center'
  width?: string
}

export function DataTable<T extends { id?: string | number }>({
  columns,
  rows,
  onRowClick,
  empty = 'Brak danych.',
  className,
}: {
  columns: Column<T>[]
  rows: T[]
  onRowClick?: (row: T) => void
  empty?: string
  className?: string
}) {
  return (
    <div className={cn('adam-card overflow-hidden', className)}>
      <div className="overflow-x-auto">
        <table className="w-full text-body">
          <thead>
            <tr className="bg-paper-2 border-b border-line text-left">
              {columns.map((c) => (
                <th
                  key={c.key}
                  style={{ width: c.width }}
                  className={cn(
                    'px-4 py-3 text-label font-medium text-ink-500 uppercase tracking-wide whitespace-nowrap',
                    c.align === 'right' && 'text-right',
                    c.align === 'center' && 'text-center',
                  )}
                >
                  {c.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {rows.map((row, i) => (
              <tr
                key={row.id ?? i}
                onClick={() => onRowClick?.(row)}
                className={cn('transition-colors', onRowClick && 'cursor-pointer hover:bg-paper-2')}
              >
                {columns.map((c) => (
                  <td
                    key={c.key}
                    className={cn(
                      'px-4 py-3 text-ink-700 align-middle',
                      c.align === 'right' && 'text-right',
                      c.align === 'center' && 'text-center',
                    )}
                  >
                    {c.render ? c.render(row) : (row as any)[c.key]}
                  </td>
                ))}
              </tr>
            ))}
            {!rows.length && (
              <tr>
                <td colSpan={columns.length} className="px-4 py-10 text-center text-ink-400">
                  {empty}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
