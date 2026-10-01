// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// A round is sequenced the way Kahoot sequences one: the answers, then who is winning,
// then the next question. The standings used to share the answers screen.

import { test, expect } from '@playwright/test';
import { mc, saveQuiz, rememberAnonQuiz, hostFromViewPage, gotoPlayHydrated } from './helpers';
test('the host advances answers \u2192 scoreboard \u2192 next question', async ({ browser, request }) => {
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
	for (const [n, a1, a2] of [['Ada','Four','Water'],['Bo','Four','Trees'],['Cy','Two','Water'],['Dee','Two','Trees'],['Eve','Four','Water'],['Fay','Six','Trees']] as [string,string,string][]) {
		const c = await browser.newContext({ viewport: { width: 390, height: 844 } });
		const p = await c.newPage();
		await gotoPlayHydrated(p);
		await p.getByRole('textbox', { name: 'Game PIN' }).fill(pin);
		await p.getByRole('textbox', { name: 'Username' }).fill(n);
		await p.getByRole('button', { name: 'Submit' }).click();
		made.push({ c, p, a1, a2 });
	}
	await host.waitForTimeout(1400);
	await host.getByRole('button', { name: /Start game/ }).first().click();
	await host.waitForTimeout(800);
	await host.getByRole('button', { name: /Next Question/ }).first().click();
	await host.waitForTimeout(1200);
	for (const m of made) { await m.p.getByRole('button', { name: new RegExp(`^${m.a1}$`) }).first().click().catch(() => undefined); await m.p.waitForTimeout(200); }
	await host.waitForTimeout(6500);
	await host.getByRole('button', { name: /Show results/ }).first().click();
	await host.waitForTimeout(1200);
	await host.getByRole('button', { name: 'Scoreboard' }).click();
	await host.waitForTimeout(1200);
	// The answers screen carries the breakdown and nothing else; the standings are the
	// screen the host advances into.
	await expect(host.getByRole('button', { name: /Next Question/ })).toBeVisible();
	await expect(host.getByText('Scoreboard', { exact: true })).toBeVisible();
	await expect(host.getByText('Ada')).toBeVisible();
	// round two, so the movement arrows have something to say
	await host.getByRole('button', { name: /Next Question/ }).click();
	await host.waitForTimeout(1200);
	for (const m of made) { await m.p.getByRole('button', { name: new RegExp(`^${m.a2}$`) }).first().click().catch(() => undefined); await m.p.waitForTimeout(200); }
	await host.waitForTimeout(6500);
	await host.getByRole('button', { name: /Show results/ }).first().click();
	await host.waitForTimeout(1000);
	await host.getByRole('button', { name: 'Scoreboard' }).click();
	await host.waitForTimeout(1400);

	// Five rows, the rest counted, and the movement called out: Eve overtook Bo.
	await expect(host.getByRole('listitem')).toHaveCount(5);
	await expect(host.getByText(/and 1 more player/)).toBeVisible();
	await expect(host.getByLabel(/^up /)).toHaveCount(1);
	await expect(host.getByLabel(/^down /)).toHaveCount(1);

	// Last question: the scoreboard comes before the podium, not instead of it.
	await expect(host.getByRole('button', { name: 'Get final results' })).toBeVisible();
	await hostCtx.close();
	for (const m of made) await m.c.close();
});
