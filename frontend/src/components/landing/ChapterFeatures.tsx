import { Mic, Pill, Siren, Watch, ShoppingBag, FileText } from 'lucide-react'
import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import { ChapterHead } from './ChapterHead'

interface Feature {
  n: string
  icon: ReactNode
  title: string
  body: string
  wide?: boolean
  dark?: boolean
}

const FEATURES: Feature[] = [
  {
    n: '01',
    icon: <Mic size={22} />,
    title: 'Rozpoznaje ton głosu, nie tylko słowa.',
    body: 'Model językowy Adama fine-tunowany na 200+ godzinach mowy senioralnej z Wielkopolski. Rozumie „ale coś dziś słabo" i wie, że to nie żart. Analiza pitchu, tempa, pauz. 14+ sygnałów kryzysu wykrywanych w tle rozmowy.',
    wide: true,
    dark: true,
  },
  { n: '02', icon: <Pill size={22} />, title: 'Przypomina o lekach.', body: 'Metformina, amlodypina, insulina. Adam zna schemat, pyta o wzięcie, notuje adherence.' },
  { n: '03', icon: <Siren size={22} />, title: 'Alarm w 18 sekund.', body: '4-poziomowy semafor eskalacji: Green, Yellow, Red, Purple. Przy zagrożeniu życia Adam sam wykonuje połączenie 112 z podaniem adresu, wieku i danych medycznych.' },
  { n: '04', icon: <Watch size={22} />, title: 'Xiaomi. Apple. Garmin. Wszystko.', body: 'Integracja z opaskami i zegarkami. HR, SpO₂, wykrycie upadku, sen. Adam pyta o kontekst — nie wysyła alarmu przy porannym spacerze z tętnem 130.' },
  { n: '05', icon: <ShoppingBag size={22} />, title: 'Concierge · marketplace.', body: 'Lekarz domowy, taxi, apteka, sprzątanie, pielęgniarka. 10 kategorii, 80+ zweryfikowanych partnerów Poznania.' },
  {
    n: '06',
    icon: <FileText size={22} />,
    title: 'Raporty tygodniowe — jak od geriatry.',
    body: 'Krótki dzienny w aplikacji. Pełny tygodniowy PDF na e-mail. Miesięczne podsumowanie z trendami. Format zgodny z HL7 FHIR — do przekazania lekarzowi bez tłumaczenia.',
    wide: true,
  },
]

export function ChapterFeatures() {
  return (
    <section id="chapter-03" className="py-28 scroll-mt-20">
      <div className="container-tight">
        <ChapterHead
          num="03"
          label="Sześć funkcji"
          title={
            <>
              Nie aplikacja. <br />
              <em className="italic text-zloto-700">Codzienna praktyka.</em>
            </>
          }
          sub="Każdą z tych funkcji wynegocjowaliśmy z rodzinami w rozmowach — nie w burzy mózgów."
        />

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map((f) => (
            <article
              key={f.n}
              className={cn(
                'rounded-lg border p-7 flex flex-col',
                f.wide && 'md:col-span-2 lg:col-span-2',
                f.dark
                  ? 'bg-granat-900 border-granat-800 text-paper'
                  : 'bg-white border-line text-granat-900',
              )}
            >
              <div className="flex items-center justify-between">
                <span className={cn('grid place-items-center w-11 h-11 rounded-md', f.dark ? 'bg-white/10 text-zloto-400' : 'bg-granat-50 text-granat-700')}>
                  {f.icon}
                </span>
                <span className={cn('font-mono text-caption tracking-[0.14em] uppercase', f.dark ? 'text-white/50' : 'text-ink-400')}>
                  Funkcja / {f.n}
                </span>
              </div>
              <h3 className={cn('font-serif text-h4 mt-5', f.dark ? 'text-white' : 'text-granat-900')}>{f.title}</h3>
              <p className={cn('text-body leading-relaxed mt-3', f.dark ? 'text-white/75' : 'text-ink-700')}>{f.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
