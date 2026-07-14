import { PhoneCall, Radio, Server, CheckCircle2, XCircle, Puzzle } from 'lucide-react'
import { AdminPageHead, StatTile } from '@/components/admin'
import { Card, CardHeader, CardBody, Badge } from '@/components/ui'
import { ASTERISK_STATUS } from '@/data/mockAdmin'

export function AdminAsterisk() {
  const a = ASTERISK_STATUS

  return (
    <>
      <AdminPageHead
        eyebrow="System"
        title="Asterisk PBX"
        subtitle="ARI, kanały głosowe i moduły telefonii"
        actions={
          a.ariConnected ? (
            <Badge tone="green">
              <CheckCircle2 size={12} className="mr-1 inline" /> ARI połączone
            </Badge>
          ) : (
            <Badge tone="red">
              <XCircle size={12} className="mr-1 inline" /> ARI rozłączone
            </Badge>
          )
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <StatTile label="Aktywne kanały" value={a.activeChannels} icon={<PhoneCall size={18} />} accent="granat" />
        <StatTile label="Zarejestrowane endpointy" value={a.registeredEndpoints} icon={<Radio size={18} />} accent="green" />
        <StatTile label="Załadowane moduły" value={a.modules.length} icon={<Puzzle size={18} />} accent="gold" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h3 className="font-serif text-h4 text-granat-900 flex items-center gap-2">
              <Server size={18} className="text-granat-500" /> Połączenie ARI
            </h3>
          </CardHeader>
          <CardBody className="space-y-2 text-label">
            <Row k="URL" v={<span className="font-mono">http://asterisk:8088/ari</span>} />
            <Row k="Użytkownik" v={<span className="font-mono">adam</span>} />
            <Row k="WebSocket" v={<Badge tone="green">connected</Badge>} />
            <Row k="Aplikacja Stasis" v={<span className="font-mono">adam-stasis</span>} />
            <Row k="Kodek" v="Opus 48 kHz" />
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="font-serif text-h4 text-granat-900 flex items-center gap-2">
              <Puzzle size={18} className="text-granat-500" /> Moduły
            </h3>
          </CardHeader>
          <CardBody>
            <ul className="space-y-2">
              {a.modules.map((m) => (
                <li key={m} className="flex items-center justify-between py-1.5 border-b border-line last:border-0">
                  <span className="font-mono text-caption text-granat-900">{m}</span>
                  <Badge tone="green">
                    <CheckCircle2 size={11} className="mr-1 inline" /> loaded
                  </Badge>
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>
      </div>
    </>
  )
}

function Row({ k, v }: { k: string; v: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-line last:border-0">
      <span className="text-ink-400">{k}</span>
      <span className="text-ink-700 font-medium">{v}</span>
    </div>
  )
}
