import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Phone, Watch, Pill, Activity } from 'lucide-react'
import { AdminPageHead, StatTile } from '@/components/admin'
import { Card, CardBody, SemaphoreBadge, PackageBadge, Button, Avatar } from '@/components/ui'
import { ADMIN_SENIORS } from '@/data/mockAdmin'
import type { SemaphoreLevel, Package } from '@/types/domain'

export function AdminSeniorDetail() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const senior = ADMIN_SENIORS.find((s) => s.id === id) ?? ADMIN_SENIORS[0]
  const [first, last] = senior.name.split(' ')

  return (
    <>
      <button onClick={() => navigate('/admin/seniors')} className="inline-flex items-center gap-1.5 text-label text-ink-500 hover:text-granat-700 mb-4">
        <ArrowLeft size={15} /> Powrót do listy
      </button>

      <AdminPageHead
        eyebrow={`Senior · ${senior.id}`}
        title={senior.name}
        subtitle={`${senior.age} lat · ${senior.district} · koordynator: ${senior.coordinator}`}
        actions={<Button variant="primary"><Phone size={16} /> Zainicjuj rozmowę</Button>}
      />

      <Card className="mb-6">
        <CardBody className="flex flex-wrap items-center gap-5">
          <Avatar firstName={first} lastName={last ?? ''} size="xl" pulse={senior.semaphore === 'red' ? 'red' : senior.semaphore === 'purple' ? 'purple' : 'none'} />
          <div className="flex flex-wrap items-center gap-3">
            <SemaphoreBadge level={senior.semaphore as SemaphoreLevel} size="sm" />
            <PackageBadge package={senior.package as Package} />
          </div>
        </CardBody>
      </Card>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatTile label="Adherencja leków" value={senior.adherence} unit="%" icon={<Pill size={18} />} accent={senior.adherence < 70 ? 'red' : 'green'} />
        <StatTile label="Ostatnia rozmowa" value={senior.lastCall} icon={<Phone size={18} />} accent="granat" />
        <StatTile label="Wearable" value="Sparowany" icon={<Watch size={18} />} accent="granat" />
        <StatTile label="Status" value="Aktywny" icon={<Activity size={18} />} accent="green" />
      </div>

      <Card>
        <CardBody>
          <span className="eyebrow">Renderer szczegółów</span>
          <h3 className="text-h4 font-serif text-granat-900 mt-1">DETAIL_RENDERERS.senior</h3>
          <p className="text-body text-ink-500 mt-2 max-w-2xl">
            Pełny profil administracyjny łączy dane z Panelu Opiekuna (rozmowy, leki, wearable, alerty, RODO)
            z metadanymi operacyjnymi: przypisany agent, pipeline, profil audio, historia eskalacji semafora
            oraz audit trail dostępu.
          </p>
        </CardBody>
      </Card>
    </>
  )
}
