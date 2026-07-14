import { ArrowRight, Play } from 'lucide-react'
import { Button } from '@/components/ui'

const META = [
  { k: '18', sub: 's', l: 'Alarm rodzina' },
  { k: '96', sub: '%', l: 'Adherence leków' },
  { k: '2', sub: '×', l: 'Dziennie welfare check' },
  { k: '49', sub: 'zł', l: 'Od tyle miesięcznie' },
]

export function Hero({ onOrder }: { onOrder?: () => void }) {
  return (
    <section id="top" className="relative overflow-hidden pt-10 pb-24">
      <div className="container-tight">
        <div className="grid lg:grid-cols-2 gap-16 items-end min-h-[600px]">
          {/* LEFT */}
          <div className="pt-12">
            <div className="flex items-center gap-5 font-mono text-caption text-ink-500 tracking-[0.12em] uppercase mb-10">
              <span className="font-serif italic text-body text-zloto-700 tracking-tight normal-case">Numer 01</span>
              <span className="h-px w-16 bg-line-strong" />
              <span>Codzienna opieka · Lipiec 2026</span>
            </div>

            <h1 className="font-serif font-normal text-granat-900 leading-[0.9] tracking-[-0.035em] text-[clamp(48px,8vw,96px)]">
              Codziennie <br />
              dzwoni do niej. <br />
              <span className="italic text-zloto-700 border-b-2 border-zloto-500 pb-1">Ty masz spokój.</span>
            </h1>

            <p className="font-serif italic font-light text-body-l text-ink-700 mt-9 max-w-[480px] leading-relaxed">
              Adam to głosowy asystent, który rozmawia z Twoją mamą jak zaufany sąsiad.
              Dwa razy dziennie. Bez ekranu, bez aplikacji, bez internetu po jej stronie.
            </p>

            <div className="flex flex-wrap items-center gap-3 mt-10">
              <Button variant="primary" size="lg" onClick={onOrder}>
                Poznaj Adama <ArrowRight size={16} />
              </Button>
              <button className="inline-flex items-center gap-2 text-body text-granat-900 hover:text-zloto-700 transition-colors">
                <span className="grid place-items-center w-8 h-8 rounded-full border border-granat-900">
                  <Play size={12} fill="currentColor" />
                </span>
                Posłuchaj rozmowy (0:42)
              </button>
            </div>

            <div className="flex flex-wrap gap-12 mt-16 pt-8 border-t border-line-strong">
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

          {/* RIGHT — editorial portrait placeholder */}
          <div className="relative h-[520px] lg:h-[640px]">
            <div
              className="absolute inset-0 lg:left-10 rounded overflow-hidden"
              style={{
                background:
                  'radial-gradient(ellipse at 35% 40%, rgba(200,150,62,0.28), transparent 55%), linear-gradient(160deg, #d8c9a8 0%, #a68d5f 30%, #5a4a2e 65%, #14213d 100%)',
              }}
            >
              <p className="absolute top-10 left-10 right-10 font-serif italic font-light text-h3 text-white/95 leading-snug tracking-tight drop-shadow-lg">
                <span className="text-zloto-500 text-6xl leading-none absolute -top-6 -left-3 opacity-60">“</span>
                Adam dzwoni codziennie o ósmej. Nie wiem, czy to komputer, ale zawsze pyta, jak spałam.
              </p>
              <div className="absolute bottom-6 left-6 right-6 flex justify-between items-end text-white/90">
                <span className="font-serif italic text-body">
                  <span className="not-italic font-medium text-zloto-300">Halina W.</span>, 78 lat · Wilda, Poznań
                </span>
                <span className="font-mono text-caption tracking-[0.14em] uppercase text-white/60 text-right">
                  Fot. placeholder<br />do wymiany
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
