🎯 GENSPARK AI DEVELOPER — PROMPT: KONWERSJA PWA → CAPACITOR (iOS + ANDROID)
Poniżej znajduje się jeden, kompletny prompt, który wklejasz do GenSpark AI Developer wraz z kodem frontendu. GenSpark wykona go krok po kroku.
═══════════════════════════════════════════════════════════════
ZADANIE: Konwersja PWA → Natywna aplikacja mobilna (Capacitor)
Projekt: Adam – Panel Opiekuna (SilverTech, Poznań)
Stack: React 18+ / TypeScript / Vite / Tailwind CSS
Cel: iOS (App Store) + Android (Google Play) z jednego kodu
═══════════════════════════════════════════════════════════════
KONTEKST:
Mam w pełni działającą aplikację webową React/TypeScript/Vite —
Panel Opiekuna dla systemu opieki nad seniorami "Adam". 
Aplikacja ma już wsparcie PWA (vite-plugin-pwa, manifest.json, 
Service Worker). Teraz potrzebuję opakować ją w Capacitor JS, 
żeby powstała natywna aplikacja iOS i Android gotowa do 
publikacji w App Store i Google Play.
KOD ŹRÓDŁOWY: [załączam folder frontend/]
═══════════════════════════════════════════════════════════════
KROK 1: INSTALACJA I INICJALIZACJA CAPACITOR
═══════════════════════════════════════════════════════════════
1.1. Zainstaluj pakiety:
    npm install @capacitor/core @capacitor/cli @capacitor/ios @capacitor/android
1.2. Zainicjuj Capacitor w projekcie:
    npx cap init "Adam Panel Opiekuna" "pl.silvertech.adam.caregiver" \
      --web-dir=dist --npm-client=npm
1.3. Dodaj platformy:
    npx cap add ios
    npx cap add android
1.4. Utwórz plik capacitor.config.ts w głównym katalogu projektu
     (obok vite.config.ts) z następującą zawartością:
     ```typescript
     import { CapacitorConfig } from '@capacitor/cli';
     const config: CapacitorConfig = {
       appId: 'pl.silvertech.adam.caregiver',
       appName: 'Adam – Opieka Seniora',
       webDir: 'dist',
       server: {
         // W produkcji: ładuj z URL (Twoja domena)
         // url: 'https://panel.silvertech.poznan.pl',
         // cleartext: false,
         // W trybie deweloperskim: ładuj z localhost
         // url: 'http://192.168.1.100:5173',
         // cleartext: true
         // Tryb offline (wszystko w apce):
         androidScheme: 'https',
       },
       plugins: {
         SplashScreen: {
           launchShowDuration: 2000,
           launchAutoHide: true,
           backgroundColor: '#1a2744',
           androidSplashResourceName: 'splash',
           androidScaleType: 'CENTER_CROP',
           showSpinner: false,
           splashFullScreen: true,
           splashImmersive: true,
         },
         PushNotifications: {
           presentationOptions: ['badge', 'sound', 'alert'],
         },
         LocalNotifications: {
           smallIcon: 'ic_stat_adam',
           iconColor: '#c8963e',
         },
       },
       ios: {
         contentInset: 'automatic',
         scheme: 'AdamPanel',
         // Dla App Store: minimum iOS 15
         minVersion: '15.0',
       },
       android: {
         // Dla Google Play: minimum Android 8 (API 26)
         minWebViewVersion: '60',
         allowMixedContent: false,
       },
     };
     export default config;
     ```
1.5. Zbuduj projekt webowy i zsynchronizuj z Capacitor:
    npm run build
    npx cap sync
═══════════════════════════════════════════════════════════════
KROK 2: PLUGINY — INSTALACJA I KONFIGURACJA
═══════════════════════════════════════════════════════════════
2.1. Zainstaluj wszystkie wymagane pluginy:
    npm install @capacitor/push-notifications
    npm install @capacitor/local-notifications
    npm install @capacitor/splash-screen
    npm install @capacitor/share
    npm install @capacitor/preferences
    npm install @capacitor/status-bar
    npm install @capacitor/app
    npm install @capacitor/device
    npm install @capacitor/network
