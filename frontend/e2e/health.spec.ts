import { test, expect } from '@playwright/test'

test.describe('Health Page', () => {
  test('navigates to health page and displays heading', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Health')
    await expect(page).toHaveURL('/health')
    await expect(page.locator('h1')).toHaveText('System Health')
  })

  test('health page shows status or error', async ({ page }) => {
    await page.goto('/health')
    await page.waitForSelector(
      '[data-testid="status-badge"], text=Connection Error',
    )
    const hasBadge = await page.$('[data-testid="status-badge"]')
    const hasError = await page.$('text=Connection Error')
    expect(hasBadge || hasError).toBeTruthy()
  })
})
