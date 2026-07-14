/**
 * initNativeShell — jednorazowa inicjalizacja powłoki natywnej Capacitor.
 * Wywoływana z main.tsx. Bezpieczny no-op w środowisku web/PWA.
 */
import { Capacitor } from '@capacitor/core'
import { SplashScreen } from '@capacitor/splash-screen'
import { NotificationService } from './NotificationService'

export async function initNativeShell(): Promise<void> {
  if (!Capacitor.isNativePlatform()) return

  try {
    // Rejestracja powiadomień + kanałów krytycznych
    await NotificationService.init((token) => {
      // eslint-disable-next-line no-console
      console.info('[Push] token urządzenia:', token)
      // TODO(backend F): wyślij token do API rejestracji urządzeń
    })

    // Ukryj splash po zainicjowaniu aplikacji
    await SplashScreen.hide()
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('[NativeShell] init error:', err)
  }
}
