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
  photo?: string
}

const FEATURES: Feature[] = [
  {
    n: '01',
    icon: <Mic size={22} />,
    title: 'Rozpoznaje ton głosu, nie tylko słowa.',
    body: 'Model językowy Adama fine-tunowany na 200+ godzinach mowy senioralnej z Wielkopolski. Rozumie „ale coś dziś słabo” i wie, że to nie żart. Analiza pitchu, tempa, pauz — 14+ sygnałów kryzysu wychwyconych w tle zwykłej rozmowy.',
    wide: true,
    dark: true,
  },
  { n: '02', icon: <Pill size={22} />, title: 'Przypomina o lekach.', body: 'Metformina, amlodypina, insulina. Adam zna schemat, dopytuje o wzięcie i notuje adherence — dzień po dniu.' },
  { n: '03', icon: <Siren size={22} />, title: 'Alarm w 18 sekund.', body: '4-poziomowy semafor eskalacji: Green, Yellow, Red, Purple. Przy zagrożeniu życia Adam sam wybiera 112 i podaje adres, wiek oraz dane medyczne.' },
  {
    n: '04',
    icon: <Watch size={22} />,
    title: 'Xiaomi. Apple. Garmin. Wszystko.',
    body: 'Integracja z opaskami i zegarkami: tętno, SpO₂, wykrycie upadku, sen. Adam najpierw pyta o kontekst — nie wysyła alarmu przy porannym spacerze z tętnem 130.',
    wide: true,
    photo: '/images/landing/feature-smartband.jpg',
  },
  { n: '05', icon: <ShoppingBag size={22} />, title: 'Concierge · marketplace.', body: 'Lekarz domowy, taxi, apteka, sprzątanie, pielęgniarka. 10 kategorii, 80+ zweryfikowanych partnerów Poznania — jednym poleceniem głosowym.' },
  {
    n: '06',
    icon: <FileText size={22} />,
    title: 'Raporty jak od geriatry.',
    body: 'Krótki dzienny wpis w aplikacji. Pełny tygodniowy PDF na e-mail. Miesięczne podsumowanie z trendami — w formacie HL7 FHIR, gotowe dla lekarza bez tłumaczenia.',
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
          sub="Każdej z tych funkcji nie wymyśliliśmy w burzy mózgów — wynegocjowaliśmy ją w rozmowach z prawdziwymi rodzinami."
        />

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map((f) => {
            // Photo feature — image as full background, text overlaid
            if (f.photo) {
              return (
                <article
                  key={f.n}
                  className="relative md:col-span-2 lg:col-span-2 rounded-lg overflow-hidden min-h-[240px] flex flex-col justify-end p-7 text-paper shadow-e2"
                >
                  <img src={f.photo} alt="" aria-hidden className="absolute inset-0 h-full w-full object-cover" loading="lazy" />
                  <span aria-hidden className="absolute inset-0" style={{ background: 'linear-gradient(90deg, rgba(14,26,46,0.92) 0%, rgba(14,26,46,0.6) 45%, rgba(14,26,46,0.15) 100%)' }} />
                  <div className="relative max-w-md">
                    <div className="flex items-center justify-between mb-4">
                      <span className="grid place-items-center w-11 h-11 rounded-md bg-white/10 text-zloto-400 backdrop-blur-sm">{f.icon}</span>
                      <span className="font-mono text-caption tracking-[0.14em] uppercase text-white/50">Funkcja / {f.n}</span>
                    </div>
                    <h3 className="font-serif text-h4 text-white">{f.title}</h3>
                    <p className="text-body leading-relaxed mt-3 text-white/80">{f.body}</p>
                  </div>
                </article>
              )
            }
            return (
              <article
                key={f.n}
                className={cn(
                  'group rounded-lg border p-7 flex flex-col transition-shadow duration-300 ease-adam-out',
                  f.wide && 'md:col-span-2 lg:col-span-2',
                  f.dark
                    ? 'bg-granat-900 border-granat-800 text-paper hover:shadow-gold'
                    : 'bg-white border-line text-granat-900 hover:shadow-e3 hover:border-line-strong',
                )}
              >
                <div className="flex items-center justify-between">
                  <span className={cn('grid place-items-center w-11 h-11 rounded-md transition-colors', f.dark ? 'bg-white/10 text-zloto-400' : 'bg-granat-50 text-granat-700 group-hover:bg-zloto-50 group-hover:text-zloto-700')}>
                    {f.icon}
                  </span>
                  <span className={cn('font-mono text-caption tracking-[0.14em] uppercase', f.dark ? 'text-white/50' : 'text-ink-400')}>
                    Funkcja / {f.n}
                  </span>
                </div>
                <h3 className={cn('font-serif text-h4 mt-5', f.dark ? 'text-white' : 'text-granat-900')}>{f.title}</h3>
                <p className={cn('text-body leading-relaxed mt-3', f.dark ? 'text-white/75' : 'text-ink-700')}>{f.body}</p>
              </article>
            )
          })}
        </div>
      </div>
    </section>
  )
}
