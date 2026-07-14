import { ArrowLeft, Phone, MessageCircle, ShoppingBag, MapPin } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import type { SeniorDetail } from '@/types/domain'
import { Avatar, SemaphoreBadge, PackageBadge, Button } from '@/components/ui'

function QuickStat({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <div className="text-center px-3">
      <p className={`kpi text-h4 ${tone ?? 'text-granat-800'}`}>{value}</p>
      <p className="text-caption text-ink-500 uppercase tracking-wide mt-0.5">{label}</p>
    </div>
  )
}

export function SeniorDetailHead({ senior }: { senior: SeniorDetail }) {
  const navigate = useNavigate()
  const pulse = senior.semaphore === 'red' ? 'red' : senior.semaphore === 'purple' ? 'purple' : 'none'

  return (
    <div className="adam-card overflow-hidden">
      {/* accent band */}
      <div
        className="h-1.5"
        style={{
          background:
            senior.semaphore === 'red'
              ? 'var(--sem-red)'
              : senior.semaphore === 'purple'
                ? 'var(--sem-purple)'
                : senior.semaphore === 'yellow'
                  ? 'var(--sem-yellow)'
                  : 'var(--sem-green)',
        }}
      />
      <div className="p-5 lg:p-6">
        <button
          onClick={() => navigate('/panel')}
          className="inline-flex items-center gap-1.5 text-label text-ink-500 hover:text-granat-700 mb-4"
        >
          <ArrowLeft size={15} /> Powrót do dashboardu
        </button>

        <div className="flex flex-col lg:flex-row lg:items-center gap-5">
          <Avatar
            firstName={senior.firstName}
            lastName={senior.lastName}
            size="xl"
            pulse={pulse}
          />
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="font-serif text-h2 text-granat-900">
                {senior.firstName} {senior.lastName}
              </h1>
              <SemaphoreBadge level={senior.semaphore} label={senior.semaphoreReason} size="sm" />
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-label text-ink-500">
              <span className="font-mono text-caption text-ink-400">{senior.id}</span>
              <span>{senior.age} lat</span>
              <span className="inline-flex items-center gap-1">
                <MapPin size={13} /> {senior.district}
                {senior.address ? ` · ${senior.address}` : ''}
              </span>
              <PackageBadge package={senior.package} />
            </div>
          </div>

          {/* actions */}
          <div className="flex gap-2 shrink-0">
            <Button size="sm" variant="primary">
              <Phone size={15} /> Zadzwoń
            </Button>
            <Button size="sm" variant="secondary">
              <MessageCircle size={15} /> Wiadomość
            </Button>
            <Button size="sm" variant="ghost">
              <ShoppingBag size={15} /> Zamów
            </Button>
          </div>
        </div>

        {/* quick stats */}
        <div className="grid grid-cols-2 sm:grid-cols-5 divide-x divide-line border-t border-line mt-5 pt-5">
          <QuickStat label="Nastrój" value={`${Math.round(senior.mood * 100)}%`} tone={senior.mood < 0.5 ? 'text-zloto-700' : 'text-sem-green'} />
          <QuickStat label="Leki 30d" value={`${senior.adherence30d}%`} tone={senior.adherence30d < 70 ? 'text-sem-red' : 'text-granat-800'} />
          <QuickStat label="Tętno" value={senior.heartRate ? `${senior.heartRate}` : '—'} />
          <QuickStat label="SpO₂" value={senior.spo2 ? `${senior.spo2}%` : '—'} />
          <QuickStat label="Alerty" value={`${senior.alerts.length}`} tone={senior.alerts.length ? 'text-zloto-700' : 'text-granat-800'} />
        </div>
      </div>
    </div>
  )
}
