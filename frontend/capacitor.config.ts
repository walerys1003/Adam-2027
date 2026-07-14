import type { CapacitorConfig } from '@capacitor/cli'

/**
 * Konfiguracja Capacitor dla natywnych aplikacji Adam (iOS + Android).
 *
 * appId  : pl.silvertech.adam.caregiver  (Panel Opiekuna)
 * webDir : dist  (produkcyjny build Vite)
 *
 * Build .ipa/.aab wykonywany po stronie SilverTech — patrz docs/CAPACITOR-BUILD.md.
 */
const config: CapacitorConfig = {
  appId: 'pl.silvertech.adam.caregiver',
  appName: 'Adam',
  webDir: 'dist',
  backgroundColor: '#fbfaf7',
  loggingBehavior: 'production',
  plugins: {
    SplashScreen: {
      launchShowDuration: 1200,
      launchAutoHide: true,
      backgroundColor: '#1a2744', // granat-700 — brand
      showSpinner: false,
      androidScaleType: 'CENTER_CROP',
      splashImmersive: true,
      iosSpinnerStyle: 'small',
      spinnerColor: '#c8963e', // złoto-500 — accent
    },
    PushNotifications: {
      // Kanał krytyczny RED/PURPLE — dźwięk + wysoki priorytet (patrz NotificationService)
      presentationOptions: ['badge', 'sound', 'alert'],
    },
    LocalNotifications: {
      smallIcon: 'ic_stat_adam',
      iconColor: '#1a2744',
      sound: 'critical.wav',
    },
  },
  ios: {
    contentInset: 'always',
    backgroundColor: '#fbfaf7',
    // Critical Alerts entitlement wymaga zgody Apple — patrz docs/CAPACITOR-BUILD.md
  },
  android: {
    backgroundColor: '#fbfaf7',
    allowMixedContent: false,
  },
  // W środowisku deweloperskim można wskazać live-reload na host sandboxa:
  // server: { url: 'https://<host>', cleartext: false },
}

export default config
