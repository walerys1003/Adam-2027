/* ============================================================
   ADAM · SkipLink (WP-3 · WCAG 2.4.1 Bypass Blocks)
   Link „Przejdź do treści” widoczny dopiero po sfokusowaniu (Tab).
   Pozwala pominąć nawigację i skoczyć do <main id="main-content">.
   ============================================================ */

export function SkipLink({ targetId = 'main-content' }: { targetId?: string }) {
  return (
    <a
      href={`#${targetId}`}
      className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[100] focus:rounded-md focus:bg-granat-700 focus:px-4 focus:py-2 focus:text-white focus:shadow-e3 focus:outline-none focus:ring-2 focus:ring-zloto-500"
    >
      Przejdź do treści
    </a>
  )
}
