# Adam — Build natywny (Capacitor iOS + Android)

> **Zasada dzielenia pracy:** kod natywny (Capacitor, wtyczki, warstwa `src/lib/native/`)
> jest utrzymywany w tym repo. **Build binarny `.ipa` / `.aab` wykonuje zespół SilverTech**
> na macOS (iOS) i dowolnym OS z Android SDK (Android), ponieważ wymaga certyfikatów,
> kluczy podpisu i konta Apple Developer / Google Play.

---

## 1. Wymagania

| Platforma | Narzędzia |
|-----------|-----------|
| Wspólne   | Node 18+, npm, `npx cap` (Capacitor 6) |
| iOS       | macOS, Xcode 15+, CocoaPods (`sudo gem install cocoapods`), konto Apple Developer |
| Android   | Android Studio, JDK 17, Android SDK 34, Gradle 8 |

## 2. Konfiguracja aplikacji

- **appId:** `pl.silvertech.adam.caregiver`
- **appName:** `Adam`
- **webDir:** `dist` (produkcyjny build Vite)
- Plik: [`frontend/capacitor.config.ts`](../frontend/capacitor.config.ts)

Kolory brandowe: splash **granat `#1a2744`**, spinner **złoto `#c8963e`**, tło aplikacji `#fbfaf7`.

## 3. Przygotowanie buildu web

```bash
cd frontend
npm install
npm run build          # tworzy dist/ (zawiera też PWA: manifest + sw.js)
npx cap sync           # kopiuje dist/ + wtyczki do ios/ oraz android/
```

`cap sync` należy uruchamiać **po każdej** zmianie w kodzie web lub liście wtyczek.

## 4. Wtyczki natywne (zainstalowane)

| Wtyczka | Zastosowanie w Adam |
|---------|---------------------|
| `@capacitor/push-notifications` | Push APNs/FCM (alerty z backendu) |
| `@capacitor/local-notifications` | Kanał **krytyczny** RED/PURPLE (dźwięk + wibracja) |
| `@capacitor/splash-screen` | Ekran startowy granat + logo |
| `@capacitor/share` | Udostępnianie raportów PDF |
| `capacitor-native-biometric` | Face ID / Touch ID / odcisk — `BiometricGate` |

Warstwa TypeScript: [`frontend/src/lib/native/`](../frontend/src/lib/native/)
- `NotificationService.ts` — rejestracja push + `notifySemaphore()` (kanał krytyczny dla RED/PURPLE)
- `BiometricGate.ts` — `status()` / `verify()` (Face ID / odcisk)
- `initNativeShell.ts` — inicjalizacja z `main.tsx` (no-op w web)

## 5. iOS — build `.ipa`

```bash
cd frontend
npx cap open ios       # otwiera Xcode
```

W Xcode:
1. **Signing & Capabilities** → wybierz Team (konto Apple Developer SilverTech).
2. Dodaj capability **Push Notifications**.
3. Dodaj capability **Background Modes** → zaznacz *Remote notifications*.
4. **Critical Alerts** (semafor RED/PURPLE): wymaga specjalnego entitlementu
   `com.apple.developer.usernotifications.critical-alerts` — **należy złożyć wniosek do Apple**
   (https://developer.apple.com/contact/request/notifications-critical-alerts-entitlement/).
   Do czasu przyznania alerty krytyczne działają jako standardowe (bez ominięcia trybu cichego).
5. Skonfiguruj **APNs**: klucz `.p8` (Key ID + Team ID) w panelu backendu (placeholder `APNS_KEY_ID`, `APNS_TEAM_ID`).
6. **Product → Archive** → Distribute App → App Store Connect / Ad Hoc → generuje `.ipa`.

### Ikony / splash iOS
Zastąp assety w `ios/App/App/Assets.xcassets/` (AppIcon + Splash) — źródło: `frontend/public/icons/`.

## 6. Android — build `.aab`

```bash
cd frontend
npx cap open android   # otwiera Android Studio
```

W Android Studio / CLI:
1. **FCM**: umieść `google-services.json` w `android/app/` (placeholder — z konsoli Firebase SilverTech).
2. Kanał krytyczny `adam_critical` (importance MAX + `critical.wav`) tworzony automatycznie w `NotificationService.init()`.
3. Podpis release: skonfiguruj `keystore` w `android/app/build.gradle` (`signingConfigs.release`).
4. Build:
   ```bash
   cd android
   ./gradlew bundleRelease      # → android/app/build/outputs/bundle/release/app-release.aab
   ./gradlew assembleRelease    # → .apk (testy)
   ```

### Ikony / splash Android
Zastąp `android/app/src/main/res/mipmap-*/` (ikony) i `drawable/splash.png`.
Dźwięk krytyczny: `android/app/src/main/res/raw/critical.wav`.

## 7. Placeholdery kluczy (do uzupełnienia przez SilverTech)

| Klucz | Gdzie | Opis |
|-------|-------|------|
| `APNS_KEY_ID` / `APNS_TEAM_ID` / `.p8` | Backend + Apple | Push iOS |
| `google-services.json` | `android/app/` | Push Android (FCM) |
| Certyfikat dystrybucji iOS | Xcode | Podpis `.ipa` |
| `release.keystore` | `android/app/` | Podpis `.aab` |
| Critical Alerts entitlement | Apple wniosek | Ominięcie trybu cichego dla RED/PURPLE |

## 8. Aktualizacja aplikacji

Po zmianach w kodzie web:
```bash
cd frontend && npm run build && npx cap sync
```
Następnie ponownie zarchiwizuj (iOS) / zbuduj bundle (Android).

---

**Uwaga:** katalogi `ios/` i `android/` są wygenerowane przez `npx cap add`. Zawierają natywne
projekty, które SilverTech dostosowuje (podpisy, klucze). Nie usuwać — są wersjonowane w repo.