2.2. UTWÓRZ PLIK: src/core/services/mobileBridge.ts
     To jest WARSTWA ABSTRAKCYJNA — jednolity interfejs, który działa:
     - w przeglądarce (web) → mockowane/alternatywne implementacje
     - w Capacitor (iOS/Android) → natywne API
     ```typescript
     /**
      * mobileBridge.ts
      * Warstwa abstrakcji między webem a natywną aplikacją.
      * Automatycznie wykrywa środowisko i używa odpowiedniej implementacji.
      */
     import { Capacitor } from '@capacitor/core';
     // === WYKRYWANIE ŚRODOWISKA ===
     export const isNative = Capacitor.isNativePlatform();
     export const platform = Capacitor.getPlatform(); // 'ios' | 'android' | 'web'
     // ============================================================
     // PUSH NOTIFICATIONS — alerty RED/PURPLE
     // ============================================================
     export async function initPushNotifications(onNotificationReceived: (data: any) => void) {
       if (!isNative) {
         // WEB: użyj Service Worker Push API (PWA)
         if ('serviceWorker' in navigator && 'PushManager' in window) {
           const registration = await navigator.serviceWorker.ready;
           const subscription = await registration.pushManager.subscribe({
             userVisibleOnly: true,
             applicationServerKey: urlBase64ToUint8Array(import.meta.env.VITE_VAPID_PUBLIC_KEY),
           });
           // Wyślij subscription na backend
           await fetch('/api/v1/notifications/register', {
             method: 'POST',
             headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
             body: JSON.stringify({ platform: 'web', subscription }),
           });
         }
         return;
       }
       // NATIVE: Capacitor Push Notifications
       const { PushNotifications } = await import('@capacitor/push-notifications');
       // Poproś o pozwolenie
       const permStatus = await PushNotifications.requestPermissions();
       if (permStatus.receive !== 'granted') {
         console.warn('[Adam] Push notifications denied');
         return;
       }
       // Zarejestruj się
       await PushNotifications.register();
       // Nasłuchuj zdarzeń
       PushNotifications.addListener('registration', async (token) => {
         console.log('[Adam] Push token:', token.value);
         // Wyślij token na backend
         await fetch('/api/v1/notifications/register', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
           body: JSON.stringify({ platform: platform, token: token.value }),
         });
       });
       PushNotifications.addListener('pushNotificationReceived', (notification) => {
         console.log('[Adam] Push received:', notification);
         // Jeśli apka jest otwarta — pokaż in-app toast
         onNotificationReceived(notification);
       });
       PushNotifications.addListener('pushNotificationActionPerformed', (action) => {
         console.log('[Adam] Push action:', action);
         // Nawiguj do odpowiedniego seniora
         if (action.notification.data.seniorId) {
           window.location.href = `/panel/senior/${action.notification.data.seniorId}`;
         }
       });
     }
     // ============================================================
     // LOCAL NOTIFICATIONS — przypomnienia (np. "czas sprawdzić leki")
     // ============================================================
     export async function scheduleLocalNotification(title: string, body: string, at: Date, data?: any) {
       if (!isNative) {
         // WEB: użyj Notification API (jeśli pozwolono)
         if ('Notification' in window && Notification.permission === 'granted') {
           const delayMs = at.getTime() - Date.now();
           if (delayMs > 0) {
             setTimeout(() => {
               new Notification(title, { body, data, icon: '/icons/icon-192.png' });
             }, delayMs);
           }
         }
         return;
       }
       const { LocalNotifications } = await import('@capacitor/local-notifications');
       await LocalNotifications.schedule({
         notifications: [{
           id: Date.now(),
           title,
           body,
           schedule: { at },
           extra: data,
         }],
       });
     }
     // ============================================================
     // SHARE — udostępnianie raportu PDF
     // ============================================================
     export async function shareContent(title: string, text: string, url?: string) {
       if (!isNative) {
         // WEB: Web Share API
         if (navigator.share) {
           await navigator.share({ title, text, url });
         } else {
           // Fallback: kopiuj do schowka
           await navigator.clipboard.writeText(`${title}\n${text}\n${url || ''}`);
           alert('Skopiowano do schowka');
         }
         return;
       }
       const { Share } = await import('@capacitor/share');
       await Share.share({ title, text, url });
     }
     // ============================================================
     // STATUS BAR — dopasowanie do theme (granatowy #1a2744)
     // ============================================================
     export async function configureStatusBar() {
       if (!isNative) {
         // WEB: meta tag theme-color (już ustawiony przez PWA manifest)
         return;
       }
       const { StatusBar } = await import('@capacitor/status-bar');
       await StatusBar.setStyle({ style: 'Dark' });
       await StatusBar.setBackgroundColor({ color: '#1a2744' });
     }
     // ============================================================
     // STORAGE — bezpieczne przechowywanie tokenu JWT
     // ============================================================
     export async function secureStore(key: string, value: string) {
       if (!isNative) {
         localStorage.setItem(`adam_${key}`, value);
         return;
       }
       const { Preferences } = await import('@capacitor/preferences');
       await Preferences.set({ key: `adam_${key}`, value });
     }
     export async function secureGet(key: string): Promise<string | null> {
       if (!isNative) {
         return localStorage.getItem(`adam_${key}`);
       }
       const { Preferences } = await import('@capacitor/preferences');
       const result = await Preferences.get({ key: `adam_${key}` });
       return result.value || null;
     }
     export async function secureRemove(key: string) {
       if (!isNative) {
         localStorage.removeItem(`adam_${key}`);
         return;
       }
       const { Preferences } = await import('@capacitor/preferences');
       await Preferences.remove({ key: `adam_${key}` });
     }
     // ============================================================
     // APP LIFECYCLE — co robić gdy apka w tle / wraca
     // ============================================================
     export function onAppStateChange(callback: (isActive: boolean) => void) {
       if (!isNative) {
         // WEB: visibilitychange
         document.addEventListener('visibilitychange', () => {
           callback(document.visibilityState === 'visible');
         });
         return;
       }
       import('@capacitor/app').then(({ App }) => {
         App.addListener('appStateChange', (state) => {
           callback(state.isActive);
         });
       });
     }
     // ============================================================
     // HELPER
     // ============================================================
     function urlBase64ToUint8Array(base64String: string): Uint8Array {
       const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
       const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
       const rawData = atob(base64);
       return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
     }
     function getToken(): string {
       return localStorage.getItem('adam_access_token') || '';
     }
     ```
