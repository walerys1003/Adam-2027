import { Phone, MessageCircle, Mail, PlayCircle, Siren, CheckCircle2 } from 'lucide-react'
import { PageHead } from '@/components/panel/PageHead'
import { Card, CardBody, Button, Badge, Accordion } from '@/components/ui'
import type { AccordionItem } from '@/components/ui'

const CHANNELS = [
  { icon: Phone, title: 'Infolinia 24/7', detail: '+48 61 123 45 67', note: 'Śr. czas oczekiwania: 40 s', cta: 'Zadzwoń', variant: 'primary' as const },
  { icon: MessageCircle, title: 'Czat na żywo', detail: 'Pon–Pt 8:00–20:00', note: 'Konsultant online', cta: 'Rozpocznij czat', variant: 'secondary' as const },
  { icon: Mail, title: 'E-mail', detail: 'pomoc@silvertech.pl', note: 'Odpowiedź do 4 godz.', cta: 'Napisz', variant: 'ghost' as const },
]

const TUTORIALS = [
  { title: 'Pierwsze kroki z Adamem', len: '3:12' },
  { title: 'Jak czytać semafor', len: '2:40' },
  { title: 'Zamawianie w marketplace', len: '4:05' },
  { title: 'Parowanie opaski wearable', len: '5:20' },
]

const FAQ: AccordionItem[] = [
  { id: 'q1', question: 'Co oznaczają kolory semafora?', answer: 'Zielony — wszystko OK. Żółty — uwaga, obserwujemy. Czerwony — alarm, kontaktujemy się natychmiast. Fioletowy — zagrożenie życia, uruchamiamy protokół 112.' },
  { id: 'q2', question: 'Jak często Adam dzwoni do seniora?', answer: 'Domyślnie 2× dziennie (rano i wieczorem) w pakiecie Premium. Częstotliwość można dostosować w ustawieniach agenta.' },
  { id: 'q3', question: 'Czy rozmowy są nagrywane?', answer: 'Tak, za zgodą seniora (RODO art. 6 i 9). Nagrania służą wyłącznie analizie zdrowotnej i są szyfrowane. Zgodę można wycofać w każdej chwili.' },
  { id: 'q4', question: 'Co się dzieje przy alarmie czerwonym?', answer: 'Adam próbuje skontaktować się ponownie (3× co 20 s), następnie wysyła SMS do opiekuna i powiadamia koordynatora. Brak reakcji eskaluje do poziomu fioletowego.' },
  { id: 'q5', question: 'Jak anulować zamówienie?', answer: 'Każde zamówienie ma okno anulowania (zwykle 5–30 min). W zakładce Zamówienia widoczny jest licznik czasu i przycisk „Anuluj”.' },
  { id: 'q6', question: 'Czy mogę dodać kolejną osobę z rodziny?', answer: 'Tak — w widoku seniora, zakładka Rodzina, przycisk „Zaproś”. Możesz nadać dostęp pełny lub tylko do odczytu.' },
]

export function HelpPage() {
  return (
    <>
      <PageHead eyebrow="Wsparcie" title="Pomoc" subtitle="Kontakt, samouczki i najczęstsze pytania" />

      {/* Support status bar */}
      <Card className="mb-6">
        <CardBody className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <span className="inline-flex items-center gap-2 text-body text-granat-900">
            <CheckCircle2 size={18} className="text-sem-green" />
            Wszystkie systemy działają prawidłowo
          </span>
          <div className="flex items-center gap-2">
            <Badge tone="green">Telefonia OK</Badge>
            <Badge tone="green">AI OK</Badge>
            <Badge tone="green">Wearables OK</Badge>
          </div>
        </CardBody>
      </Card>

      {/* Emergency box */}
      <Card accent="red" className="mb-6">
        <CardBody className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <span className="w-10 h-10 rounded-md bg-sem-red-bg text-sem-red flex items-center justify-center shrink-0">
              <Siren size={20} />
            </span>
            <div>
              <h3 className="text-h4 font-serif text-granat-900">Sytuacja awaryjna?</h3>
              <p className="text-body text-ink-600 mt-0.5">
                W bezpośrednim zagrożeniu życia dzwoń <b>112</b>. Nasza infolinia kryzysowa działa całą dobę.
              </p>
            </div>
          </div>
          <div className="flex gap-2 shrink-0">
            <Button variant="danger"><Phone size={15} /> Zadzwoń 112</Button>
            <Button variant="secondary"><Phone size={15} /> Infolinia kryzysowa</Button>
          </div>
        </CardBody>
      </Card>

      {/* Support channels */}
      <div className="grid gap-4 sm:grid-cols-3 mb-6">
        {CHANNELS.map((c) => {
          const Icon = c.icon
          return (
            <Card key={c.title}>
              <CardBody>
                <span className="w-10 h-10 rounded-md bg-granat-50 text-granat-700 flex items-center justify-center">
                  <Icon size={19} />
                </span>
                <h3 className="text-body font-medium text-granat-900 mt-3">{c.title}</h3>
                <p className="text-body text-granat-800 mt-0.5">{c.detail}</p>
                <p className="text-caption text-ink-400">{c.note}</p>
                <Button variant={c.variant} size="sm" fullWidth className="mt-3">{c.cta}</Button>
              </CardBody>
            </Card>
          )
        })}
      </div>

      {/* Video tutorials */}
      <div className="mb-6">
        <h2 className="font-serif text-h4 text-granat-900 mb-3">Samouczki wideo</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {TUTORIALS.map((t) => (
            <Card key={t.title} interactive>
              <div className="aspect-video bg-gradient-to-br from-granat-700 to-granat-900 rounded-t-lg grid place-items-center relative">
                <PlayCircle size={40} className="text-zloto-400" />
                <span className="absolute bottom-2 right-2 text-caption text-white/80 bg-granat-900/60 rounded px-1.5">{t.len}</span>
              </div>
              <CardBody>
                <p className="text-body font-medium text-granat-900">{t.title}</p>
              </CardBody>
            </Card>
          ))}
        </div>
      </div>

      {/* FAQ */}
      <div>
        <h2 className="font-serif text-h4 text-granat-900 mb-3">Najczęstsze pytania</h2>
        <Accordion items={FAQ} defaultOpen="q1" />
      </div>
    </>
  )
}
