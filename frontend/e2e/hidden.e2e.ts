// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// What the MVP hides (MVP.md D4, D6, D15 and §4.2), pinned down so un-hiding something is
// a deliberate change to this file rather than an accident. Hidden means: no entry point
// in the UI, and the route 404s through DISABLED_ROUTES. The code stays in the tree.

import { expect, test } from '@playwright/test';
import { signedInContext } from './accounts';

const HIDDEN = [
	'/docs',
	'/docs/self-host',
	'/docs/import-from-kahoot',
	'/import',
	'/results',
	'/edit/files',
	'/dashboard/files',
	'/edit/videos',
	'/remote',
	'/user/00000000-0000-0000-0000-000000000000',
	'/account/settings/avatar'
];
const KEPT = ['/docs/tos', '/docs/privacy-policy', '/docs/attribution'];

test('hidden routes 404 and the legal pages stay', async ({ page }) => {
	for (const route of HIDDEN) {
		const res = await page.goto(route);
		expect(res?.status(), route).toBe(404);
	}
	for (const route of KEPT) {
		const res = await page.goto(route);
		expect(res?.status(), route).toBe(200);
	}
});

test('no navbar, footer or toolbar link points at a hidden page', async ({ browser, request }) => {
	const user = await signedInContext(browser, request);
	for (const signedIn of [false, true]) {
		const page = signedIn ? user.page : await browser.newPage();
		await page.goto('/my-quizzes');
		const hrefs = await page.$$eval('a[href]', (as) => as.map((a) => a.getAttribute('href')!));
		for (const href of hrefs) {
			expect(href, `signed ${signedIn ? 'in' : 'out'}`).not.toMatch(
				/github\.com|^\/docs\/?$|^\/(import|results|remote|user|edit\/files)\b/
			);
		}
		const footer = page.getByRole('contentinfo');
		await expect(footer.getByRole('link', { name: 'Terms of Service' })).toBeVisible();
	}
	await user.page.goto('/account/settings');
	await expect(user.page.getByRole('link', { name: /avatar|public profile/i })).toHaveCount(0);
	await user.context.close();
});
