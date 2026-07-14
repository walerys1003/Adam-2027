const ITEMS = [
  'Wykrywa samotność',
  'Przypomina o lekach',
  'Alarmuje rodzinę w 18 sekund',
  'Zna wielkopolski',
  'Bez smartfona, bez internetu',
]

export function SignoffStrip() {
  return (
    <div className="relative overflow-hidden bg-granat-900 text-paper py-10">
      <span className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-zloto-500 to-transparent opacity-70" />
      <div className="flex items-center gap-14 font-serif text-h4 whitespace-nowrap animate-[marquee_28s_linear_infinite] will-change-transform">
        {[...ITEMS, ...ITEMS].map((item, i) => (
          <span key={i} className="inline-flex items-center gap-14">
            {item}
            <span className="w-1.5 h-1.5 rounded-full bg-zloto-500 shrink-0" />
          </span>
        ))}
      </div>
      <style>{`@keyframes marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }`}</style>
    </div>
  )
}
