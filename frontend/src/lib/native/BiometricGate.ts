/**
 * BiometricGate — natywna weryfikacja biometryczna (Face ID / Touch ID / odcisk).
 *
 * Używane jako dodatkowa brama przy wejściu do Panelu Opiekuna/Admina
 * na urządzeniach natywnych. W web (PWA) zawsze zwraca `available: false`,
 * a `verify()` przepuszcza (fallback na logowanie hasłem/2FA).
 */
import { Capacitor } from '@capacitor/core'
import { NativeBiometric, BiometryType } from 'capacitor-native-biometric'

function isNative(): boolean {
  return Capacitor.isNativePlatform()
}

export interface BiometricStatus {
  available: boolean
  type: 'faceId' | 'touchId' | 'fingerprint' | 'none'
}

function mapType(t: BiometryType): BiometricStatus['type'] {
  switch (t) {
    case BiometryType.FACE_ID:
      return 'faceId'
    case BiometryType.TOUCH_ID:
      return 'touchId'
    case BiometryType.FINGERPRINT:
      return 'fingerprint'
    default:
      return 'none'
  }
}

export const BiometricGate = {
  /** Sprawdza dostępność biometrii na urządzeniu. */
  async status(): Promise<BiometricStatus> {
    if (!isNative()) return { available: false, type: 'none' }
    try {
      const res = await NativeBiometric.isAvailable()
      return { available: res.isAvailable, type: mapType(res.biometryType) }
    } catch {
      return { available: false, type: 'none' }
    }
  },

  /**
   * Prosi o weryfikację biometryczną.
   * W web zwraca `true` (brak biometrii → nie blokujemy, decyduje login+2FA).
   */
  async verify(reason = 'Potwierdź tożsamość, aby otworzyć panel Adam'): Promise<boolean> {
    if (!isNative()) return true
    try {
      await NativeBiometric.verifyIdentity({
        reason,
        title: 'Adam — weryfikacja',
        subtitle: 'SilverTech',
        description: reason,
        useFallback: true, // pozwól na kod urządzenia jako fallback
      })
      return true
    } catch {
      return false
    }
  },

  /** Zapisuje poświadczenia w bezpiecznym keychain/keystore (opcjonalne). */
  async saveCredentials(server: string, username: string, password: string): Promise<void> {
    if (!isNative()) return
    await NativeBiometric.setCredentials({ server, username, password }).catch(() => {})
  },
}
