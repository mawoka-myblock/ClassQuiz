// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { expect, test, type APIRequestContext, type Browser, type Page } from '@playwright/test';
import {
	advancePastResults,
	advanceToFinalResults,
	expectNoHorizontalOverflow,
	hostFromViewPage,
	joinAsPlayer,
	mc,
	rememberAnonQuiz,
	saveQuiz
} from './helpers';

const NAMES = ['anabela', 'bruno', 'carla'] as const;

const QUIZ = {
	title: 'Anon game',
	description: 'e2e',
	questions: [
		mc('Capital of Portugal?', [
			['Lisbon', true],
			['Porto', false],
			['Faro', false]
		]),
		// Short timer so the "somebody never answers" path runs on its own clock.
		mc(
			'2 + 2?',
			[
				['4', true],
				['5', false]
			],
			'5'
		)
	]
};

/** Score printed under a name on a podium (host's or a player's -- same markup). */
async function podiumScore(p: Page, name: string): Promise<number> {
	const block = p.getByText(name, { exact: true }).locator('xpath=..');
	return Number((await block.textContent())!.replace(name, '').match(/\d+/)![0]);
}

/**
 * Plays the two-question game to the podium. anabela gets both right, bruno gets Q1 right
 * and never answers Q2, carla gets both wrong. `resultsDwellMs` is how long the host sits on
 * each per-question results screen before moving on.
 */
async function playGame(
	page: Page,
	request: APIRequestContext,
	browser: Browser,
	resultsDwellMs: number
) {
	const saved = await saveQuiz(request, QUIZ);
	expect(saved.status).toBe(200);
	expect(saved.secret, 'anonymous save returns a secret').toBeTruthy();
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);

	const pin = await hostFromViewPage(page, saved.body.id);
	const players = [];
	for (const name of NAMES) players.push(await joinAsPlayer(browser, pin, name));
	const [ana, bruno, carla] = players.map((p) => p.page);
	for (const p of [ana, bruno, carla]) await expect(p.getByText(/You're in/)).toBeVisible();
	for (const name of NAMES) await expect(page.getByText(name, { exact: true })).toBeVisible();

	await page.getByRole('button', { name: 'Start game' }).click();

	await page.getByRole('button', { name: /Next Question/ }).click();
	await ana.getByRole('button', { name: 'Lisbon' }).click();
	await bruno.getByRole('button', { name: 'Lisbon' }).click();
	await carla.getByRole('button', { name: 'Porto' }).click();
	await expect(page.getByText('3 answers submitted')).toBeVisible();
	await page.getByRole('button', { name: 'Show results' }).click();
	await page.waitForTimeout(resultsDwellMs);

	await advancePastResults(page);
	await ana.getByRole('button', { name: '4', exact: true }).click();
	await carla.getByRole('button', { name: '5', exact: true }).click();
	// Nobody ends the question: the 5 s timer has to.
	await expect(page.getByRole('button', { name: 'Show results' })).toBeVisible({
		timeout: 15_000
	});
	await expect(bruno.getByRole('button', { name: '4', exact: true })).toHaveCount(0);
	await page.getByRole('button', { name: 'Show results' }).click();
	await page.waitForTimeout(resultsDwellMs);

	await advanceToFinalResults(page);
	// Scoped to the podium block, not the page. The host screen legitimately says
	// "1st Place" twice -- once on the gold block and once in the standings row for the
	// winner -- so a bare getByText is a strict-mode violation rather than a real check.
	// The player's own medal bar, not the page. Their screen shows the podium too, and
	// the block's place label is now in the DOM at phone width as well -- it used to be
	// `hidden sm:block`, which removed it, and is `max-sm:sr-only` so a screen reader
	// still gets it. That made a bare getByText ambiguous on this side as well.
	await expect(ana.locator('.fixed.bottom-0').getByText('1st Place')).toBeVisible();
	await expect(page.locator('.podium-block.is-gold').getByText('1st Place')).toBeVisible();

	// Players' podiums are rendered from the server's totals, so they are the reference.
	const truth: Record<string, number> = {};
	for (const name of NAMES) truth[name] = await podiumScore(ana, name);
	return { players, ana, bruno, carla, truth };
}

test('anonymous host runs a full game with three players', async ({ page, request, browser }) => {
	const { players, ana, truth } = await playGame(page, request, browser, 2500);

	expect(truth.anabela).toBeGreaterThan(truth.bruno);
	expect(truth.bruno).toBeGreaterThan(0);
	expect(truth.carla).toBe(0);
	await expect(ana.getByText(`Your score: ${truth.anabela}`)).toBeVisible();
	// The winner gets a medal instead of their place in words -- never both. This still
	// asserted the words, which player-medal.e2e.ts explicitly asserts the winner does
	// NOT get, so the two specs contradicted each other.
	await expect(ana.locator('.fixed.bottom-0').getByText('1st Place')).toBeVisible();
	await expect(ana.locator('.fixed.bottom-0').getByText(/You.re on place/)).toHaveCount(0);

	for (const name of NAMES) {
		expect(await podiumScore(page, name), `host podium score for ${name}`).toBe(truth[name]);
	}
	// An anonymous host has nowhere to save results to; export still works.
	await expect(page.getByRole('button', { name: 'Save results' })).toHaveCount(0);
	// One press now: the button says what it does rather than minting a token and then
	// renaming itself. 'Request result download' is the old label.
	await expect(page.getByRole('button', { name: 'Download results' })).toBeVisible();
	for (const p of [page, ana]) await expectNoHorizontalOverflow(p);
	for (const { context } of players) await context.close();
});

test.describe('regressions', () => {
	test('host podium keeps points for a question the host moved past quickly', async ({
		page,
		request,
		browser
	}) => {
		const { players, truth } = await playGame(page, request, browser, 200);
		for (const name of NAMES) expect(await podiumScore(page, name), name).toBe(truth[name]);
		for (const { context } of players) await context.close();
	});

	test('a player on zero points still sees their score and place', async ({
		page,
		request,
		browser
	}) => {
		const { players, carla } = await playGame(page, request, browser, 2500);
		await expect(carla.getByText('Your score: 0')).toBeVisible({ timeout: 3000 });
		for (const { context } of players) await context.close();
	});

	test('podium shows "points", not a raw translation key', async ({ page, request, browser }) => {
		const { players, ana } = await playGame(page, request, browser, 2500);
		for (const p of [page, ana])
			await expect(p.locator('body')).not.toContainText('words.point_plural');
		for (const { context } of players) await context.close();
	});
});
