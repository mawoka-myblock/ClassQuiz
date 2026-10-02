// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// A player who placed gets a medal on their own screen, which is the only thing they
// carry out of the room. Below third, they get their place instead -- the two never
// appear together, because the medal already says the place.

import { test, expect } from '@playwright/test';
import {
	advancePastResults,
	advanceToFinalResults,
	gotoPlayHydrated,
	hostFromViewPage,
	mc,
	rememberAnonQuiz,
	saveQuiz
} from './helpers';
test('a player who placed gets a medal, and nobody gets both', async ({ browser, request }) => {
	test.setTimeout(6 * 60_000);
	const saved = await saveQuiz(request, { title: 'Frog Anatomy', description: 'two',
		questions: [
			mc('How many legs does a frog have?', [['Four', true], ['Two', false], ['Six', false], ['None', false]], '5'),
			mc('Where do tadpoles live?', [['Water', true], ['Trees', false]], '5')
		] });
	const hostCtx = await browser.newContext({ viewport: { width: 1600, height: 900 } });
	const host = await hostCtx.newPage();
	await rememberAnonQuiz(host, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(host, saved.body.id);
	const made: any[] = [];
	for (const [n, a1, a2] of [['Ada','Four','Water'],['Bo','Four','Trees'],['Cy','Two','Water'],['Dee','Two','Trees']] as [string,string,string][]) {
		const c = await browser.newContext({ viewport: { width: 390, height: 844 } });
		const p = await c.newPage();
		await gotoPlayHydrated(p);
		await p.getByRole('textbox', { name: 'Game PIN' }).fill(pin);
		await p.getByRole('textbox', { name: 'Username' }).fill(n);
		await p.getByRole('button', { name: 'Submit' }).click();
		made.push({ c, p, a1, a2 });
	}
	await host.waitForTimeout(1200);
	await host.getByRole('button', { name: /Start game/ }).first().click();
	await host.waitForTimeout(800);
	await host.getByRole('button', { name: /Next Question/ }).first().click();
	await host.waitForTimeout(1200);
	for (const m of made) { await m.p.getByRole('button', { name: new RegExp(`^${m.a1}$`) }).first().click().catch(() => undefined); await m.p.waitForTimeout(220); }
	await host.waitForTimeout(6500);
	await host.getByRole('button', { name: /Show results/ }).first().click();
	await host.waitForTimeout(1600);

	// through question 2 to the podium, for the medal
	await advancePastResults(host);
	await host.waitForTimeout(1200);
	for (const m of made) { await m.p.getByRole('button', { name: new RegExp(`^${m.a2}$`) }).first().click().catch(() => undefined); await m.p.waitForTimeout(220); }
	await host.waitForTimeout(6500);
	await host.getByRole('button', { name: /Show results/ }).first().click();
	await host.waitForTimeout(1400);
	await advanceToFinalResults(host);
	await host.waitForTimeout(6000);
	const winnerBar = made[0].p.locator('.fixed.bottom-0');
	await expect(winnerBar.getByText('1st Place')).toBeVisible();
	await expect(winnerBar.getByText(/You.re on place/)).toHaveCount(0);

	// Fourth gets no medal, so they get their place in words instead.
	const lastBar = made[3].p.locator('.fixed.bottom-0');
	await expect(lastBar.getByText(/You.re on place 4/)).toBeVisible();
	await expect(lastBar.getByText(/Place$/)).toHaveCount(0);
	await hostCtx.close();
	for (const m of made) await m.c.close();
});
