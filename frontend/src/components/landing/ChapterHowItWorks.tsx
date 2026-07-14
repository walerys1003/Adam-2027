import { ChapterHead } from './ChapterHead'
import { SemaphoreBadge } from '@/components/ui'
import type { SemaphoreLevel } from '@/types/domain'

const CUTS: Array<{
  n: string
  time: string
  title: string
  intro: string
  body: string
  tags: string[]
  level: SemaphoreLevel
}> = [
  {
    n: '01',
    time: '08:00 · Dzień dobry, Pani Halino',
    title: 'Adam dzwoni. Rozmowa trwa 3 minuty 22 sekundy.',
    intro: '',
    body: 'Pyta o sen, ból, samopoczucie. Przypomina o metforminie. Notuje głośność, tempo mowy, mood. Wynik: semafor Green. Krótki zapis trafia do panelu córki — bez notyfikacji, bez wibracji, po prostu jest tam rano, gdy zajrzy.',
    tags: ['MOOD 0.72', 'LEKI 07:15 OK'],
    level: 'green',
  },
  {
    n: '02',
    time: '19:00 · Coś się zmieniło',
    title: 'Adam pyta, mama mówi „wnuki dawno nie dzwoniły".',
    intro: '',
    body: 'Sygnał samotności. Nie kryzys — ale zmiana tonu wobec tygodnia. Semafor przełącza się na Yellow. Córka dostaje delikatny push: „Mama wspomniała, że dawno się nie widzieliście. Może zadzwoń wieczorem." Bez alarmu, bez dramatyzmu.',
    tags: ['MOOD 0.42', 'SAMOTNOŚĆ WYKRYTA'],
    level: 'yellow',
  },
  {
    n: '03',
    time: '22:14 · Upadek. Adam reaguje.',
    title: 'Xiaomi Band 8 wykrywa gwałtowne przemieszczenie. Adam dzwoni.',
    intro: '',
    body: 'Nikt nie odbiera. Adam próbuje trzy razy w odstępie 20 sekund. Po ostatniej próbie: SMS do córki z lokalizacją i statusem, jednoczesne połączenie do koordynatora SilverTech. Jeśli koordynator w ciągu 40 sekund nie potwierdzi — Adam wybiera 112. Cała eskalacja: 78 sekund od upadku do karetki.',
    tags: ['UPADEK WYKRYTY', 'SMS RODZINA 18s', '112'],
    level: 'purple',
  },
]

export function ChapterHowItWorks() {
  return (
    <section id="chapter-02" className="py-28 bg-paper-2 scroll-mt-20">
      <div className="container-tight">
        <ChapterHead
          num="02"
          label="Historia · Rozdział drugi"
          title={
            <>
              Trzy ujęcia, <br />
              <em className="italic text-zloto-700">jednego dnia.</em>
            </>
          }
          sub="Wtorek, 12 lipca. Rano, wieczór, moment kryzysu. Tak wygląda dzień z Adamem po stronie seniora — i po stronie rodziny."
        />

        <div className="grid md:grid-cols-3 gap-6">
          {CUTS.map((cut) => (
            <article key={cut.n} className="adam-card p-6 flex flex-col">
              <div className="font-serif italic text-h2 text-zloto-500 leading-none">{cut.n}</div>
              <h3 className="font-serif text-h4 text-granat-900 mt-4">{cut.time}</h3>
              <p className="text-body font-medium text-granat-800 mt-3">{cut.title}</p>
              <p className="text-body text-ink-700 leading-relaxed mt-3 flex-1">{cut.body}</p>
              <div className="flex flex-wrap items-center gap-2 mt-5 pt-4 border-t border-line">
                <SemaphoreBadge level={cut.level} size="sm" />
                {cut.tags.map((t) => (
                  <span key={t} className="font-mono text-caption tracking-wide text-ink-500 uppercase">
                    {t}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
