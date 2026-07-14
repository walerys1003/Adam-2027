import { Avatar } from '@/components/ui'

export function Testimonial() {
  return (
    <section className="py-28 bg-granat-900 text-paper">
      <div className="container-tight">
        <span className="font-serif text-[120px] leading-none text-zloto-500/50 block">“</span>
        <blockquote className="font-serif font-light text-[clamp(28px,4vw,44px)] leading-tight text-white/95 -mt-8 max-w-4xl tracking-tight">
          Trzy miesiące używamy Adama. Mama myśli, że to miły pan z centrali telefonicznej. Ja wiem,
          że to system. Oboje jesteśmy <em className="italic text-zloto-400">szczęśliwi.</em>
        </blockquote>
        <div className="flex items-center gap-4 mt-10">
          <Avatar firstName="Magdalena" lastName="C." size="lg" />
          <div>
            <p className="font-serif text-h4 text-white">Magdalena C.</p>
            <p className="font-mono text-caption tracking-[0.12em] uppercase text-white/50 mt-1">
              Córka · Warszawa · Adam od kwietnia 2026
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