2.3. UTWÓRZ PLIK: src/core/hooks/useMobileInit.ts
     Hook, który odpala się raz przy starcie apki, inicjuje wszystko:
     ```typescript
     import { useEffect } from 'react';
     import {
       initPushNotifications,
       configureStatusBar,
       onAppStateChange,
       isNative,
       platform,
     } from '../services/mobileBridge';
     export function useMobileInit() {
       useEffect(() => {
         console.log(`[Adam] Running on: ${platform}, native: ${isNative}`);
         // 1. Skonfiguruj status bar
         configureStatusBar();
         // 2. Zainicjuj push notifications
         initPushNotifications((data) => {
           // Pokazanie in-app toastu gdy apka otwarta
           // (użyj swojego systemu toastów)
           console.log('[Adam] In-app notification:', data);
         });
         // 3. Obsługa cyklu życia apki
         onAppStateChange((isActive) => {
           if (isActive) {
             // Odśwież dane gdy apka wraca z tła
             console.log('[Adam] App resumed — refreshing data...');
             // queryClient.invalidateQueries();
           }
         });
         // 4. Ukryj splash screen (już auto-hide po 2s z configu)
       }, []);
     }
     ```
2.4. WPIJ HOOK w głównym komponencie App.tsx:
     ```typescript
     import { useMobileInit } from './core/hooks/useMobileInit';
     function App() {
       useMobileInit(); // ← dodaj tę linię na początku komponentu
       // ... reszta aplikacji (AuthProvider, routing, itd.)
     }
     ```
═══════════════════════════════════════════════════════════════
KROK 3: SPLASH SCREEN I IKONY
═══════════════════════════════════════════════════════════════
3.1. Przygotuj folder resources/ (na poziomie głównym projektu, obok frontend/):
    resources/
    ├── icon.png          # 1024×1024 px — logo Adam (kwadratowe)
    ├── splash.png        # 2732×2732 px — tło splash (#1a2744) + logo Adam wyśrodkowane
    └── android/
        └── notification/
            └── ic_stat_adam.png   # 96×96 px — ikona powiadomień (białe logo na przezroczystym)
3.2. Zainstaluj generator assetów (automatyczne przycinanie ikon):
    npm install -D @capacitor/assets
