import { useState } from 'react'
import {
  Pill,
  ShoppingCart,
  UtensilsCrossed,
  Car,
  Sparkles,
  Wrench,
  HeartHandshake,
  Users,
  Scissors,
  Package,
  Star,
  X,
  Plus,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import type { Order } from '@/types/domain'
import { api } from '@/lib/api/client'
import { useApi } from '@/lib/hooks/useApi'
import { ORDER_CATEGORIES } from '@/data/mockPanel'
import { MOCK_SENIORS } from '@/data/mockSeniors'
import { PageHead } from '@/components/panel/PageHead'
import { Card, CardBody, Badge, Button, Countdown, AsyncBoundary } from '@/components/ui'

const ICONS: Record<string, LucideIcon> = {
  Pill, ShoppingCart, UtensilsCrossed, Car, Sparkles, Wrench, HeartHandshake, Users, Scissors, Package,
}

const STATUS_META: Record<Order['status'], { label: string; tone: 'green' | 'gold' | 'neutral' | 'red' }> = {
  auto_confirmed: { label: 'Auto-potwierdzone', tone: 'green' },
  waiting_manual_confirm: { label: 'Czeka na potwierdzenie', tone: 'gold' },
  confirmed: { label: 'Potwierdzone', tone: 'green' },
  cancelled: { label: 'Anulowane', tone: 'neutral' },
}

function seniorName(id: string) {
  const s = MOCK_SENIORS.find((x) => x.id === id)
  return s ? `${s.firstName} ${s.lastName}` : id
}
function catLabel(id: string) {
  return ORDER_CATEGORIES.find((c) => c.id === id)?.label ?? id
}

function OrderCard({ order, onCancel }: { order: Order; onCancel: (id: string) => void }) {
  const [expired, setExpired] = useState(false)
  const meta = STATUS_META[order.status]
  const Icon = ICONS[ORDER_CATEGORIES.find((c) => c.id === order.categoryId)?.icon ?? 'Package'] ?? Package
  const cancellable =
    order.status !== 'cancelled' && !!order.cancellationWindowEndsAt && !expired

  return (
    <Card>
      <CardBody>
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-md bg-granat-50 text-granat-700 flex items-center justify-center shrink-0">
            <Icon size={19} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <h3 className="text-body font-medium text-granat-900">{catLabel(order.categoryId)}</h3>
              <Badge tone={meta.tone}>{meta.label}</Badge>
            </div>
            <p className="text-label text-ink-500 mt-0.5">
              Dla: {seniorName(order.seniorId)} · <span className="font-mono text-caption">{order.orderId}</span>
            </p>
            {order.partner && (
              <p className="text-label text-ink-500 mt-1 inline-flex items-center gap-1">
                {order.partner.name}
                <span className="inline-flex items-center gap-0.5 text-zloto-600">
                  <Star size={11} className="fill-zloto-500 text-zloto-500" /> {order.partner.rating}
                </span>
              </p>
            )}
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-label text-ink-600">
              {order.estimatedPrice && <span>{order.estimatedPrice}</span>}
              {order.estimatedDelivery && <span className="text-ink-400">dostawa: {order.estimatedDelivery}</span>}
              <Badge tone="neutral">{order.requestSource === 'adam-call' ? 'z rozmowy Adama' : 'z panelu'}</Badge>
            </div>
          </div>
        </div>

        {cancellable && (
          <div className="mt-4 pt-3 border-t border-line flex items-center justify-between">
            <span className="text-label text-ink-500">
              Anulowanie do:{' '}
              <Countdown endsAt={order.cancellationWindowEndsAt!} onExpire={() => setExpired(true)} />
            </span>
            <Button size="sm" variant="danger" onClick={() => onCancel(order.orderId)}>
              <X size={14} /> Anuluj
            </Button>
          </div>
        )}
      </CardBody>
    </Card>
  )
}

function CategoryPicker({ onPick }: { onPick: (categoryId: string) => void }) {
  return (
    <Card>
      <CardBody>
        <span className="eyebrow">Nowe zamówienie</span>
        <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-4">Wybierz kategorię</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {ORDER_CATEGORIES.map((c) => {
            const Icon = ICONS[c.icon] ?? Package
            return (
              <button
                key={c.id}
                onClick={() => onPick(c.id)}
                className="group text-left rounded-lg border border-line p-3 hover:border-zloto-400 hover:bg-zloto-50/40 transition-colors"
              >
                <span className="w-9 h-9 rounded-md bg-granat-50 text-granat-700 flex items-center justify-center group-hover:bg-white">
                  <Icon size={18} />
                </span>
                <p className="text-label font-medium text-granat-900 mt-2">{c.label}</p>
                <p className="text-caption text-ink-400 mt-0.5 line-clamp-2">{c.examples}</p>
              </button>
            )
          })}
        </div>
      </CardBody>
    </Card>
  )
}

export function OrdersPage() {
  const [picking, setPicking] = useState(false)
  // WP-1: dane zleceń przez fasadę `api` z jednolitą obsługą stanów (useApi).
  const { data, loading, error, empty, refetch } = useApi<Order[]>(() => api.listOrders())

  const cancel = async (id: string) => {
    await api.cancelOrder(id)
    refetch()
  }

  const createFor = async (categoryId: string) => {
    await api.createOrder({ seniorId: MOCK_SENIORS[0].id, categoryId, requestSource: 'caregiver-panel' })
    setPicking(false)
    refetch()
  }

  const orders = data ?? []
  const active = orders.filter((o) => o.status !== 'cancelled')
  const cancelled = orders.filter((o) => o.status === 'cancelled')

  return (
    <>
      <PageHead
        eyebrow="Marketplace"
        title="Zamówienia"
        subtitle="Zlecenia z rozmów Adama i z panelu — z oknem anulowania"
        actions={
          <Button variant="gold" onClick={() => setPicking((p) => !p)}>
            <Plus size={16} /> Nowe zamówienie
          </Button>
        }
      />

      {picking && (
        <div className="mb-6">
          <CategoryPicker onPick={createFor} />
        </div>
      )}

      <AsyncBoundary
        loading={loading}
        error={error}
        empty={empty}
        onRetry={refetch}
        emptyLabel="Brak zamówień. Utwórz nowe przyciskiem „Nowe zamówienie”."
        loadingLabel="Ładowanie zamówień…"
      >
        <div className="space-y-6">
          <div>
            <h2 className="font-serif text-h4 text-granat-900 mb-3">Aktywne ({active.length})</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {active.map((o) => (
                <OrderCard key={o.orderId} order={o} onCancel={cancel} />
              ))}
              {!active.length && <p className="text-body text-ink-400">Brak aktywnych zamówień.</p>}
            </div>
          </div>
          {cancelled.length > 0 && (
            <div>
              <h2 className="font-serif text-h4 text-granat-900 mb-3">Anulowane ({cancelled.length})</h2>
              <div className="grid md:grid-cols-2 gap-4 opacity-70">
                {cancelled.map((o) => (
                  <OrderCard key={o.orderId} order={o} onCancel={cancel} />
                ))}
              </div>
            </div>
          )}
        </div>
      </AsyncBoundary>
    </>
  )
}
