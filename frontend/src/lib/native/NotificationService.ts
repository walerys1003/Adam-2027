/**
 * NotificationService — warstwa natywna powiadomień Adam (Capacitor).
 *
 * Obsługuje:
 *  - Push (APNs/FCM) z rejestracją tokena
 *  - Local notifications z kanałem KRYTYCZNYM dla semafora RED/PURPLE
 *    (dźwięk + wibracja + pełnoekranowy alert; na iOS wymaga entitlement
 *     „Critical Alerts" — patrz docs/CAPACITOR-BUILD.md)
 *
 * Bezpiecznie no-op w środowisku web (Capacitor.isNativePlatform() === false),
 * dzięki czemu ten sam kod działa w PWA i w aplikacji natywnej.
 */
import { Capacitor } from '@capacitor/core'
import { PushNotifications } from '@capacitor/push-notifications'
import {
  LocalNotifications,
  type LocalNotificationSchema,
} from '@capacitor/local-notifications'

export type SemaphoreLevel = 'green' | 'yellow' | 'red' | 'purple'

const CRITICAL_CHANNEL = 'adam_critical'
const STANDARD_CHANNEL = 'adam_standard'

function isNative(): boolean {
  return Capacitor.isNativePlatform()
}

export const NotificationService = {
  /** Inicjalizacja: kanały Android + prośba o uprawnienia + rejestracja push. */
  async init(onToken?: (token: string) => void): Promise<void> {
    if (!isNative()) return

    // Kanały powiadomień (Android 8+)
    await LocalNotifications.createChannel({
      id: CRITICAL_CHANNEL,
      name: 'Alerty krytyczne (Adam)',
      description: 'Semafor CZERWONY i FIOLETOWY — sytuacje wymagające natychmiastowej reakcji',
      importance: 5, // MAX
      visibility: 1,
      sound: 'critical.wav',
      vibration: true,
      lights: true,
      lightColor: '#a5121a',
    }).catch(() => {})

    await LocalNotifications.createChannel({
      id: STANDARD_CHANNEL,
      name: 'Powiadomienia Adam',
      description: 'Rozmowy, raporty, wiadomości',
      importance: 3,
      visibility: 1,
    }).catch(() => {})

    // Uprawnienia local + push
    await LocalNotifications.requestPermissions().catch(() => {})
    const perm = await PushNotifications.requestPermissions()
    if (perm.receive === 'granted') {
      await PushNotifications.register()
    }

    PushNotifications.addListener('registration', (token) => {
      onToken?.(token.value)
    })
    PushNotifications.addListener('registrationError', (err) => {
      // eslint-disable-next-line no-console
      console.error('[Push] błąd rejestracji:', err)
    })
  },

  /**
   * Powiadomienie lokalne o alercie semafora.
   * RED/PURPLE → kanał krytyczny (dźwięk + wibracja + full-screen).
   */
  async notifySemaphore(opts: {
    id?: number
    level: SemaphoreLevel
    seniorName: string
    message: string
  }): Promise<void> {
    if (!isNative()) return
    const critical = opts.level === 'red' || opts.level === 'purple'

    const notification: LocalNotificationSchema = {
      id: opts.id ?? Math.floor(Date.now() % 2147483647),
      title:
        opts.level === 'purple'
          ? `🚨 KRYZYS — ${opts.seniorName}`
          : opts.level === 'red'
            ? `⚠️ Alert — ${opts.seniorName}`
            : `Adam — ${opts.seniorName}`,
      body: opts.message,
      channelId: critical ? CRITICAL_CHANNEL : STANDARD_CHANNEL,
      sound: critical ? 'critical.wav' : undefined,
      ongoing: opts.level === 'purple',
      smallIcon: 'ic_stat_adam',
      extra: { level: opts.level, senior: opts.seniorName },
    }

    await LocalNotifications.schedule({ notifications: [notification] })
  },

  /** Nasłuch tapnięcia w powiadomienie (deep-link do seniora). */
  onNotificationTap(handler: (data: { level?: SemaphoreLevel; senior?: string }) => void): void {
    if (!isNative()) return
    LocalNotifications.addListener('localNotificationActionPerformed', (event) => {
      handler(event.notification.extra ?? {})
    })
    PushNotifications.addListener('pushNotificationActionPerformed', (event) => {
      handler(event.notification.data ?? {})
    })
  },
}
