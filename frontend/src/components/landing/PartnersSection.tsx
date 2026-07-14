import { ChapterHead } from './ChapterHead'
import { cn } from '@/lib/cn'

const PARTNERS = [
  { n: '01', emoji: '💊', name: 'DOZ · Apteka św. Marcin', desc: 'Dostawa metforminy w 45 minut · Wilda, Grunwald · 487 zamówień w tym miesiącu', featured: true, meta: ['NIP 783-123-45-67', 'OC ważne', '4.8 ★'] },
  { n: '02', emoji: '🚕', name: 'MPT Poznań', desc: 'Taxi medyczne · 687 zamówień 30d' },
  { n: '03', emoji: '🛒', name: 'Frisco.pl', desc: 'Zakupy · 412 zamówień 30d' },
  { n: '04', emoji: '👨‍⚕️', name: 'Dr Chmielewska POZ', desc: 'Lekarz domowy · Wilda + Jeżyce' },
  { n: '05', emoji: '🧑‍⚕️', name: 'Pielęgniarka M.L.', desc: 'Iniekcje · opatrunki · pobrania' },
  { n: '06', emoji: '🧹', name: 'CleanPoznań', desc: 'Sprzątanie · dedykowane seniorom' },
  { n: '07', emoji: '💪', name: 'FizjoDom', desc: 'Rehabilitant · fizjoterapia' },
  { n: '08', emoji: '💬', name: 'Psycholog M.N.', desc: 'Wsparcie psychologiczne' },
]

const STATS = [
  { k: '80+', l: 'Partnerów' },
  { k: '64/80', l: 'Lokalni Poznańscy' },
  { k: '100%', l: 'OC ważne · NIP zweryfikowane' },
  { k: '4.7 ★', l: 'Średnia ocena' },
]

export function PartnersSection() {
  return (
    <section className="py-28 bg-paper-2">
      <div className="container-tight">
        <ChapterHead
          num="Alt."
          label="Ekosystem · Lokalny biznes"
          title={
            <>
              Osiemdziesiąt rąk, <br />
              <em className="italic text-zloto-700">jeden Poznań.</em>
            </>
          }
          sub="Adam nie zamawia u anonimowych podwykonawców. Każdy z osiemdziesięciu partnerów SilverTech ma ważne OC, zweryfikowany NIP i historię pracy. 80% to lokalne firmy poznańskie — bo tylko lokalny partner wie, że pani Halina mieszka na trzecim piętrze bez windy."
        />

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {PARTNERS.map((p) => (
            <article
              key={p.n}
              className={cn(
                'rounded-lg border border-line bg-white p-5',
                p.featured && 'sm:col-span-2 border-zloto-300 bg-zloto-50/40',
              )}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-3xl">{p.emoji}</span>
                <span className="font-mono text-caption tracking-[0.14em] uppercase text-ink-400">
                  Partner / {p.n}{p.featured && ' · Featured'}
                </span>
              </div>
              <h3 className="font-serif text-h4 text-granat-900">{p.name}</h3>
              <p className="text-body text-ink-700 mt-2">{p.desc}</p>
              {p.meta && (
                <div className="flex flex-wrap gap-3 mt-4 font-mono text-caption text-ink-500 uppercase tracking-wide">
                  {p.meta.map((m) => (
                    <span key={m}>{m}</span>
                  ))}
                </div>
              )}
            </article>
          ))}
        </div>

        {/* manifest */}
        <div className="mt-8 rounded-lg bg-granat-900 text-paper p-8">
          <p className="font-mono text-caption tracking-[0.14em] uppercase text-zloto-400 mb-3">Manifest partnerski</p>
          <p className="font-serif italic text-h4 text-white/95 max-w-3xl leading-snug">
            „Każdy partner zostaje w ekosystemie tylko dopóki utrzymuje ocenę powyżej 4.5★ i zero
            skarg krytycznych. Bez wyjątków."
          </p>
          <p className="font-mono text-caption text-white/50 uppercase tracking-wide mt-3">
            SilverTech · Zasada #4 · Ekosystem
          </p>
        </div>

        {/* stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-10 pt-8 border-t border-line-strong">
          {STATS.map((s) => (
            <div key={s.l}>
              <div className="font-serif text-h2 text-granat-900 font-medium leading-none">{s.k}</div>
              <div className="font-mono text-caption tracking-[0.12em] uppercase text-ink-500 mt-2">{s.l}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
