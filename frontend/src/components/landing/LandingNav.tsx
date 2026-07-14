import { ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui'

const LINKS = [
  { href: '#chapter-01', label: 'Historia' },
  { href: '#chapter-02', label: 'Jak to działa' },
  { href: '#chapter-03', label: 'Funkcje' },
  { href: '#pricing', label: 'Cennik' },
  { href: '#footer', label: 'Kontakt' },
]

export function LandingNav({ onLogin, onOrder }: { onLogin?: () => void; onOrder?: () => void }) {
  return (
    <nav className="sticky top-0 z-50 bg-paper/85 backdrop-blur-md border-b border-line">
      <div className="container-tight flex items-center justify-between py-4">
        <a href="#top" className="flex items-center gap-3">
          <span className="relative grid place-items-center w-8 h-8 rounded-md bg-granat-700">
            <span className="absolute inset-1 border border-zloto-500 rounded-[3px]" />
            <span className="relative font-serif text-zloto-500 text-body font-medium">A</span>
          </span>
          <span className="leading-none">
            <span className="block font-serif text-h4 text-granat-900">Adam</span>
            <span className="block font-mono text-[9px] tracking-[0.14em] text-ink-500 uppercase mt-0.5">
              SilverTech · Poznań
            </span>
          </span>
        </a>

        <div className="hidden md:flex items-center gap-8 text-body text-ink-700">
          {LINKS.map((l) => (
            <a key={l.href} href={l.href} className="hover:text-granat-900 transition-colors">
              {l.label}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <button onClick={onLogin} className="hidden sm:inline text-body text-granat-900 hover:text-zloto-700 transition-colors">
            Zaloguj
          </button>
          <Button variant="gold" size="sm" onClick={onOrder}>
            Zamów Adama <ArrowRight size={15} />
          </Button>
        </div>
      </div>
    </nav>
  )
}
