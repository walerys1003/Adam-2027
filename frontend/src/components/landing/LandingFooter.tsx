const COLUMNS = [
  {
    heading: 'Produkt',
    links: ['Jak to działa', 'Funkcje', 'Cennik', 'iOS · Android'],
  },
  {
    heading: 'SilverTech',
    links: ['O nas', 'Zespół medyczny', 'Kariera', 'Blog'],
  },
  {
    heading: 'Wsparcie',
    links: ['Kontakt', 'FAQ', 'Status systemu', 'Dokumentacja'],
  },
  {
    heading: 'Prawne',
    links: ['RODO / GDPR', 'AI Act', 'Regulamin', 'Polityka prywatności'],
  },
]

export function LandingFooter() {
  return (
    <footer id="footer" className="bg-granat-950 text-paper/80 pt-16 pb-8 scroll-mt-20">
      <div className="container-tight">
        <div className="grid md:grid-cols-[1.5fr_repeat(4,1fr)] gap-10">
          {/* brand */}
          <div>
            <div className="flex items-center gap-3">
              <span className="relative grid place-items-center w-9 h-9 rounded-md bg-granat-700">
                <span className="absolute inset-1 border border-zloto-500 rounded-[3px]" />
                <span className="relative font-serif text-zloto-500 text-body font-medium">A</span>
              </span>
              <span className="leading-none">
                <span className="block font-serif text-h4 text-white">Adam</span>
                <span className="block font-mono text-[9px] tracking-[0.14em] text-paper/50 uppercase mt-0.5">
                  SilverTech · Poznań
                </span>
              </span>
            </div>
            <p className="font-serif italic text-body-l text-paper/70 mt-6 max-w-sm leading-snug">
              „Adam nie jest aplikacją. Jest codzienną praktyką opieki."
            </p>
            <p className="text-caption text-paper/40 mt-6 leading-relaxed">
              ul. Święty Marcin 24, 61-805 Poznań<br />
              +48 61 22 44 000 · kontakt@silvertech.pl<br />
              SilverTech Sp. z o.o. · NIP 783-123-45-67
            </p>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.heading}>
              <h3 className="font-mono text-caption tracking-[0.14em] uppercase text-zloto-400 mb-4">{col.heading}</h3>
              <ul className="space-y-2.5">
                {col.links.map((l) => (
                  <li key={l}>
                    <a href="#" className="text-body text-paper/70 hover:text-white transition-colors">
                      {l}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-14 pt-6 border-t border-white/10 text-caption text-paper/40">
          <span>© 2026 SilverTech Sp. z o.o. Wszystkie prawa zastrzeżone.</span>
          <span className="font-mono tracking-wide">Adam v7.4.2 · zbudowano w Poznaniu</span>
        </div>
      </div>
    </footer>
  )
}
