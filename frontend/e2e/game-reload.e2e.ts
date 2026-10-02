// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Phones lock, tabs get reloaded, the projector laptop sleeps. A live game has to
// survive a reload on either side.

import { expect, test, type Page } from '@playwright/test';
import { hostFromViewPage, joinAsPlayer, mc, rememberAnonQuiz, saveQuiz } from './helpers';

const QUIZ = {
	title: 'Reload game',
	description: 'e2e',
	questions: [
		mc('First?', [
			['Yes', true],
			['No', false]
		]),
		mc('Second?', [
			['Up', true],
			['Down', false]
		])
	]
};

async function reloadHydrated(page: Page) {
	const connected = page.waitForEvent('console', {
		predicate: (m) => m.text() === 'Connected!',
		timeout: 15_000
	});
	await page.reload();
	await connected;
}

async function setUp(
	page: Page,
	request: Parameters<typeof saveQuiz>[0],
	browser: import('@playwright/test').Browser
) {
	const saved = await saveQuiz(request, QUIZ);
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(page, saved.body.id);
	const player = await joinAsPlayer(browser, pin, 'reloader');
	await expect(player.page.getByText(/You're in/)).toBeVisible();
	return { pin, player };
}

test('a player who reloads in the lobby is still in the game and can answer', async ({
	page,
	request,
	browser
}) => {
	// Regression guard: rejoin_game used to emit time_sync before saving the new session,
	// so no ping was stored and every later answer raised KeyError("ping") and was dropped.
	const { player } = await setUp(page, request, browser);
	await reloadHydrated(player.page);
	await page.getByRole('button', { name: 'Start game' }).click();
	await page.getByRole('button', { name: /Next Question/ }).click();
	await player.page.getByRole('button', { name: 'Yes' }).click();
	await expect(page.getByText('1 answer submitted')).toBeVisible({ timeout: 5000 });
	await player.context.close();
});

test('the host can reload mid-game and carry on', async ({ page, request, browser }) => {
	const { player } = await setUp(page, request, browser);
	await page.getByRole('button', { name: 'Start game' }).click();
	await page.getByRole('button', { name: /Next Question/ }).click();
	await player.page.getByRole('button', { name: 'Yes' }).click();
	await page.reload();
	// Whatever screen it comes back on, the host must be able to move the game on.
	// Scoreboard is in the list because the standings are now a host step of their own,
	// so a reload timed just after the answers can legitimately come back on it. This
	// passes today only because the reload lands mid-question; without it the test is one
	// timing change away from a confusing failure.
	const next = page.getByRole('button', {
		name: /Next Question|Show results|Scoreboard|Start game/
	});
	await expect(next.first()).toBeVisible({ timeout: 15_000 });
	test.info().annotations.push({
		type: 'host came back on',
		description: (await next.first().textContent()) ?? ''
	});
	await player.context.close();
});

test.describe('repeated and mid-question reloads', () => {
	test('a player can reload twice and still be in the game', async ({
		page,
		request,
		browser
	}) => {
		// The joined_game cookie used to be written on join only, so after the first
		// rejoin it held a stale socket id and the second reload was refused.
		const { player } = await setUp(page, request, browser);
		await reloadHydrated(player.page);
		await reloadHydrated(player.page);
		await page.getByRole('button', { name: 'Start game' }).click();
		await page.getByRole('button', { name: /Next Question/ }).click();
		await expect(player.page.getByRole('button', { name: 'Yes' })).toBeVisible({
			timeout: 5000
		});
		await player.context.close();
	});

	test('a player who reloads during a question gets the question back', async ({
		page,
		request,
		browser
	}) => {
		const { player } = await setUp(page, request, browser);
		await page.getByRole('button', { name: 'Start game' }).click();
		await page.getByRole('button', { name: /Next Question/ }).click();
		await expect(player.page.getByRole('button', { name: 'Yes' })).toBeVisible();
		await reloadHydrated(player.page);
		await expect(player.page.getByRole('button', { name: 'Yes' })).toBeVisible({
			timeout: 5000
		});
		await player.context.close();
	});
});
