// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Vite dev compiles each route the first time a browser asks for it, which can take
// longer than an assertion timeout. Visiting them once up front keeps that cost out of
// the tests, so a slow first compile never reads as a failure.

import { chromium, type FullConfig } from '@playwright/test';

const ROUTES = [
	'/',
	'/play',
	'/explore',
	'/create',
	'/account/login',
	'/account/register',
	'/admin',
	'/my-quizzes',
	'/edit?quiz_id=00000000-0000-0000-0000-000000000000'
];

export default async function globalSetup(config: FullConfig) {
	const { baseURL, channel } = config.projects[0].use;
	// Same executable the tests use. This read `PW_CHROME`, which nothing sets, so on a
	// machine whose only browser is an out-of-tree Chromium the setup tried to launch
	// Playwright's own bundled shell and the whole run died before the first test.
	const browser = await chromium.launch({ channel, executablePath: process.env.E2E_CHROME });
	const page = await browser.newPage({ baseURL });
	for (const route of ROUTES) {
		await page.goto(route, { timeout: 120_000 }).catch(() => undefined);
		await page.waitForLoadState('load').catch(() => undefined);
	}
	await browser.close();
}
