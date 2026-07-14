import { useEffect, useState } from 'react'
import { Crown, Gift, Share2, Monitor, Download, LogOut, Copy, Check } from 'lucide-react'
import type { Invoice, Session } from '@/types/domain'
import { api } from '@/lib/api/client'
import { useAuth } from '@/lib/auth/AuthContext'
import { PageHead } from '@/components/panel/PageHead'
import { Card, CardBody, Button, Badge, RadialGauge } from '@/components/ui'

const INV_TONE: Record<Invoice['status'], 'green' | 'gold' | 'red'> = {
  paid: 'green',
  pending: 'gold',
  overdue: 'red',
}
const INV_LABEL: Record<Invoice['status'], string> = {
  paid: 'Opłacona',
  pending: 'Do zapłaty',
  overdue: 'Zaległa',
}

export function AccountPage() {
  const { user } = useAuth()
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [sessions, setSessions] = useState<Session[]>([])
  const [copied, setCopied] = useState(false)
  const referral = 'ADAM-ANNA-2026'

  useEffect(() => {
    api.listInvoices().then(setInvoices)
    api.listSessions().then(setSessions)
  }, [])

  const copy = () => {
    navigator.clipboard?.writeText(referral)
    setCopied(true)
    setTimeout(() => setCopied(false), 1800)
  }

  return (
    <>
      <PageHead eyebrow="Profil" title="Konto" subtitle={user?.email} />

      {/* Subscription hero */}
      <Card className="overflow-hidden mb-6">
        <div className="bg-gradient-to-br from-granat-700 to-granat-900 p-6 text-white">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="inline-flex items-center gap-1.5 text-zloto-400 text-label uppercase tracking-wide">
                <Crown size={14} /> Plan Premium
              </span>
              <h2 className="font-serif text-h2 mt-1">SilverTech Adam · Premium</h2>
              <p className="text-white/70 text-body mt-1">
                5 podopiecznych · nielimitowane rozmowy · wsparcie 24/7 · wearables
              </p>
            </div>
            <div className="text-right">
              <p className="kpi text-h1 text-zloto-400">249 zł</p>
              <p className="text-white/60 text-label">/ miesiąc · odnowienie 1 sierpnia</p>
              <Button variant="gold" size="sm" className="mt-3">Zarządzaj planem</Button>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid gap-5 lg:grid-cols-3">
        {/* Loyalty */}
        <Card>
          <CardBody className="flex items-center gap-5">
            <RadialGauge value={72} size={96} sublabel="do rangi" />
            <div>
              <span className="eyebrow flex items-center gap-1.5"><Gift size={13} /> Program lojalnościowy</span>
              <h3 className="text-h4 font-serif text-granat-900 mt-1">Srebrny Opiekun</h3>
              <p className="text-label text-ink-500 mt-1">
                Jeszcze 280 pkt do rangi <span className="text-zloto-700 font-medium">Złoty</span>.
              </p>
            </div>
          </CardBody>
        </Card>

        {/* Referral */}
        <Card>
          <CardBody>
            <span className="eyebrow flex items-center gap-1.5"><Share2 size={13} /> Polecenia</span>
            <h3 className="text-h4 font-serif text-granat-900 mt-1">Poleć Adama</h3>
            <p className="text-label text-ink-500 mt-1">
              Za każde polecenie: <span className="text-zloto-700 font-medium">1 miesiąc gratis</span>.
            </p>
            <div className="flex items-center gap-2 mt-3">
              <code className="flex-1 bg-paper-2 rounded-md px-3 py-2 text-label font-mono text-granat-800">{referral}</code>
              <Button size="sm" variant="secondary" onClick={copy}>
                {copied ? <Check size={14} /> : <Copy size={14} />}
              </Button>
            </div>
          </CardBody>
        </Card>

        {/* Loyalty stats */}
        <Card>
          <CardBody>
            <span className="eyebrow">Twoje korzyści</span>
            <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-3">Zebrane punkty</h3>
            <div className="space-y-2 text-body">
              <div className="flex justify-between"><span className="text-ink-500">Punkty</span><span className="kpi text-granat-800">720</span></div>
              <div className="flex justify-between"><span className="text-ink-500">Polecenia</span><span className="kpi text-granat-800">3</span></div>
              <div className="flex justify-between"><span className="text-ink-500">Miesiące gratis</span><span className="kpi text-sem-green">2</span></div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Sessions */}
      <Card className="mt-5">
        <CardBody>
          <span className="eyebrow flex items-center gap-1.5"><Monitor size={13} /> Bezpieczeństwo</span>
          <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-3">Aktywne sesje</h3>
          <div className="divide-y divide-line">
            {sessions.map((s) => (
              <div key={s.id} className="py-3 flex items-center justify-between gap-3">
                <div>
                  <p className="text-body font-medium text-granat-900">
                    {s.device} {s.current && <Badge tone="green" className="ml-1">ta sesja</Badge>}
                  </p>
                  <p className="text-caption text-ink-500">{s.location} · {s.lastActive}</p>
                </div>
                {!s.current && (
                  <Button size="sm" variant="ghost"><LogOut size={14} /> Wyloguj</Button>
                )}
              </div>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Invoices */}
      <Card className="mt-5">
        <CardBody>
          <span className="eyebrow">Rozliczenia</span>
          <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-3">Faktury</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-body">
              <thead>
                <tr className="text-label text-ink-400 text-left border-b border-line">
                  <th className="py-2 font-medium">Numer</th>
                  <th className="py-2 font-medium">Okres</th>
                  <th className="py-2 font-medium">Kwota</th>
                  <th className="py-2 font-medium">Status</th>
                  <th className="py-2" />
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {invoices.map((inv) => (
                  <tr key={inv.id}>
                    <td className="py-3 font-mono text-caption text-ink-600">{inv.id}</td>
                    <td className="py-3 text-ink-700">{inv.period}</td>
                    <td className="py-3 kpi text-granat-800">{inv.amount}</td>
                    <td className="py-3"><Badge tone={INV_TONE[inv.status]}>{INV_LABEL[inv.status]}</Badge></td>
                    <td className="py-3 text-right">
                      <Button size="sm" variant="ghost"><Download size={14} /> PDF</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>
    </>
  )
}
