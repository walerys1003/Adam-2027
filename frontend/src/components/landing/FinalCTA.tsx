import { ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui'

export function FinalCTA({ onOrder }: { onOrder?: () => void }) {
  return (
    <section className="py-28 bg-paper-2">
      <div className="container-tight text-center max-w-3xl mx-auto">
        <p className="font-mono text-caption tracking-[0.16em] uppercase text-ink-500 mb-6">Fin.</p>
        <h2 className="font-serif font-normal text-[clamp(36px,6vw,64px)] leading-[1.02] tracking-[-0.03em] text-granat-900">
          Twój bliski zasługuje <br />
          <em className="italic text-zloto-700">na codzienną rozmowę.</em>
        </h2>
        <p className="text-body-l text-ink-700 mt-6">
          14 dni gratis. Bez karty. Bez umowy. Adam dzwoni jutro rano.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3 mt-8">
          <Button variant="primary" size="lg" onClick={onOrder}>
            Zamów Adama <ArrowRight size={16} />
          </Button>
          <Button variant="secondary" size="lg">
            Umów konsultację
          </Button>
        </div>
      </div>
    </section>
  )
}
