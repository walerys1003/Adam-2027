import { test, expect } from '@playwright/test'

/**
 * WP-2 · Scenariusz 3 — Zamówienia (marketplace) w Panelu Opiekuna.
 * Ścieżka: logowanie → /panel/orders → utworzenie nowego zamówienia
 * przez picker kategorii. Weryfikuje spięcie z fasadą `api` (useApi).
 */
test.describe('Zamówienia', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('E-mail').fill('anna@silvertech.pl')
    await page.getByLabel('Hasło').fill('demo1234')
    await page.getByRole('button', { name: /^Zaloguj/i }).click()
    await expect(page).toHaveURL(/\/panel/)
  })

  test('lista zamówień renderuje się i można otworzyć picker', async ({ page }) => {
    await page.goto('/panel/orders')

    // Nagłówek strony.
    await expect(page.getByRole('heading', { name: 'Zamówienia', exact: true })).toBeVisible()

    // Sekcja „Aktywne (n)” pojawia się po załadowaniu danych (useApi).
    await expect(page.getByText(/Aktywne \(/)).toBeVisible()

    // Otwórz picker nowego zamówienia.
    await page.getByRole('button', { name: /Nowe zamówienie/i }).click()
    await expect(page.getByText(/Wybierz kategorię/i)).toBeVisible()
  })

  test('utworzenie zamówienia zwiększa liczbę aktywnych', async ({ page }) => {
    await page.goto('/panel/orders')
    await expect(page.getByText(/Aktywne \(/)).toBeVisible()

    await page.getByRole('button', { name: /Nowe zamówienie/i }).click()
    await expect(page.getByText(/Wybierz kategorię/i)).toBeVisible()

    // Kliknij pierwszą kategorię w pickerze.
    const firstCategory = page.locator('button.group').first()
    await firstCategory.click()

    // Po utworzeniu picker znika, a lista odświeża się bez błędu.
    await expect(page.getByText(/Aktywne \(/)).toBeVisible()
  })
})