3.3. Dodaj do package.json skrypt:
    ```json
    "scripts": {
      "assets:generate": "npx @capacitor/assets generate --iconBackgroundColor '#1a2744' --splashBackgroundColor '#1a2744'"
    }
    ```
3.4. Wygeneruj wszystkie rozmiary ikon i splash screenów:
    npm run assets:generate
    To automatycznie utworzy wszystkie potrzebne rozmiary:
    - iOS: AppIcon (20×20 do 1024×1024), LaunchImage
    - Android: mipmap-* (48×48 do 512×512), drawable-*
3.5. UTWÓRZ PLIK: src/main.tsx (modyfikacja — dodaj inicjalizację SplashScreen):
    ```typescript
    import React from 'react';
    import ReactDOM from 'react-dom/client';
    import App from './App';
    import './styles/globals.css';
    // Ukryj splash screen jak najszybciej
    import { Capacitor } from '@capacitor/core';
    if (Capacitor.isNativePlatform()) {
      import('@capacitor/splash-screen').then(({ SplashScreen }) => {
        // Auto-hide jest w config (2s), ale możemy przyspieszyć
        // SplashScreen.hide(); // odkomentuj jeśli chcesz ręcznie kontrolować
      });
    }
    ReactDOM.createRoot(document.getElementById('root')!).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>,
    );
    ```
