/**
 * Playwright configuration for end-to-end tests
 */
import { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
  testDir: './src/tests/e2e',
  timeout: 30000,
  retries: 2,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
        viewport: { width: 1280, height: 720 }
      }
    },
    {
      name: 'firefox',
      use: {
        browserName: 'firefox',
        viewport: { width: 1280, height: 720 }
      }
    }
  ],
  webServer: {
    command: 'npm run start',
    port: 3000,
    timeout: 120000,
    reuseExistingServer: !process.env.CI
  },
  reporter: [
    ['html'],
    ['list']
  ]
};

export default config;
