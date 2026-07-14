import { Check, ArrowRight } from 'lucide-react'
import { cn } from '@/lib/cn'
import { Button } from '@/components/ui'
import { ChapterHead } from './ChapterHead'

const TIERS = [
  {
    name: 'Podstawowy',
    tagline: 'Codzienna rozmowa i raport.',
    price: '49',
    desc: 'Dla rodzin, które chcą wiedzieć, że u mamy wszystko dobrze — bez alarmów krytycznych.',
    cta: 'Zacznij 14 dni gratis',
    variant: 'secondary' as const,
    features: [
      'Welfare check 2× dziennie',
      'Panel Opiekuna (2 osoby)',
      'Semafor Green / Yellow',
      'Raport tygodniowy PDF',
      'Przypomnienia o lekach',
    ],
  },
  {
    name: 'Rodzinny',
    tagline: 'Pełna ochrona + alerty krytyczne.',
    price: '79',
    desc: 'Wybór 7 na 10 rodzin. Semafor Red i Purple + integracja z opaską.',
    cta: 'Zacznij 14 dni gratis',
    variant: 'gold' as const,
    featured: true,
    features: [
      'Wszystko z Podstawowego',
      'Semafor Red + Purple + auto-112',
      'Xiaomi / Apple / Garmin',
      'Do 5 opiekunów',
      'SMS alarm w 18s',
      'Aplikacja iOS + Android',
    ],
  },
  {
    name: 'Premium',
    tagline: 'Concierge i koordynator.',
    price: '119',
    desc: 'Dla rodzin z seniorem samotnym lub przewlekle chorym. Człowiek 24/7.',
    cta: 'Umów konsultację',
    variant: 'secondary' as const,
    features: [
      'Wszystko z Rodzinnego',
      'Concierge — zamawianie usług',
      'Dedykowany koordynator',
      'Raport dla lekarza',
      'Nielimitowani opiekunowie',
      'Priorytetowe SLA',
    ],
  },
]

export function Pricing({ onOrder }: { onOrder?: () => void }) {
  return (
    <section id="pricing" className="py-28 scroll-mt-20">
      <div className="container-tight">
        <ChapterHead
          num="04"
          label="Cennik · Trzy pakiety"
          title={
            <>
              Bez umowy. <br />
              <em className="italic text-zloto-700">Zawsze możesz odejść.</em>
            </>
          }
        />

        <div className="grid md:grid-cols-3 gap-6 items-start">
          {TIERS.map((t) => (
            <div
              key={t.name}
              className={cn(
                'rounded-xl border p-8 flex flex-col',
                t.featured
                  ? 'bg-granat-900 border-granat-800 text-paper md:-mt-4 md:mb-4 shadow-e4'
                  : 'bg-white border-line text-granat-900',
              )}
            >
              {t.featured && (
                <span className="self-start font-mono text-caption tracking-[0.14em] uppercase text-granat-900 bg-zloto-500 rounded-full px-3 py-1 mb-4">
                  Najpopularniejszy
                </span>
              )}
              <h3 className={cn('font-serif text-h3', t.featured ? 'text-white' : 'text-granat-900')}>{t.name}</h3>
              <p className={cn('font-serif italic text-body-l mt-1', t.featured ? 'text-zloto-400' : 'text-zloto-700')}>
                {t.tagline}
              </p>
              <div className="flex items-baseline gap-1 mt-6">
                <span className={cn('kpi text-[64px]', t.featured ? 'text-white' : 'text-granat-900')}>{t.price}</span>
                <span className={cn('text-body', t.featured ? 'text-white/60' : 'text-ink-500')}>zł / miesiąc</span>
              </div>
              <p className={cn('text-body mt-4 leading-relaxed', t.featured ? 'text-white/75' : 'text-ink-700')}>{t.desc}</p>

              <Button variant={t.variant} size="lg" fullWidth className="mt-6" onClick={onOrder}>
                {t.cta} <ArrowRight size={16} />
              </Button>

              <ul className="space-y-3 mt-8">
                {t.features.map((f) => (
                  <li key={f} className={cn('flex items-start gap-2 text-body', t.featured ? 'text-white/85' : 'text-ink-700')}>
                    <Check size={16} className={cn('mt-0.5 shrink-0', t.featured ? 'text-zloto-400' : 'text-sem-green')} />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
