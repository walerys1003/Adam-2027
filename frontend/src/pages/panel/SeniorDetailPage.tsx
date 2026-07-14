import { useEffect, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import type { SeniorDetail, MoodPoint, AlertMarker } from '@/types/domain'
import { api } from '@/lib/api/client'
import { Tabs } from '@/components/ui'
import type { TabItem } from '@/components/ui'
import { SeniorDetailHead } from '@/components/panel/SeniorDetailHead'
import {
  TabOverview,
  TabCalls,
  TabMeds,
  TabWearable,
  TabAlerts,
  TabReports,
  TabFamily,
  TabGdpr,
} from '@/components/panel/senior-tabs'

const TAB_IDS = ['overview', 'calls', 'meds', 'wearable', 'alerts', 'reports', 'family', 'gdpr'] as const
type TabId = (typeof TAB_IDS)[number]

export function SeniorDetailPage() {
  const { id = '' } = useParams()
  const [params, setParams] = useSearchParams()
  const [senior, setSenior] = useState<SeniorDetail | null>(null)
  const [mood, setMood] = useState<{ data: MoodPoint[]; markers: AlertMarker[] }>({ data: [], markers: [] })
  const [loading, setLoading] = useState(true)

  const rawTab = params.get('tab') as TabId | null
  const tab: TabId = rawTab && TAB_IDS.includes(rawTab) ? rawTab : 'overview'

  useEffect(() => {
    let alive = true
    setLoading(true)
    Promise.all([api.getSenior(id), api.getMood(id, '30d')]).then(([s, m]) => {
      if (!alive) return
      setSenior(s)
      setMood(m)
      setLoading(false)
    })
    return () => {
      alive = false
    }
  }, [id])

  if (loading || !senior) {
    return (
      <div className="space-y-4">
        <div className="adam-card h-40 animate-pulse bg-paper-2" />
        <div className="adam-card h-64 animate-pulse bg-paper-2" />
      </div>
    )
  }

  const tabs: TabItem[] = [
    { id: 'overview', label: 'Przegląd' },
    { id: 'calls', label: 'Rozmowy', count: senior.calls.length },
    { id: 'meds', label: 'Leki', count: senior.meds.length },
    { id: 'wearable', label: 'Wearable' },
    { id: 'alerts', label: 'Alerty', count: senior.alerts.length },
    { id: 'reports', label: 'Raporty', count: senior.reports.length },
    { id: 'family', label: 'Rodzina' },
    { id: 'gdpr', label: 'RODO' },
  ]

  const setTab = (t: string) => {
    params.set('tab', t)
    setParams(params, { replace: true })
  }

  return (
    <div className="space-y-5">
      <SeniorDetailHead senior={senior} />
      <Tabs items={tabs} value={tab} onChange={setTab} />
      <div>
        {tab === 'overview' && <TabOverview senior={senior} mood={mood} />}
        {tab === 'calls' && <TabCalls senior={senior} />}
        {tab === 'meds' && <TabMeds senior={senior} />}
        {tab === 'wearable' && <TabWearable senior={senior} />}
        {tab === 'alerts' && <TabAlerts senior={senior} />}
        {tab === 'reports' && <TabReports senior={senior} />}
        {tab === 'family' && <TabFamily senior={senior} />}
        {tab === 'gdpr' && <TabGdpr senior={senior} />}
      </div>
    </div>
  )
}
