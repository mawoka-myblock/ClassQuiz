// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Ctrl/Cmd+K from anywhere. Searching it threw: MiniSearch returns the id an action was
// indexed under, and four actions had been removed, so `actions[id]` was undefined for
// every hit -- an empty list and a TypeError on each render.

import { expect, test } from '@playwright/test';

test('the command palette opens, searches and runs an action', async ({ page }) => {
	const errors: string[] = [];
	page.on('pageerror', (e) => errors.push(String(e)));

	await page.goto('/my-quizzes');
	await page.waitForTimeout(800);
	await page.keyboard.press('Control+k');

	const input = page.getByRole('textbox').last();
	await expect(input).toBeFocused();

	await input.fill('create');
	await page.waitForTimeout(400);
	const hits = page.getByRole('button', { name: /Create Quiz/ });
	await expect(hits.first()).toBeVisible();
	expect(errors, 'searching the palette threw').toEqual([]);

	await hits.first().click();
	await expect(page).toHaveURL(/\/create/);
	expect(errors).toEqual([]);
});

test('the palette does not scroll the page sideways', async ({ page }) => {
	await page.goto('/my-quizzes');
	await page.waitForTimeout(800);
	await page.keyboard.press('Control+k');
	await page.waitForTimeout(400);
	// w-screen is 100vw, which includes the scrollbar -- the trap CLAUDE.md lists first.
	const overflow = await page.evaluate(
		() => document.documentElement.scrollWidth - document.documentElement.clientWidth
	);
	expect(overflow).toBeLessThanOrEqual(0);
});
