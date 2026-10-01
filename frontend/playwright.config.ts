// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { defineConfig } from '@playwright/test';

// Drives a browser that is already installed: Edge on Windows, Playwright's Chromium
// elsewhere, so no download is needed on the machines this was written for. e2e/run.sh
// sets E2E_BROWSER per platform; E2E_CHROME points at an executable when the browser is
// somewhere Playwright does not look (a container image that ships its own Chromium).
// The app stack is started by e2e/run.sh at the repo root, not here: it needs Postgres,
// Redis and Meilisearch up first.
//
// Specs are named *.e2e.ts because vitest's default include would otherwise pick up
// *.spec.ts and try to run them without a browser.
export default defineConfig({
	testDir: './e2e',
	testMatch: '**/*.e2e.ts',
	globalSetup: './e2e/global-setup.ts',
	outputDir: '../e2e/.data/playwright',
	fullyParallel: false,
	workers: 1,
	retries: 0,
	timeout: 60_000,
	expect: { timeout: 10_000 },
	reporter: [['list'], ['html', { outputFolder: '../e2e/.data/report', open: 'never' }]],
	use: {
		baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:3000',
		// 'chromium' is Playwright's own build and is not a channel, so it is passed as
		// undefined rather than as a name.
		channel:
			process.env.E2E_BROWSER === 'chromium'
				? undefined
				: (process.env.E2E_BROWSER ?? 'msedge'),
		launchOptions: process.env.E2E_CHROME ? { executablePath: process.env.E2E_CHROME } : {},
		headless: true,
		screenshot: 'only-on-failure',
		trace: 'retain-on-failure'
	}
});
