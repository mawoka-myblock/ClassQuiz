// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Lobby music, and the control that turns it off. A room has to be able to stop it
// without hunting, and a browser will not start audio without a gesture, so the control
// has to be honest about which state it is in.

import { test, expect } from '@playwright/test';
import { mc, saveQuiz, rememberAnonQuiz, hostFromViewPage } from './helpers';
test('the lobby offers music, with a way to turn it off', async ({ browser, request }) => {
	test.setTimeout(4 * 60_000);
	const saved = await saveQuiz(request, { title: 'Music', description: 'one',
		questions: [mc('A?', [['A', true], ['B', false]], '5')] });
	const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
	const host = await ctx.newPage();
	await rememberAnonQuiz(host, saved.body.id, saved.secret!);
	await hostFromViewPage(host, saved.body.id);
	await host.waitForTimeout(1500);
	// The control is there and says what it does.
	await expect(host.getByRole('button', { name: /Turn the music (on|off)/ })).toBeVisible();
	await expect(host.getByRole('slider', { name: 'Music volume' })).toBeVisible();

	// The choice outlives the game: a host who turns it off should not fight it again.
	await host.getByRole('button', { name: /Turn the music off/ }).click();
	await expect(host.getByRole('button', { name: /Turn the music on/ })).toBeVisible();
	expect(
		await host.evaluate(() => JSON.parse(localStorage.getItem('frogquiz_music') ?? '{}').on)
	).toBe(false);

	// And it is only in the lobby: nothing on the player's screen plays anything.
	await expect(host.locator('audio')).toHaveCount(0);
	await ctx.close();
});
