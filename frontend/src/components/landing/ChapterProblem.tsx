import { ChapterHead } from './ChapterHead'

export function ChapterProblem() {
  return (
    <section id="chapter-01" className="py-28 scroll-mt-20">
      <div className="container-tight">
        <ChapterHead
          num="01"
          label="Historia · Rozdział pierwszy"
          title={
            <>
              Między troską, <br />
              <em className="italic text-zloto-700">a codziennością.</em>
            </>
          }
          sub="85% dorosłych dzieci martwi się o samotnie mieszkających rodziców. Tylko 12% jest w stanie sprawdzić ich codziennie. To nie luka technologiczna — to ciche pęknięcie w środku dnia. Adama zaprojektowaliśmy, żeby je wypełnić."
        />

        <div className="grid md:grid-cols-2 gap-12 md:gap-20 items-center">
          {/* image — real photo, layered editorial frame */}
          <figure className="relative">
            <div aria-hidden className="absolute -inset-3 rounded-lg bg-paper-3/60" />
            <div aria-hidden className="absolute -top-4 -left-4 h-24 w-24 border-t border-l border-zloto-500/50 rounded-tl-lg" />
            <div aria-hidden className="absolute -bottom-4 -right-4 h-24 w-24 border-b border-r border-zloto-500/50 rounded-br-lg" />
            <div className="relative aspect-[4/5] rounded-lg overflow-hidden shadow-e3">
              <img
                src="/images/landing/problem-daughter.jpg"
                alt="Dorosła córka spogląda na telefon, myśląc o mieszkającej samotnie mamie"
                className="h-full w-full object-cover"
                loading="lazy"
              />
              <span aria-hidden className="absolute inset-0" style={{ background: 'linear-gradient(180deg, transparent 55%, rgba(14,26,46,0.72) 100%)' }} />
              <figcaption className="absolute bottom-5 left-5 right-5 text-paper">
                <p className="font-mono text-caption uppercase tracking-[0.14em] text-zloto-300">Niedziela · 20:47</p>
                <p className="font-serif italic text-body-l mt-1 text-white/90 leading-snug">
                  „Mówiła, że wszystko dobrze. Uwierzyłam, bo chciałam.”
                </p>
              </figcaption>
            </div>
          </figure>

          {/* narrative */}
          <div className="space-y-6">
            <blockquote className="relative pl-2">
              <span aria-hidden className="absolute -left-2 -top-6 font-serif text-[96px] leading-[0.6] text-zloto-500/70 select-none">„</span>
              <p className="font-serif text-h3 leading-snug text-granat-900 relative">
                Dzwoniłam w niedziele. Zawsze mówiła, że wszystko dobrze. Trzy tygodnie później
                odebrałam telefon ze szpitala.
              </p>
            </blockquote>
            <p className="text-body text-ink-700 leading-relaxed">
              To zdanie usłyszeliśmy w Wielkopolsce ponad czterdzieści razy — zawsze w tej samej
              tonacji: <em className="text-granat-800 not-italic font-medium">„nie wiedziałam”, „dowiedziałam się za późno”, „myślałam, że wszystko gra”</em>.
              Nie z braku miłości. Z braku czasu i systemu, który sam by zapytał.
            </p>
            <div className="grid gap-px overflow-hidden rounded-lg border border-line bg-line">
              <div className="bg-white p-4">
                <span className="font-serif text-h4 text-granat-900">4 500 zł / mies.</span>
                <span className="block font-mono text-caption uppercase tracking-wide text-ink-500 mt-1">Opiekunka — plus rekrutacja i kwestia zaufania</span>
              </div>
              <div className="bg-white p-4">
                <span className="font-serif text-h4 text-granat-900">Guzik SOS</span>
                <span className="block font-mono text-caption uppercase tracking-wide text-ink-500 mt-1">Wymaga, by senior go nosił, umiał obsłużyć i pamiętał</span>
              </div>
              <div className="bg-white p-4">
                <span className="font-serif text-h4 text-granat-900">Telefon co niedzielę</span>
                <span className="block font-mono text-caption uppercase tracking-wide text-ink-500 mt-1">Sześć dni ciszy pomiędzy</span>
              </div>
            </div>
            <p className="text-body text-ink-700 leading-relaxed">
              Adam robi jedną rzecz, którą każdy z nas próbowałby robić ręcznie — gdyby tylko miał
              czas. <em className="text-granat-800 not-italic font-medium">Dzwoni. Codziennie. Rozmawia. Zauważa. Zapisuje. Powiadamia</em> —
              Ciebie, koordynatora, a w krytycznym przypadku 112.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
