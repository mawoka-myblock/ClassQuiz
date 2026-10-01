// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// What a player is told after a question. It used to be a bare "+760", so somebody who
// scored 0 could not tell a wrong answer from a broken game.

import { test, expect } from '@playwright/test';
import { mc, saveQuiz, rememberAnonQuiz, hostFromViewPage, gotoPlayHydrated } from './helpers';
test('a player is told whether they were right, and where they stand', async ({ browser, request }) => {
	test.setTimeout(5 * 60_000);
	const saved = await saveQuiz(request, {
		title: 'Feedback', description: 'one',
		questions: [mc('Pick A?', [['A', true], ['B', false]], '5')]
	});
	const hostCtx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
	const host = await hostCtx.newPage();
	await rememberAnonQuiz(host, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(host, saved.body.id);
	const mk = async (name: string) => {
		const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
		const p = await ctx.newPage();
		await gotoPlayHydrated(p);
		await p.getByRole('textbox', { name: 'Game PIN' }).fill(pin);
		await p.getByRole('textbox', { name: 'Username' }).fill(name);
		await p.getByRole('button', { name: 'Submit' }).click();
		return { ctx, p };
	};
	const good = await mk('Winner');
	const bad = await mk('Loser');
	await host.waitForTimeout(1000);
	await host.getByRole('button', { name: /Start game/ }).first().click();
	await host.waitForTimeout(900);
	await host.getByRole('button', { name: /Next Question/ }).first().click();
	await host.waitForTimeout(1200);
	await good.p.getByRole('button', { name: /A/ }).first().click();
	await bad.p.getByRole('button', { name: /B/ }).last().click();
	await host.waitForTimeout(6500);
	await host.getByRole('button', { name: /Show results/ }).first().click();
	await host.waitForTimeout(1500);
	await expect(good.p.getByText('Correct!')).toBeVisible();
	await expect(bad.p.getByText('Not this time')).toBeVisible();
	await expect(good.p.getByText(/1 of 2/)).toBeVisible();
	await expect(bad.p.getByText(/2 of 2/)).toBeVisible();
	await expect(bad.p.getByText('+0')).toBeVisible();
	await hostCtx.close(); await good.ctx.close(); await bad.ctx.close();
});
