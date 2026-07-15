import { test, expect } from '@playwright/test'

/**
 * WP-2 · Scenariusz 4 — Nawigacja i ochrona tras.
 * - Nieautoryzowany dostęp do /panel przekierowuje na /login.
 * - Po zalogowaniu nawigacja bocznа między sekcjami panelu działa.
 */
test.describe('Nawigacja i ochrona tras', () => {
  test('nieautoryzowany /panel przekierowuje na /login', async ({ page }) => {
    await page.goto('/panel/orders')
    await expect(page).toHaveURL(/\/login/)
  })

  test('nawigacja między sekcjami panelu po zalogowaniu', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('E-mail').fill('anna@silvertech.pl')
    await page.getByLabel('Hasło').fill('demo1234')
    await page.getByRole('button', { name: /^Zaloguj/i }).click()
    await expect(page).toHaveURL(/\/panel/)

    // Nawigacja do Zamówień przez menu boczne.
    await page.getByRole('link', { name: /Zamówienia/i }).click()
    await expect(page).toHaveURL(/\/panel\/orders/)

    // Powrót do Dashboardu.
    await page.getByRole('link', { name: /Dashboard/i }).click()
    await expect(page).toHaveURL(/\/panel$/)
  })
})
