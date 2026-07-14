import { useEffect, useState } from 'react'
import { useRegisterSW } from 'virtual:pwa-register/react'
import { Download, X, RefreshCw, WifiOff } from 'lucide-react'
import { cn } from '@/lib/cn'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

const DISMISS_KEY = 'adam.pwa.install.dismissed'

export function InstallPrompt() {
  // --- Service Worker update lifecycle ---
  const {
    offlineReady: [offlineReady, setOfflineReady],
    needRefresh: [needRefresh, setNeedRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    onRegisteredSW(url) {
      // eslint-disable-next-line no-console
      console.info('[PWA] Service Worker zarejestrowany:', url)
    },
  })

  // --- Install (A2HS) prompt ---
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(null)
  const [showInstall, setShowInstall] = useState(false)

  useEffect(() => {
    const dismissed = localStorage.getItem(DISMISS_KEY) === '1'
    const handler = (e: Event) => {
      e.preventDefault()
      setDeferred(e as BeforeInstallPromptEvent)
      if (!dismissed) setShowInstall(true)
    }
    window.addEventListener('beforeinstallprompt', handler)
    window.addEventListener('appinstalled', () => setShowInstall(false))
    return () => window.removeEventListener('beforeinstallprompt', handler)
  }, [])

  const install = async () => {
    if (!deferred) return
    await deferred.prompt()
    await deferred.userChoice
    setDeferred(null)
    setShowInstall(false)
  }

  const dismissInstall = () => {
    localStorage.setItem(DISMISS_KEY, '1')
    setShowInstall(false)
  }

  const closeToast = () => {
    setOfflineReady(false)
    setNeedRefresh(false)
  }

  return (
    <>
      {/* Toast: aktualizacja / gotowość offline */}
      {(offlineReady || needRefresh) && (
        <div
          role="status"
          className="fixed bottom-4 left-1/2 -translate-x-1/2 z-[60] w-[calc(100%-2rem)] max-w-md animate-fade-in"
        >
          <div className="adam-card shadow-e3 flex items-start gap-3 p-4">
            <span
              className={cn(
                'w-9 h-9 rounded-md flex items-center justify-center shrink-0',
                needRefresh ? 'bg-zloto-50 text-zloto-700' : 'bg-sem-green-bg text-sem-green',
              )}
            >
              {needRefresh ? <RefreshCw size={18} /> : <WifiOff size={18} />}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-body font-medium text-granat-900">
                {needRefresh ? 'Dostępna nowa wersja Adama' : 'Adam działa offline'}
              </p>
              <p className="text-caption text-ink-500 mt-0.5">
                {needRefresh
                  ? 'Odśwież, aby załadować najnowszą wersję aplikacji.'
                  : 'Panel został zapisany do użytku bez połączenia z internetem.'}
              </p>
              {needRefresh && (
                <button
                  onClick={() => updateServiceWorker(true)}
                  className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-granat-700 text-white px-3 py-1.5 text-label font-medium hover:bg-granat-800"
                >
                  <RefreshCw size={13} /> Odśwież teraz
                </button>
              )}
            </div>
            <button onClick={closeToast} className="text-ink-400 hover:text-granat-700 shrink-0" aria-label="Zamknij">
              <X size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Banner instalacji na ekranie głównym */}
      {showInstall && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-[55] w-[calc(100%-2rem)] max-w-md animate-fade-in">
          <div className="adam-card shadow-e3 border-l-4 border-l-zloto-500 flex items-start gap-3 p-4">
            <span className="w-9 h-9 rounded-md bg-granat-50 text-granat-700 flex items-center justify-center shrink-0">
              <Download size={18} />
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-body font-medium text-granat-900">Zainstaluj Adama</p>
              <p className="text-caption text-ink-500 mt-0.5">
                Dodaj panel do ekranu głównego — szybki dostęp i tryb offline.
              </p>
              <div className="mt-2 flex items-center gap-2">
                <button
                  onClick={install}
                  className="inline-flex items-center gap-1.5 rounded-md bg-granat-700 text-white px-3 py-1.5 text-label font-medium hover:bg-granat-800"
                >
                  <Download size={13} /> Zainstaluj
                </button>
                <button
                  onClick={dismissInstall}
                  className="rounded-md px-3 py-1.5 text-label font-medium text-ink-500 hover:text-granat-700 hover:bg-granat-50"
                >
                  Nie teraz
                </button>
              </div>
            </div>
            <button onClick={dismissInstall} className="text-ink-400 hover:text-granat-700 shrink-0" aria-label="Zamknij">
              <X size={16} />
            </button>
          </div>
        </div>
      )}
    </>
  )
}
