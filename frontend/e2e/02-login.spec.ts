import { test, expect } from '@playwright/test'

/**
 * WP-2 · Scenariusz 2 — Logowanie opiekuna.
 * Konto demo (mock) anna@silvertech.pl → Panel Opiekuna. Token trafia
 * do localStorage (adam.accessToken), a użytkownik ląduje w /panel.
 */
test.describe('Logowanie', () => {
  test('opiekun loguje się i trafia do panelu', async ({ page }) => {
    await page.goto('/login')

    await page.getByLabel('E-mail').fill('anna@silvertech.pl')
    await page.getByLabel('Hasło').fill('demo1234')
    await page.getByRole('button', { name: /^Zaloguj/i }).click()

    // Po zalogowaniu jesteśmy w panelu opiekuna.
    await expect(page).toHaveURL(/\/panel/)

    // Token zapisany w localStorage (kontrakt tokenStore).
    const token = await page.evaluate(() => localStorage.getItem('adam.accessToken'))
    expect(token).toBeTruthy()
  })

  test('administrator trafia do panelu admina', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('E-mail').fill('admin@silvertech.pl')
    await page.getByLabel('Hasło').fill('demo1234')
    await page.getByRole('button', { name: /^Zaloguj/i }).click()
    await expect(page).toHaveURL(/\/admin/)
  })
})
