// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// What happens to a game when a player's socket goes away without saying so.
//
// There was no `disconnect` handler at all, so a closed tab stayed in the set that
// "everyone answered" is counted against: once one person left, the question could
// never end early again and the host sat through every full timer for the rest of the
// game. That is the single worst thing that can happen to a live game in a room, and
// nothing caught it, because every existing spec either answers with everyone present
// or leaves through the Leave button.

import { expect, test } from '@playwright/test';
import { mc, saveQuiz, rememberAnonQuiz, hostFromViewPage, gotoPlayHydrated } from './helpers';

const QUIZ = {
	title: 'Disconnect',
	description: 'one question, a long timer',
	// 60s, so the question can only end early by the count -- if the test passes on a
	// timer expiry instead, it is not testing anything.
	questions: [
		mc(
			'Pick A?',
			[
				['A', true],
				['B', false]
			],
			'60'
		)
	]
};

async function joinPhone(browser, pin: string, name: string) {
	const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
	const page = await ctx.newPage();
	await gotoPlayHydrated(page);
	await page.getByRole('textbox', { name: 'Game PIN' }).fill(pin);
	await page.getByRole('textbox', { name: 'Username' }).fill(name);
	await page.getByRole('button', { name: 'Submit' }).click();
	return { ctx, page };
}

test('a closed tab stops blocking the question', async ({ browser, request }) => {
	test.setTimeout(3 * 60_000);
	const saved = await saveQuiz(request, QUIZ);
	const hostCtx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
	const host = await hostCtx.newPage();
	await rememberAnonQuiz(host, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(host, saved.body.id);

	const a = await joinPhone(browser, pin, 'Stays');
	const b = await joinPhone(browser, pin, 'Leaves');
	await expect(host.getByText('Stays')).toBeVisible();
	await expect(host.getByText('Leaves')).toBeVisible();

	await host.getByRole('button', { name: /Start game/ }).first().click();
	await host.waitForTimeout(800);
	await host.getByRole('button', { name: /Next Question/ }).first().click();
	await host.waitForTimeout(1200);

	// One of the two answers. The question stays open: the count is still 2.
	const tileA = a.page.getByRole('button', { name: /A/ }).first();
	await tileA.click();
	// The tiles go disabled on answering; the "Answer locked in" screen replaces them
	// only once the timer reaches zero, which on a 60s question is the whole point here.
	await expect(tileA).toBeDisabled();
	await host.waitForTimeout(1000);
	// Still running -- the host has not been handed the results yet.
	await expect(host.getByRole('button', { name: /Show results/ })).toBeHidden();

	// The other one's tab closes. No Leave, no goodbye: exactly a shut laptop.
	await b.ctx.close();

	// With only answered players left, the question ends on its own, long before 60s.
	await expect(host.getByRole('button', { name: /Show results/ })).toBeVisible({
		timeout: 20_000
	});

	await hostCtx.close();
	await a.ctx.close();
});

test('a player who reloads is still on the host list', async ({ browser, request }) => {
	test.setTimeout(3 * 60_000);
	const saved = await saveQuiz(request, QUIZ);
	const hostCtx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
	const host = await hostCtx.newPage();
	await rememberAnonQuiz(host, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(host, saved.body.id);

	const p = await joinPhone(browser, pin, 'Reloader');
	await expect(host.getByText('Reloader')).toBeVisible();

	// The host filters its list on player_left and only ever added on player_joined, so
	// a reload used to take the player off the lobby for the rest of the game -- while
	// the server still had them, which is the confusing half.
	await p.page.reload();
	await p.page.waitForTimeout(2500);
	await expect(host.getByText('Reloader')).toBeVisible({ timeout: 15_000 });

	await hostCtx.close();
	await p.ctx.close();
});
