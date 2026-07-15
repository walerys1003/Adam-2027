import { test, expect } from '@playwright/test'

/**
 * WP-2 · Scenariusz 1 — Landing page.
 * Weryfikuje, że strona główna renderuje hero + wołanie do akcji i że
 * kliknięcie CTA przenosi do logowania.
 */
test.describe('Landing', () => {
  test('renderuje hero i prowadzi do logowania', async ({ page }) => {
    await page.goto('/')

    // Nagłówek hero (H1) obecny i widoczny.
    const heading = page.getByRole('heading', { level: 1 })
    await expect(heading).toBeVisible()
    await expect(heading).toContainText('dzwoni')

    // CTA „Poznaj Adama” → /login
    await page.getByRole('button', { name: /Poznaj Adama/i }).first().click()
    await expect(page).toHaveURL(/\/login/)
    await expect(page.getByRole('heading', { name: /Zaloguj się/i })).toBeVisible()
  })
})
