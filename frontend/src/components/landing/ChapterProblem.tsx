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
          sub="85% dorosłych dzieci martwi się o samotnie mieszkających rodziców. Tylko 12% jest w stanie sprawdzić ich codziennie. To pęknięcie — nie luka technologiczna. Zaprojektowaliśmy Adama, żeby je wypełnić."
        />

        <div className="grid md:grid-cols-2 gap-12 md:gap-20 items-start">
          {/* image placeholder */}
          <div
            className="aspect-[4/5] rounded overflow-hidden relative"
            style={{
              background:
                'linear-gradient(150deg, #eeeadc 0%, #cfc9b8 45%, #8b98b3 100%)',
            }}
          >
            <div className="absolute bottom-5 left-5 right-5 text-granat-900/80">
              <p className="font-mono text-caption uppercase tracking-[0.14em]">Placeholder · do wymiany</p>
              <p className="font-serif italic text-body mt-1">
                Kadr niedzielny · rozmowa raz w tygodniu · trzy minuty
              </p>
            </div>
          </div>

          {/* narrative */}
          <div className="space-y-6">
            <p className="font-serif text-h3 leading-snug text-granat-900">
              <span className="float-left font-serif text-[72px] leading-[0.7] mr-3 mt-2 text-zloto-500">„</span>
              Dzwoniłam w niedziele. Mówiła że wszystko dobrze. Trzy tygodnie później dostałam
              telefon ze szpitala.
            </p>
            <p className="text-body text-ink-700 leading-relaxed">
              To zdanie usłyszeliśmy w wywiadach z rodzinami tylko w Wielkopolsce ponad czterdzieści
              razy. Zawsze ta sama struktura: „nie wiedziałam", „dowiedziałam się za późno",
              „myślałam, że wszystko dobrze". Nie z braku miłości — z braku czasu i systemu.
            </p>
            <p className="text-body text-ink-700 leading-relaxed">
              Zatrudnienie opiekunki to 4500 zł miesięcznie plus rekrutacja, plus kwestia zaufania.
              Aplikacje z guzikiem SOS wymagają, żeby senior nosił urządzenie, umiał je obsłużyć i
              pamiętał, że istnieje. Telefon co niedzielę — jak wyżej.
            </p>
            <p className="text-body text-ink-700 leading-relaxed">
              Adam wykonuje jedną rzecz, którą każdy z nas próbowałby wykonać ręcznie, gdyby miał
              czas: dzwoni. Codziennie. Rozmawia. Zauważa. Zapisuje. Powiadamia — Ciebie,
              koordynatora, w krytycznym przypadku 112.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
