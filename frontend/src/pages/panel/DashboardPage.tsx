import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Users, Phone, Pill, Siren } from 'lucide-react'
import type { Senior } from '@/types/domain'
import { api } from '@/lib/api/client'
import { PanelLayout } from '@/components/panel/PanelLayout'
import { PageHead } from '@/components/panel/PageHead'
import { CriticalAlertBanner } from '@/components/panel/CriticalAlertBanner'
import { SeniorCard } from '@/components/senior'
import { Card, Stat } from '@/components/ui'

export function DashboardPage() {
  const navigate = useNavigate()
  const [seniors, setSeniors] = useState<Senior[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getMySeniors().then((r) => {
      setSeniors(r.seniors)
      setLoading(false)
    })
  }, [])

  const avgAdherence = seniors.length
    ? Math.round(seniors.reduce((s, x) => s + x.adherence30d, 0) / seniors.length)
    : 0
  const alerts30d = seniors.filter((s) => s.semaphore === 'red' || s.semaphore === 'purple').length

  return (
    <PanelLayout>
      <PageHead eyebrow="Wtorek, 12 lipca" title="Dzień dobry, Anno" subtitle="Podsumowanie Twoich bliskich" />

      <CriticalAlertBanner seniors={seniors} />

      {/* KPI strip */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card className="p-5"><Stat label="Twoi bliscy" value={seniors.length} icon={<Users size={14} />} /></Card>
        <Card className="p-5"><Stat label="Rozmowy 7d" value="42" trend="up" trendLabel="+6" icon={<Phone size={14} />} /></Card>
        <Card className="p-5"><Stat label="Śr. adherence" value={avgAdherence} unit="%" icon={<Pill size={14} />} /></Card>
        <Card className="p-5"><Stat label="Alerty 30d" value={alerts30d} trend={alerts30d ? 'down' : 'flat'} icon={<Siren size={14} />} /></Card>
      </div>

      <div className="mb-4">
        <span className="eyebrow">Moi bliscy</span>
        <h2 className="font-serif text-h3 text-granat-900">Lista podopiecznych</h2>
      </div>

      {loading ? (
        <p className="text-body text-ink-500">Ładowanie…</p>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {seniors.map((s) => (
            <SeniorCard
              key={s.id}
              senior={s}
              onClick={() => navigate(`/panel/senior/${s.id}`)}
              onCall={() => {}}
            />
          ))}
        </div>
      )}
    </PanelLayout>
  )
}