═══════════════════════════════════════════════════════════════
KROK 4: KONFIGURACJA ANDROID
═══════════════════════════════════════════════════════════════
4.1. UTWÓRZ PLIK: android/app/src/main/res/values/styles.xml
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <resources>
        <!-- Base application theme -->
        <style name="AppTheme" parent="Theme.AppCompat.Light.NoActionBar">
            <item name="colorPrimary">#1a2744</item>
            <item name="colorPrimaryDark">#0f1a2e</item>
            <item name="colorAccent">#c8963e</item>
            <item name="android:statusBarColor">#1a2744</item>
            <item name="android:navigationBarColor">#1a2744</item>
        </style>
        <!-- Splash screen theme -->
        <style name="AppTheme.NoActionBarLaunch" parent="Theme.AppCompat.Light.NoActionBar">
            <item name="android:background">#1a2744</item>
            <item name="android:windowNoTitle">true</item>
            <item name="android:windowActionBar">false</item>
            <item name="android:windowFullscreen">true</item>
            <item name="android:windowContentOverlay">@null</item>
        </style>
    </resources>
    ```
4.2. Skonfiguruj AndroidManifest.xml — dodaj uprawnienia:
    W android/app/src/main/AndroidManifest.xml, wewnątrz <manifest> dodaj:
    ```xml
    <!-- Internet (domyślnie jest) -->
    <uses-permission android:name="android.permission.INTERNET" />
    <!-- Notifications (Android 13+) -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <!-- Vibration (dla powiadomień) -->
    <uses-permission android:name="android.permission.VIBRATE" />
    <!-- Biometryczne logowanie (opcjonalnie) -->
    <uses-permission android:name="android.permission.USE_BIOMETRIC" />
    ```
4.3. Skonfiguruj android/app/build.gradle — ustaw minSdkVersion i targetSdkVersion:
    ```gradle
    android {
        defaultConfig {
            minSdkVersion 26    // Android 8.0+
            targetSdkVersion 34 // Android 14
            versionCode 1
            versionName "1.0.0"
        }
    }
    ```
═══════════════════════════════════════════════════════════════
KROK 5: KONFIGURACJA iOS
═══════════════════════════════════════════════════════════════
5.1. UTWÓRZ PLIK: ios/App/App/Info.plist (dodaj wpisy):
    ```xml
    <!-- Opis użycia powiadomień (wymagane przez App Store) -->
    <key>NSUserNotificationUsageDescription</key>
    <string>Adam wysyła powiadomienia, gdy Twój bliski potrzebuje uwagi 
    (np. obniżony nastrój, pominięte leki, alert bezpieczeństwa).</string>
    <!-- Zezwól na arbitrary loads dla deweloperskiego trybu -->
    <!-- USUŃ PRZED PUBLIKACJĄ DO APP STORE! -->
    <!--
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
    -->
    ```
5.2. UTWÓRZ PLIK: ios/App/App/AppDelegate.swift — jeśli nie istnieje, Capacitor wygeneruje.
5.3. Skonfiguruj wersję minimalną iOS:
    W Xcode (po otwarciu `npx cap open ios`): 
    - Project → Info → iOS Deployment Target: 15.0
    - App Store wymaga minimum iOS 15 od 2025 roku
═══════════════════════════════════════════════════════════════
KROK 6: SKRYPTY BUDOWANIA I PUBLIKACJI
═══════════════════════════════════════════════════════════════
6.1. Dodaj do package.json skrypty:
    ```json
    "scripts": {
      "dev": "vite",
      "build": "tsc && vite build",
      "preview": "vite preview",
      "assets:generate": "npx @capacitor/assets generate --iconBackgroundColor '#1a2744' --splashBackgroundColor '#1a2744'",
      "cap:sync": "npm run build && npx cap sync",
      "cap:open:ios": "npm run cap:sync && npx cap open ios",
      "cap:open:android": "npm run cap:sync && npx cap open android",
      "cap:run:ios": "npm run cap:sync && npx cap run ios",
      "cap:run:android": "npm run cap:sync && npx cap run android",
      "cap:build:ios": "npm run cap:sync && cd ios && xcodebuild -workspace App.xcworkspace -scheme App -configuration Release -archivePath build/Adam.xcarchive archive",
      "cap:build:android": "npm run cap:sync && cd android && ./gradlew assembleRelease",
      "cap:doctor": "npx cap doctor",
      "cap:doctor:ios": "npx cap doctor ios",
      "cap:doctor:android": "npx cap doctor android"
    }
    ```
6.2. Tworzenie podpisanego bundle Android (.aab) dla Google Play:
    ```bash
    # 1. Wygeneruj keystore (tylko raz!)
    keytool -genkey -v -keystore adam-release.keystore \
      -alias adam -keyalg RSA -keysize 2048 -validity 10000 \
      -storepass ADAM_STORE_PASS -keypass ADAM_KEY_PASS
    # 2. Umieść adam-release.keystore w android/app/
    # 3. Utwórz android/app/release-signing.properties:
    #    storeFile=adam-release.keystore
    #    storePassword=ADAM_STORE_PASS
    #    keyAlias=adam
    #    keyPassword=ADAM_KEY_PASS
    # 4. Zbuduj release bundle
    cd android && ./gradlew bundleRelease
    # Plik: android/app/build/outputs/bundle/release/app-release.aab
    # Wgraj na Google Play Console
    ```
6.3. Tworzenie archiwum iOS (.ipa) dla App Store:
    ```bash
    # 1. Otwórz w Xcode
    npx cap open ios
    # 2. W Xcode:
    #    - Wybierz "Any iOS Device (arm64)" jako target
    #    - Product → Archive
    #    - Window → Organizer → Distribute App → App Store Connect
    # Alternatywnie z linii komend (fastlane — zobacz Krok 7):
    npm run cap:build:ios
    ```
═══════════════════════════════════════════════════════════════
KROK 7: FASTLANE — AUTOMATYCZNA PUBLIKACJA DO APP STORE
═══════════════════════════════════════════════════════════════
7.1. UTWÓRZ PLIK: ios/fastlane/Fastfile
    ```ruby
    default_platform(:ios)
    platform :ios do
      desc "Build and upload to TestFlight"
      lane :beta do
        increment_build_number(xcodeproj: "App.xcodeproj")
        build_app(
          scheme: "App",
          workspace: "App.xcworkspace",
          export_method: "app-store",
          output_directory: "./build",
        )
        upload_to_testflight(
          skip_waiting_for_build_processing: true,
          notify_external_testers: false,
        )
      end
      desc "Upload to App Store (submit for review)"
      lane :release do
        increment_build_number(xcodeproj: "App.xcodeproj")
        build_app(
          scheme: "App",
          workspace: "App.xcworkspace",
          export_method: "app-store",
          output_directory: "./build",
        )
        upload_to_app_store(
          force: true,
          skip_metadata: false,
          skip_screenshots: false,
          automatic_release: false, # ręczne wypuszczenie po review
        )
      end
    end
    ```
7.2. UTWÓRZ PLIK: ios/fastlane/Appfile
    ```ruby
    app_identifier("pl.silvertech.adam.caregiver")
    apple_id("your-apple-id@silvertech.poznan.pl")
    itc_team_id("XXXXXXXXXX")  # App Store Connect Team ID
    team_id("XXXXXXXXXX")       # Apple Developer Team ID
    ```
7.3. UTWÓRZ PLIK: android/fastlane/Fastfile
    ```ruby
    default_platform(:android)
    platform :android do
      desc "Build and upload to Google Play (internal testing)"
      lane :beta do
        gradle(task: "bundleRelease")
        upload_to_play_store(
          track: 'internal',
          release_status: 'draft',
          aab: 'app/build/outputs/bundle/release/app-release.aab',
        )
      end
      desc "Release to production"
      lane :release do
        gradle(task: "bundleRelease")
        upload_to_play_store(
          track: 'production',
          release_status: 'completed',
          aab: 'app/build/outputs/bundle/release/app-release.aab',
        )
      end
    end
    ```
7.4. Dodaj do package.json:
    ```json
    "scripts": {
      "deploy:ios:beta": "cd ios && fastlane beta",
      "deploy:ios:release": "cd ios && fastlane release",
      "deploy:android:beta": "cd android && fastlane beta",
      "deploy:android:release": "cd android && fastlane release"
    }
    ```
═══════════════════════════════════════════════════════════════
KROK 8: CI/CD — GITHUB ACTIONS (opcjonalnie)
═══════════════════════════════════════════════════════════════
8.1. UTWÓRZ PLIK: .github/workflows/mobile-build.yml
    ```yaml
    name: Build Mobile Apps
    on:
      push:
        branches: [main]
        paths:
          - 'frontend/**'
      workflow_dispatch:
    jobs:
      build-android:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-node@v4
            with:
              node-version: 20
              cache: 'npm'
              cache-dependency-path: frontend/package-lock.json
          - name: Install dependencies
            working-directory: frontend
            run: npm ci
          - name: Build web
            working-directory: frontend
            run: npm run build
          - name: Sync Capacitor
            working-directory: frontend
            run: npx cap sync android
          - name: Setup Java
            uses: actions/setup-java@v4
            with:
              distribution: 'temurin'
              java-version: '17'
          - name: Build Android Release
            working-directory: frontend/android
            run: ./gradlew bundleRelease
          - name: Upload AAB artifact
            uses: actions/upload-artifact@v4
            with:
              name: android-release-aab
              path: frontend/android/app/build/outputs/bundle/release/app-release.aab
      build-ios:
        runs-on: macos-14
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-node@v4
            with:
              node-version: 20
              cache: 'npm'
              cache-dependency-path: frontend/package-lock.json
          - name: Install dependencies
            working-directory: frontend
            run: npm ci
          - name: Build web
            working-directory: frontend
            run: npm run build
          - name: Sync Capacitor
            working-directory: frontend
            run: npx cap sync ios
          - name: Build iOS Archive
            working-directory: frontend/ios
            run: |
              xcodebuild -workspace App.xcworkspace \
                -scheme App \
                -configuration Release \
                -archivePath build/Adam.xcarchive \
                archive \
                CODE_SIGN_STYLE=Manual
          - name: Upload IPA artifact
            uses: actions/upload-artifact@v4
            with:
              name: ios-archive
              path: frontend/ios/build/Adam.xcarchive
    ```
═══════════════════════════════════════════════════════════════
KROK 9: TESTOWANIE — SPRAWDŹ CZY DZIAŁA
═══════════════════════════════════════════════════════════════
9.1. Sprawdź konfigurację:
    npx cap doctor
9.2. Test na Androidzie (emulator lub fizyczne urządzenie):
    npm run cap:run:android
9.3. Test na iOS (symulator):
    npm run cap:run:ios
9.4. Test w przeglądarce (tryb webowy — wszystko powinno działać z mockami):
    npm run dev
    # Otwórz http://localhost:5173
    # Sprawdź konsolę: powinno być "[Adam] Running on: web, native: false"
    # Wszystkie funkcje mobileBridge powinny działać w trybie webowym
═══════════════════════════════════════════════════════════════
KROK 10: CHECKLISTA PRZED PUBLIKACJĄ
═══════════════════════════════════════════════════════════════
10.1. UTWÓRZ PLIK: docs/APP_STORE_CHECKLIST.md
     ```markdown
     # App Store & Google Play — Checklista Publikacyjna
     ## Przed publikacją
     - [ ] Ikona 1024×1024 px (bez przezroczystości)
     - [ ] Splash screen (2732×2732 px)
     - [ ] Zrzuty ekranu:
       - [ ] iPhone 6.7" (1290×2796 px) — min. 3 szt.
       - [ ] iPhone 6.1" (1179×2556 px) — min. 3 szt.
       - [ ] Android phone — min. 4 szt.
     - [ ] Opis aplikacji (PL + EN):
       - [ ] Krótki opis (80 znaków)
       - [ ] Pełny opis (min. 500 znaków)
       - [ ] Słowa kluczowe (iOS)
     - [ ] Polityka prywatności URL (https://silvertech.poznan.pl/polityka-prywatnosci)
     - [ ] Regulamin URL (https://silvertech.poznan.pl/regulamin)
     - [ ] Kontakt support (email + telefon)
     ## Apple App Store
     - [ ] Apple Developer Account ($99/rok)
     - [ ] App Store Connect: utworzona app (pl.silvertech.adam.caregiver)
     - [ ] Bundle ID zgodny z App Store Connect
     - [ ] Certyfikat dystrybucyjny (Apple Distribution)
     - [ ] Provisioning profile (App Store)
     - [ ] NSUserNotificationUsageDescription w Info.plist
     - [ ] TestFlight: co najmniej 1 build przesłany i przetestowany
     - [ ] App Privacy labels wypełnione
     - [ ] Brak NSAppTransportSecurity z NSAllowsArbitraryLoads=true
     ## Google Play
     - [ ] Google Play Developer Account ($25 jednorazowo)
     - [ ] Google Play Console: utworzona app
     - [ ] Release keystore (bezpiecznie przechowany!)
     - [ ] .aab (Android App Bundle) — NIE .apk
     - [ ] Podpisanie przez Google Play (Play App Signing)
     - [ ] Data safety section wypełniona
     - [ ] Target API level ≥ 33
     - [ ] Testy zamknięte: min. 20 testerów na 14 dni (wymóg Google od 2024)
     ## Dla obu platform
     - [ ] Wersja 1.0.0 — versionCode 1 / CFBundleVersion 1
     - [ ] App nie crashuje na starcie
     - [ ] Logowanie działa (JWT token poprawnie przechowywany)
     - [ ] Push notyfikacje działają (przetestowane na fizycznym urządzeniu!)
     - [ ] Deep linking działa (link z email/SMS otwiera apkę)
     - [ ] Responsywność: UI nie rozjeżdża się na różnych ekranach
     ```
═══════════════════════════════════════════════════════════════
KROK 11: OBSŁUGA DEEP LINKÓW
═══════════════════════════════════════════════════════════════
Deep linki pozwalają, żeby SMS "🚨 ALARM: Sprawdź stan Jana Kowalskiego" 
po kliknięciu otwierał apkę od razu na widoku seniora.
11.1. Dodaj do capacitor.config.ts:
     ```typescript
     const config: CapacitorConfig = {
       // ... istniejąca konfiguracja
       plugins: {
         // ... istniejące pluginy
       },
     };
     // Deep linking: adam://senior/<id>
     // iOS: Universal Links też trzeba skonfigurować (apple-app-site-association)
     // Android: Intent filter w AndroidManifest.xml
     export default config;
     ```
11.2. Android — dodaj do android/app/src/main/AndroidManifest.xml, wewnątrz <activity>:
     ```xml
     <intent-filter>
         <action android:name="android.intent.action.VIEW" />
         <category android:name="android.intent.category.DEFAULT" />
         <category android:name="android.intent.category.BROWSABLE" />
         <data android:scheme="adam" android:host="senior" />
     </intent-filter>
     ```
11.3. iOS — dodaj do ios/App/App/Info.plist:
     ```xml
     <key>CFBundleURLTypes</key>
     <array>
         <dict>
             <key>CFBundleURLSchemes</key>
             <array>
                 <string>adam</string>
             </array>
         </dict>
     </array>
     ```
11.4. UTWÓRZ PLIK: src/core/hooks/useDeepLinks.ts
     ```typescript
     import { useEffect } from 'react';
     import { App } from '@capacitor/app';
     import { useNavigate } from 'react-router-dom';
     import { isNative } from '../services/mobileBridge';
     export function useDeepLinks() {
       const navigate = useNavigate();
       useEffect(() => {
         if (!isNative) return;
         App.addListener('appUrlOpen', (data) => {
           const url = new URL(data.url);
           // adam://senior/<senior_id>
           if (url.hostname === 'senior') {
             const seniorId = url.pathname.replace(/^\//, '');
             if (seniorId) {
               navigate(`/panel/senior/${seniorId}`);
             }
           }
           // adam://alert/<senior_id>
           if (url.hostname === 'alert') {
             const seniorId = url.pathname.replace(/^\//, '');
             if (seniorId) {
               navigate(`/panel/senior/${seniorId}/alerty`);
             }
           }
         });
         return () => {
           App.removeAllListeners();
         };
       }, [navigate]);
     }
     ```
═══════════════════════════════════════════════════════════════
KROK 12: WERYFIKACJA KOŃCOWA
═══════════════════════════════════════════════════════════════
Po wykonaniu wszystkich kroków uruchom:
```bash
# 1. Sprawdź, czy wszystko skonfigurowane
npx cap doctor
# 2. Przetestuj w przeglądarce (tryb webowy)
npm run dev
# 3. Przetestuj na Androidzie
npm run cap:run:android
# 4. Przetestuj na iOS
npm run cap:run:ios
# 5. Zbuduj produkcyjnie
npm run cap:build:android   # → .aab do Google Play
npm run cap:build:ios       # → archiwum do App Store
Oczekiwany rezultat:
[x] Aplikacja uruchamia się na iOS i Android
[x] Splash screen pokazuje logo Adam na granatowym tle
[x] Logowanie działa (JWT przechowywane bezpiecznie)
[x] Dashboard opiekuna ładuje się identycznie jak w web
[x] Push notyfikacje zarejestrowane (sprawdź token w konsoli)
[x] Deep link adam://senior/ otwiera właściwy ekran
[x] Status bar granatowy (#1a2744)
[x] Wszystkie 3 tryby działają: web, iOS, Android
═══════════════════════════════════════════════════════════════ WAŻNE: NIE MODYFIKUJ istotnie istniejących komponentów React. Wszystkie zmiany mają być ADDYTYWNE — nowe pliki i lekkie wpięcia w istniejący kod (głównie App.tsx i main.tsx). Aplikacja webowa ma DZIAŁAĆ DOKŁADNIE TAK SAMO po dodaniu Capacitor. ═══════════════════════════════════════════════════════════════
---
## 📋 CO ZROBI GENSPARK — PODSUMOWANIE
| # | Co powstanie | Pliki |
|---|-------------|-------|
| 1 | `capacitor.config.ts` | Konfiguracja Capacitor |
| 2 | `mobileBridge.ts` | Warstwa abstrakcji web/native (~200 linii) |
| 3 | `useMobileInit.ts` + `useDeepLinks.ts` | Hooki inicjalizacyjne |
| 4 | Modyfikacja `App.tsx` + `main.tsx` | Wpięcie hooków |
| 5 | `package.json` | Nowe skrypty (`cap:*`, `deploy:*`) |
| 6 | `styles.xml` (Android) | Theme granatowy + splash |
| 7 | `AndroidManifest.xml` | Uprawnienia + deep linki |
| 8 | `Info.plist` (iOS) | Powiadomienia + deep linki |
| 9 | `Fastfile` ×2 | Automatyczna publikacja (fastlane) |
| 10 | `mobile-build.yml` | GitHub Actions CI/CD |
| 11 | `APP_STORE_CHECKLIST.md` | Checklista publikacyjna |
| 12 | `resources/` | Ikony i splash (autogenerowane) |
---
## ⚡ PO OTRZYMANIU KODU OD GENSPARK
```bash
# 1. Zainstaluj zależności
cd frontend && npm install
# 2. Wygeneruj assety (ikony, splash)
npm run assets:generate
# 3. Zbuduj web + zsynchronizuj
npm run cap:sync
# 4. Sprawdź konfigurację
npm run cap:doctor
# 5. Testuj na urządzeniu
npm run cap:run:android   # podłącz telefon przez USB
npm run cap:run:ios       # wymaga Xcode + Mac
Chcesz, żebym teraz rozpisał któryś z tych kroków jeszcze bardziej szczegółowo — np. pełną konfigurację Firebase do push notyfikacji, albo proces rejestracji w Apple Developer i Google Play Console krok po kroku?