// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// The host's one piece of record-keeping: the answers from the game just played, as a
// spreadsheet. It used to take two presses -- one to mint a token over the socket, one
// to spend it -- with the button renaming itself in between.

import { test, expect } from '@playwright/test';
import { mc, saveQuiz, rememberAnonQuiz, hostFromViewPage, gotoPlayHydrated } from './helpers';
test('the host downloads the game\u2019s answers in one press', async ({ browser, request }) => {
	test.setTimeout(5 * 60_000);
	const saved = await saveQuiz(request, { title: 'Export', description: 'one',
		questions: [mc('Pick A?', [['A', true], ['B', false]], '5')] });
	const hostCtx = await browser.newContext({ viewport: { width: 1280, height: 800 }, acceptDownloads: true });
	const host = await hostCtx.newPage();
	await rememberAnonQuiz(host, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(host, saved.body.id);
	const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
	const p = await ctx.newPage();
	await gotoPlayHydrated(p);
	await p.getByRole('textbox', { name: 'Game PIN' }).fill(pin);
	await p.getByRole('textbox', { name: 'Username' }).fill('Robin');
	await p.getByRole('button', { name: 'Submit' }).click();
	await host.waitForTimeout(900);
	await host.getByRole('button', { name: /Start game/ }).first().click();
	await host.waitForTimeout(800);
	await host.getByRole('button', { name: /Next Question/ }).first().click();
	await host.waitForTimeout(1200);
	await p.getByRole('button', { name: /A/ }).first().click();
	await host.waitForTimeout(6500);
	await host.getByRole('button', { name: /Show results/ }).first().click();
	await host.waitForTimeout(1200);
	await host.getByRole('button', { name: 'Get final results' }).click();
	await host.waitForTimeout(5500);
	// One press: the token is minted over the socket and the download starts on arrival.
	const download = host.waitForEvent('download', { timeout: 20_000 });
	await host.getByRole('button', { name: 'Download results' }).click();
	const file = await download;
	expect(file.suggestedFilename()).toMatch(/\.xls/);
	await hostCtx.close(); await ctx.close();
});
