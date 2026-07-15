/// <reference types="vite/client" />
/// <reference types="vite-plugin-pwa/react" />
/// <reference types="vite-plugin-pwa/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  /** WP-1: jawny tryb API — 'mock' | 'real'. Brak = auto wg VITE_API_URL. */
  readonly VITE_API_MODE: 'mock' | 'real'
  readonly VITE_API_KEY: string
  readonly VITE_WS_URL: string
  readonly VITE_ADAM_VERSION: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
