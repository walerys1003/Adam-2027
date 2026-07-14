import { ArrowRight, Check } from 'lucide-react'
import { Button } from '@/components/ui'

const REASSURE = ['14 dni gratis', 'Bez karty', 'Bez umowy', 'Rezygnacja w każdej chwili']

export function FinalCTA({ onOrder }: { onOrder?: () => void }) {
  return (
    <section className="relative py-28 bg-paper-2 overflow-hidden">
      {/* ambient depth */}
      <div aria-hidden className="pointer-events-none absolute inset-0" style={{ background: 'radial-gradient(50% 60% at 50% 0%, rgba(200,150,62,0.08), transparent 70%)' }} />
      <span aria-hidden className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-line-strong to-transparent" />

      <div className="container-tight relative text-center max-w-3xl mx-auto">
        <p className="font-mono text-caption tracking-[0.16em] uppercase text-ink-500 mb-6">Fin. · Jeden telefon dzieli Was od spokoju</p>
        <h2 className="font-serif font-normal text-[clamp(36px,6vw,64px)] leading-[1.02] tracking-[-0.03em] text-granat-900">
          Twój bliski zasługuje <br />
          <em className="italic text-zloto-700">na codzienną rozmowę.</em>
        </h2>
        <p className="text-body-l text-ink-700 mt-6 max-w-xl mx-auto">
          Zamów dziś, a Adam zadzwoni jutro rano. Bez konfiguracji, bez sprzętu do instalacji —
          wystarczy zwykły telefon po stronie mamy.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-3 mt-9">
          <Button variant="primary" size="lg" onClick={onOrder}>
            Zamów Adama <ArrowRight size={16} />
          </Button>
          <Button variant="secondary" size="lg">
            Umów konsultację
          </Button>
        </div>

        <ul className="flex flex-wrap items-center justify-center gap-x-7 gap-y-2 mt-8">
          {REASSURE.map((r) => (
            <li key={r} className="inline-flex items-center gap-1.5 font-mono text-caption tracking-[0.08em] uppercase text-ink-500">
              <Check size={13} className="text-sem-green" />
              {r}
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
