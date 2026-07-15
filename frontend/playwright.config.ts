import { defineConfig, devices } from '@playwright/test'

/**
 * WP-2 — konfiguracja E2E (Playwright).
 * Testy uruchamiane w trybie MOCK (bez backendu): serwer podglądu Vite
 * podnoszony automatycznie na porcie 4173. Scenariusze pokrywają krytyczne
 * ścieżki opiekuna: logowanie → panel → zamówienie → wylogowanie.
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : [['list'], ['html', { open: 'never' }]],
  timeout: 30_000,
  expect: { timeout: 7_000 },

  use: {
    baseURL: 'http://localhost:4173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    locale: 'pl-PL',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],

  // Build + preview w trybie mock (VITE_API_MODE nieustawione → mock).
  webServer: {
    command: 'npm run build && npm run preview -- --port 4173 --host',
    url: 'http://localhost:4173',
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
  },
})
