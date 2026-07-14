import { ArrowRight, Play, Quote } from 'lucide-react'
import { Button } from '@/components/ui'

const META = [
  { k: '18', sub: 's', l: 'Alarm do rodziny' },
  { k: '96', sub: '%', l: 'Adherence leków' },
  { k: '2', sub: '×', l: 'Dziennie welfare check' },
  { k: '49', sub: 'zł', l: 'Od tyle miesięcznie' },
]

export function Hero({ onOrder }: { onOrder?: () => void }) {
  return (
    <section id="top" className="relative overflow-hidden pt-10 pb-24">
      {/* ambient depth — warm radial + hairline grid, kept in brand */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.55]"
        style={{
          background:
            'radial-gradient(60% 50% at 82% 18%, rgba(200,150,62,0.10), transparent 70%), radial-gradient(50% 40% at 8% 90%, rgba(20,33,61,0.06), transparent 70%)',
        }}
      />
      <span aria-hidden className="pointer-events-none absolute top-0 left-1/2 -translate-x-1/2 h-px w-[92%] max-w-[1180px] bg-gradient-to-r from-transparent via-line-strong to-transparent" />

      <div className="container-tight relative">
        <div className="grid lg:grid-cols-[1.05fr_0.95fr] gap-14 lg:gap-16 items-end min-h-[600px]">
          {/* LEFT */}
          <div className="pt-12">
            <div className="flex items-center gap-5 font-mono text-caption text-ink-500 tracking-[0.12em] uppercase mb-10">
              <span className="font-serif italic text-body text-zloto-700 tracking-tight normal-case">Numer 01</span>
              <span className="h-px w-16 bg-line-strong" />
              <span>Codzienna opieka · Poznań</span>
            </div>

            <h1 className="font-serif font-normal text-granat-900 leading-[0.9] tracking-[-0.035em] text-[clamp(48px,8vw,96px)]">
              Codziennie <br />
              dzwoni do niej. <br />
              <span className="relative inline-block italic text-zloto-700">
                Ty masz spokój.
                <span aria-hidden className="absolute -bottom-1 left-0 h-[2px] w-full bg-gradient-to-r from-zloto-500 to-zloto-500/0" />
              </span>
            </h1>

            <p className="font-serif italic font-light text-body-l text-ink-700 mt-9 max-w-[480px] leading-relaxed">
              Adam to głosowy asystent, który rozmawia z Twoją mamą jak zaufany sąsiad —
              dwa razy dziennie, spokojnie i bez pośpiechu. Bez ekranu, bez aplikacji,
              bez internetu po jej stronie.
            </p>

            <div className="flex flex-wrap items-center gap-3 mt-10">
              <Button variant="primary" size="lg" onClick={onOrder}>
                Poznaj Adama <ArrowRight size={16} />
              </Button>
              <button className="group inline-flex items-center gap-2 text-body text-granat-900 hover:text-zloto-700 transition-colors">
                <span className="grid place-items-center w-8 h-8 rounded-full border border-granat-900 group-hover:border-zloto-700 group-hover:bg-zloto-50 transition-colors">
                  <Play size={12} fill="currentColor" />
                </span>
                Posłuchaj rozmowy (0:42)
              </button>
            </div>

            <div className="flex flex-wrap gap-x-12 gap-y-8 mt-16 pt-8 border-t border-line-strong">
              {META.map((m) => (
                <div key={m.l}>
                  <div className="font-serif text-h2 text-granat-900 font-medium leading-none">
                    {m.k}
                    <sub className="font-serif text-h4 text-zloto-700 font-normal align-baseline ml-0.5">{m.sub}</sub>
                  </div>
                  <div className="font-mono text-caption tracking-[0.12em] text-ink-500 uppercase mt-2">{m.l}</div>
                </div>
              ))}
            </div>
          </div>

          {/* RIGHT — editorial portrait, real photo with layered depth */}
          <div className="relative h-[520px] lg:h-[660px]">
            {/* back plate — navy, offset for depth */}
            <div aria-hidden className="absolute inset-y-6 -right-2 left-16 rounded-lg bg-granat-900" />
            {/* gold hairline frame */}
            <div aria-hidden className="absolute inset-y-2 right-2 left-12 rounded-lg border border-zloto-500/40" />

            {/* photo */}
            <figure className="absolute inset-0 lg:left-10 rounded-lg overflow-hidden shadow-e4">
              <img
                src="/images/landing/hero-halina.jpg"
                alt="Pani Halina, 78 lat, rozmawia z Adamem przez telefon w swoim mieszkaniu na poznańskiej Wildzie"
                className="h-full w-full object-cover"
                loading="eager"
              />
              {/* navy scrim for text legibility */}
              <span
                aria-hidden
                className="absolute inset-0"
                style={{ background: 'linear-gradient(180deg, rgba(14,26,46,0.35) 0%, transparent 34%, transparent 52%, rgba(14,26,46,0.86) 100%)' }}
              />
              {/* pull-quote */}
              <figcaption className="absolute inset-x-0 bottom-0 p-7 lg:p-8 text-paper">
                <Quote size={26} className="text-zloto-400 mb-3" fill="currentColor" />
                <p className="font-serif italic font-light text-h4 lg:text-h3 leading-snug tracking-tight text-white/95">
                  Adam dzwoni codziennie o ósmej. Nie wiem, czy to komputer — ale zawsze pyta, jak spałam.
                </p>
                <div className="mt-5 flex items-end justify-between gap-4">
                  <span className="font-serif italic text-body text-white/85">
                    <span className="not-italic font-medium text-zloto-300">Halina W.</span>, 78 lat · Wilda, Poznań
                  </span>
                  <span className="font-mono text-caption tracking-[0.14em] uppercase text-white/45 text-right shrink-0">
                    Klientka<br />od 2026
                  </span>
                </div>
              </figcaption>
            </figure>

            {/* floating live badge — subtle "wow" detail */}
            <div className="absolute -top-3 right-4 lg:right-0 z-10 flex items-center gap-2 rounded-full bg-white/95 backdrop-blur px-4 py-2 shadow-e3 border border-line">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full rounded-full bg-sem-green opacity-70 animate-sem-pulse-ring" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-sem-green" />
              </span>
              <span className="font-mono text-caption tracking-[0.1em] uppercase text-granat-900">Semafor · Green</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
