// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Motion, measured in a browser rather than asserted in the source.
//
// `src/lib/a11y/motion.test.ts` checks the scale is declared once and respected; this
// checks what the page actually does with it: that the podium really is held back and
// then released, that asking for less motion really does make it instant, and that the
// one element animating sixty times a second is composited rather than laid out.

import { expect, test } from '@playwright/test';
import { mc, saveQuiz, rememberAnonQuiz, hostFromViewPage, gotoPlayHydrated } from './helpers';

const QUIZ = {
	title: 'Motion',
	description: 'one',
	questions: [
		mc(
			'Pick A?',
			[
				['A', true],
				['B', false]
			],
			'5'
		)
	]
};

/** Plays one question through to the podium and leaves the host there. */
async function toPodium(browser, request, options: { reducedMotion?: 'reduce' | 'no-preference' }) {
	const saved = await saveQuiz(request, QUIZ);
	const hostCtx = await browser.newContext({
		viewport: { width: 1280, height: 800 },
		reducedMotion: options.reducedMotion
	});
	const host = await hostCtx.newPage();
	await rememberAnonQuiz(host, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(host, saved.body.id);

	const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
	const phone = await ctx.newPage();
	await gotoPlayHydrated(phone);
	await phone.getByRole('textbox', { name: 'Game PIN' }).fill(pin);
	await phone.getByRole('textbox', { name: 'Username' }).fill('Robin');
	await phone.getByRole('button', { name: 'Submit' }).click();
	await host.waitForTimeout(900);

	await host.getByRole('button', { name: /Start game/ }).first().click();
	await host.waitForTimeout(800);
	await host.getByRole('button', { name: /Next Question/ }).first().click();
	await host.waitForTimeout(1200);
	return { host, phone, hostCtx, ctx };
}

test('the question timer is composited, not laid out', async ({ browser, request }) => {
	test.setTimeout(3 * 60_000);
	const { host, hostCtx, ctx } = await toPodium(browser, request, {});

	// This bar redraws every second of every question, full width of a projector.
	// Animating `width` would make the browser lay the page out for each frame.
	const bar = host.getByRole('progressbar', { name: 'Time remaining' });
	const style = await bar.evaluate((el) => {
		const s = getComputedStyle(el);
		return { property: s.transitionProperty, transform: s.transform };
	});
	// Tailwind's `transition-transform` expands to the four transform properties, so this
	// is a set, not a single name. What matters is what is NOT in it.
	const animated = style.property.split(',').map((p) => p.trim());
	expect(animated, 'the timer does not animate a transform').toContain('transform');
	for (const banned of ['width', 'height', 'left', 'right', 'margin', 'padding', 'all']) {
		expect(animated, `the timer animates ${banned}, which forces layout`).not.toContain(banned);
	}
	expect(style.transform, 'the bar is drawn with a transform').toMatch(/^matrix\(/);

	await hostCtx.close();
	await ctx.close();
});

test('the podium is held back, then released', async ({ browser, request }) => {
	test.setTimeout(4 * 60_000);
	const { host, phone, hostCtx, ctx } = await toPodium(browser, request, {});
	await phone.getByRole('button', { name: /A/ }).first().click();
	await host.waitForTimeout(6500);
	await host.getByRole('button', { name: /Show results/ }).first().click();
	await host.waitForTimeout(1200);
	await host.getByRole('button', { name: 'Scoreboard' }).click();
	await host.waitForTimeout(600);
	await host.getByRole('button', { name: 'Get final results' }).click();

	const opacity = () =>
		host.locator('.podium-block.is-gold').evaluate((el) => Number(getComputedStyle(el).opacity));

	// A second in, the winner has not landed: the build-up is the point of the screen.
	await host.waitForTimeout(1000);
	expect(await opacity(), 'the winner arrived before the build-up ran').toBeLessThan(0.6);

	// By four, it has. The designed window is 600ms + 2 x 1400ms + 750ms.
	await expect.poll(opacity, { timeout: 5000 }).toBeGreaterThan(0.95);

	await hostCtx.close();
	await ctx.close();
});

test('asking for less motion makes the podium instant', async ({ browser, request }) => {
	test.setTimeout(4 * 60_000);
	const { host, phone, hostCtx, ctx } = await toPodium(browser, request, {
		reducedMotion: 'reduce'
	});
	await phone.getByRole('button', { name: /A/ }).first().click();
	await host.waitForTimeout(6500);
	await host.getByRole('button', { name: /Show results/ }).first().click();
	await host.waitForTimeout(1200);
	await host.getByRole('button', { name: 'Scoreboard' }).click();
	await host.waitForTimeout(600);
	await host.getByRole('button', { name: 'Get final results' }).click();

	// No build-up, no delay: everything is simply there. Svelte's transitions are
	// JavaScript and never see the media query, so this is `dur()` doing its job.
	await host.waitForTimeout(600);
	const states = await host.locator('.podium-block').evaluateAll((els) =>
		els.map((el) => Number(getComputedStyle(el).opacity))
	);
	expect(states.length).toBeGreaterThan(0);
	for (const o of states) expect(o, 'a block was still animating in').toBeGreaterThan(0.95);
	// And the crown, which is a CSS animation rather than a Svelte transition.
	await expect(host.locator('.crown')).toBeVisible();

	await hostCtx.close();
	await ctx.close();
});
