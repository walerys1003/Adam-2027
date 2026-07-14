export function Testimonial() {
  return (
    <section className="relative py-28 bg-granat-900 text-paper overflow-hidden">
      {/* gold hairlines top & bottom */}
      <span aria-hidden className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-zloto-500/70 to-transparent" />
      <span aria-hidden className="absolute bottom-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-zloto-500/40 to-transparent" />
      {/* ambient warm glow */}
      <div aria-hidden className="pointer-events-none absolute -right-40 -top-20 h-[420px] w-[420px] rounded-full opacity-30" style={{ background: 'radial-gradient(circle, rgba(200,150,62,0.35), transparent 65%)' }} />

      <div className="container-tight relative">
        <div className="grid lg:grid-cols-[1fr_auto] gap-12 lg:gap-16 items-center">
          <div>
            <span className="font-serif text-[120px] leading-[0.5] text-zloto-500/45 block select-none">„</span>
            <blockquote className="font-serif font-light text-[clamp(28px,4vw,44px)] leading-tight text-white/95 mt-4 max-w-4xl tracking-tight">
              Trzy miesiące używamy Adama. Mama myśli, że to miły pan z centrali telefonicznej.
              Ja wiem, że to system. Oboje jesteśmy <em className="italic text-zloto-400">spokojni.</em>
            </blockquote>

            <div className="flex items-center gap-4 mt-10">
              <img
                src="/images/landing/testimonial-magdalena.jpg"
                alt="Magdalena C., córka klientki Adama"
                className="h-16 w-16 rounded-full object-cover ring-1 ring-zloto-500/50"
                loading="lazy"
              />
              <div>
                <p className="font-serif text-h4 text-white">Magdalena C.</p>
                <p className="font-mono text-caption tracking-[0.12em] uppercase text-white/50 mt-1">
                  Córka · Warszawa · Adam od kwietnia 2026
                </p>
              </div>
            </div>
          </div>

          {/* rating panel — quiet, editorial */}
          <div className="hidden lg:flex flex-col items-end gap-2 pl-10 border-l border-white/10">
            <span className="font-serif text-[64px] leading-none text-white">4.9</span>
            <span className="font-mono text-caption tracking-[0.14em] uppercase text-zloto-400">★★★★★</span>
            <span className="font-mono text-caption tracking-[0.12em] uppercase text-white/45 text-right max-w-[160px] leading-relaxed mt-1">
              Średnia ocena rodzin<br />po 90 dniach z Adamem
            </span>
          </div>
        </div>
      </div>
    </section>
  )
}
