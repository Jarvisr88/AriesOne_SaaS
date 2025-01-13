/**
 * End-to-end tests for deposit workflow
 */
import { test, expect } from '@playwright/test';

test.describe('Deposit Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
  });

  test('creates a new deposit', async ({ page }) => {
    // Navigate to deposits page
    await page.goto('/deposits');
    await page.click('button:text("New Deposit")');

    // Fill deposit form
    await page.fill('[name="amount"]', '100.00');
    await page.selectOption('[name="paymentMethod"]', 'cash');
    await page.fill('[name="customerId"]', '1');
    await page.fill('[name="notes"]', 'Test deposit');

    // Submit form
    await page.click('button:text("Create Deposit")');

    // Verify success
    await expect(page.locator('.chakra-toast')).toContainText('Deposit created');
    await expect(page).toHaveURL('/deposits');
    await expect(page.locator('table')).toContainText('100.00');
  });

  test('validates deposit form', async ({ page }) => {
    await page.goto('/deposits/new');

    // Submit empty form
    await page.click('button:text("Create Deposit")');

    // Check validation messages
    await expect(page.locator('text=Amount is required')).toBeVisible();
    await expect(page.locator('text=Payment method is required')).toBeVisible();
    await expect(page.locator('text=Customer ID is required')).toBeVisible();
  });

  test('views deposit details', async ({ page }) => {
    await page.goto('/deposits');

    // Click on first deposit
    await page.click('table >> text=View');

    // Verify details page
    await expect(page).toHaveURL(/\/deposits\/\d+/);
    await expect(page.locator('h1')).toContainText('Deposit Details');
    await expect(page.locator('[data-testid="deposit-amount"]')).toBeVisible();
    await expect(page.locator('[data-testid="deposit-status"]')).toBeVisible();
  });

  test('filters deposits list', async ({ page }) => {
    await page.goto('/deposits');

    // Apply filters
    await page.fill('[placeholder="Search deposits"]', 'cash');
    await page.selectOption('[name="status"]', 'completed');

    // Verify filtered results
    await expect(page.locator('table')).toContainText('cash');
    await expect(page.locator('table')).toContainText('completed');
  });
});
