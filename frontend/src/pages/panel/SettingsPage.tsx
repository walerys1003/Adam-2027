import { useState } from 'react'
import { Bell, Moon, Globe, ShieldCheck, Lock, Smartphone, Mail, MessageSquare, Phone } from 'lucide-react'
import type { SemaphoreLevel } from '@/types/domain'
import { PageHead } from '@/components/panel/PageHead'
import { Card, CardBody, Toggle, Button, Badge, SemaphoreBadge } from '@/components/ui'
import { cn } from '@/lib/cn'

type Channel = 'push' | 'sms' | 'email' | 'phone'
const CHANNELS: { id: Channel; label: string; icon: any }[] = [
  { id: 'push', label: 'Push', icon: Smartphone },
  { id: 'sms', label: 'SMS', icon: MessageSquare },
  { id: 'email', label: 'E-mail', icon: Mail },
  { id: 'phone', label: 'Telefon', icon: Phone },
]
const LEVELS: SemaphoreLevel[] = ['green', 'yellow', 'red', 'purple']
const LEVEL_LABEL: Record<SemaphoreLevel, string> = {
  green: 'Zielony',
  yellow: 'Żółty',
  red: 'Czerwony',
  purple: 'Fioletowy',
}

// initial matrix: level → channel → on
function initialMatrix(): Record<SemaphoreLevel, Record<Channel, boolean>> {
  return {
    green: { push: false, sms: false, email: true, phone: false },
    yellow: { push: true, sms: false, email: true, phone: false },
    red: { push: true, sms: true, email: true, phone: true },
    purple: { push: true, sms: true, email: true, phone: true }, // phone LOCKED on
  }
}

export function SettingsPage() {
  const [matrix, setMatrix] = useState(initialMatrix)
  const [quietHours, setQuietHours] = useState(true)

  const toggle = (level: SemaphoreLevel, ch: Channel) => {
    // Purple × Telefon is locked (mandatory)
    if (level === 'purple' && ch === 'phone') return
    setMatrix((m) => ({ ...m, [level]: { ...m[level], [ch]: !m[level][ch] } }))
  }

  return (
    <>
      <PageHead eyebrow="Preferencje" title="Ustawienia" subtitle="Powiadomienia, cisza nocna, język i bezpieczeństwo" />

      {/* Notification matrix */}
      <Card className="mb-6">
        <CardBody>
          <span className="eyebrow flex items-center gap-1.5"><Bell size={13} /> Powiadomienia</span>
          <h3 className="text-h4 font-serif text-granat-900 mt-1">Matryca semafora × kanał</h3>
          <p className="text-label text-ink-500 mt-1 mb-4">
            Poziom <b>Fioletowy</b> zawsze dzwoni (telefon) — zgodnie z protokołem 112. To ustawienie jest zablokowane.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[520px]">
              <thead>
                <tr>
                  <th className="text-left text-label text-ink-400 font-medium py-2 pr-4">Poziom</th>
                  {CHANNELS.map((c) => {
                    const Icon = c.icon
                    return (
                      <th key={c.id} className="text-center text-label text-ink-500 font-medium py-2 px-2">
                        <span className="inline-flex flex-col items-center gap-1">
                          <Icon size={16} /> {c.label}
                        </span>
                      </th>
                    )
                  })}
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {LEVELS.map((lvl) => (
                  <tr key={lvl}>
                    <td className="py-3 pr-4">
                      <SemaphoreBadge level={lvl} label={LEVEL_LABEL[lvl]} size="xs" />
                    </td>
                    {CHANNELS.map((c) => {
                      const locked = lvl === 'purple' && c.id === 'phone'
                      return (
                        <td key={c.id} className="py-3 px-2 text-center">
                          <div className="inline-flex flex-col items-center gap-1">
                            <Toggle checked={matrix[lvl][c.id]} onChange={() => toggle(lvl, c.id)} locked={locked} />
                            {locked && (
                              <span className="text-[10px] uppercase tracking-wide text-sem-purple flex items-center gap-0.5">
                                <Lock size={9} /> Wymagane
                              </span>
                            )}
                          </div>
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>

      <div className="grid gap-5 lg:grid-cols-2">
        {/* Quiet hours */}
        <Card>
          <CardBody>
            <div className="flex items-center justify-between">
              <div>
                <span className="eyebrow flex items-center gap-1.5"><Moon size={13} /> Cisza nocna</span>
                <h3 className="text-h4 font-serif text-granat-900 mt-1">22:00 – 07:00</h3>
                <p className="text-label text-ink-500 mt-1">
                  Wyciszamy powiadomienia zielone i żółte. Czerwone i fioletowe zawsze przechodzą.
                </p>
              </div>
              <Toggle checked={quietHours} onChange={setQuietHours} />
            </div>
          </CardBody>
        </Card>

        {/* Language */}
        <Card>
          <CardBody>
            <span className="eyebrow flex items-center gap-1.5"><Globe size={13} /> Język</span>
            <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-3">Język interfejsu</h3>
            <div className="flex gap-2">
              <Button variant="primary" size="sm">Polski</Button>
              <Button variant="secondary" size="sm">English</Button>
              <Button variant="secondary" size="sm">Deutsch</Button>
            </div>
          </CardBody>
        </Card>

        {/* Security */}
        <Card>
          <CardBody>
            <span className="eyebrow flex items-center gap-1.5"><ShieldCheck size={13} /> Bezpieczeństwo</span>
            <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-3">Uwierzytelnianie</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-body text-ink-700">Weryfikacja dwuetapowa (2FA)</span>
                <Badge tone="green">Aktywna</Badge>
              </div>
              <Button variant="secondary" fullWidth>Zmień hasło</Button>
            </div>
          </CardBody>
        </Card>

        {/* GDPR */}
        <Card>
          <CardBody>
            <span className="eyebrow">Prywatność (RODO)</span>
            <h3 className="text-h4 font-serif text-granat-900 mt-1 mb-3">Zarządzanie danymi</h3>
            <div className="space-y-2">
              <Button variant="secondary" fullWidth>Pobierz moje dane</Button>
              <Button variant="ghost" fullWidth>Zarządzaj zgodami</Button>
            </div>
          </CardBody>
        </Card>
      </div>
    </>
  )
}
