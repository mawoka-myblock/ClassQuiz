// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Deliberately hostile input, because every other spec in this suite uses "Lisbon" and
// "ana" and so proved nothing about a real room.
//
// Measured on 2026-10-02 against the code as it then was:
//   - a 272-character title with no spaces overflowed the player's lobby by 6611px at 390
//   - the same text as a question and an answer overflowed the host's screen by 7736px
//     at 1440
//   - a 5000-character title saved and stored intact; there was no bound of any kind
//
// Two independent defences went in: bounds on QuizInput, and wrap-anywhere at every place
// this text is rendered. Both are tested here, because a quiz saved before the bounds
// existed is never revalidated -- the CSS is what protects a room from those.

import { expect, test } from '@playwright/test';
import {
	expectNoHorizontalOverflow,
	gotoPlayHydrated,
	hostFromViewPage,
	joinAsPlayer,
	mc,
	rememberAnonQuiz,
	saveQuiz
} from './helpers';

/** 272 characters, not one of them a space. */
const LONG_TOKEN = 'Supercalifragilisticexpialidocious'.repeat(8);
const HUGE = 'x'.repeat(5000);

test.describe('the server refuses what would wreck a screen', () => {
	test('an over-long title, description, question and answer are each rejected', async ({
		request
	}) => {
		const base = {
			title: 'Fine',
			description: 'Fine',
			questions: [
				mc('Fine?', [
					['a', true],
					['b', false]
				])
			]
		};
		const cases: [string, object][] = [
			['title', { ...base, title: HUGE }],
			['description', { ...base, description: HUGE }],
			[
				'question',
				{
					...base,
					questions: [
						mc(HUGE, [
							['a', true],
							['b', false]
						])
					]
				}
			],
			[
				'answer',
				{
					...base,
					questions: [
						mc('Fine?', [
							[HUGE, true],
							['b', false]
						])
					]
				}
			]
		];
		for (const [field, quiz] of cases) {
			const res = await saveQuiz(request, quiz as never);
			// A refusal, not a 500, and not a silent accept.
			expect(res.status, `${field} was accepted at 5000 characters`).toBe(422);
		}
	});

	test('a quiz that fits the bounds still saves', async ({ request }) => {
		// The other half: a cap nobody can live within is a different bug.
		const res = await saveQuiz(request, {
			title: 'Q4 Security Awareness Refresher',
			description: 'Ten minutes, no prep needed. '.repeat(10).slice(0, 400),
			questions: [
				mc('Which of these is the safest way to share a password with a colleague?', [
					['A one-time secret link that expires after it is opened', true],
					['A chat message you delete afterwards', false]
				])
			]
		});
		expect(res.status).toBe(200);
	});
});

test('text that is already stored cannot push a layout sideways', async ({
	page,
	request,
	browser
}) => {
	// Saved through the model's own path, so this is as close to a pre-bounds quiz as the
	// suite can build: the title is inside the cap, the damage is that it cannot wrap.
	const saved = await saveQuiz(request, {
		title: LONG_TOKEN.slice(0, 90),
		description: LONG_TOKEN.slice(0, 200),
		questions: [
			mc(LONG_TOKEN.slice(0, 200), [
				[LONG_TOKEN.slice(0, 90), true],
				['b', false]
			])
		]
	});
	expect(saved.status).toBe(200);
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(page, saved.body.id);

	const player = await joinAsPlayer(browser, pin, 'ana');
	await expect(player.page.getByText(/You're in/)).toBeVisible();

	// The lobby is where the phone broke: the quiz title is the biggest thing on it.
	await expectNoHorizontalOverflow(player.page);
	await expectNoHorizontalOverflow(page);

	await page
		.getByRole('button', { name: /Start game/ })
		.first()
		.click();
	await page
		.getByRole('button', { name: /Next Question/ })
		.first()
		.click();
	await expect(page.getByText(/Supercalifragilistic/).first()).toBeVisible({ timeout: 15_000 });

	// And the host screen is where the projector broke.
	await expectNoHorizontalOverflow(page);
	await expectNoHorizontalOverflow(player.page);

	await player.context.close();
});

test('a nickname cannot be used to wreck the host’s player list', async ({
	page,
	request,
	browser
}) => {
	// The join form caps at 17 characters, but the socket server is reachable without it,
	// so the bound that matters is MAX_USERNAME_LENGTH = 50 on the server. These are the
	// shapes that cost more width or height than their length suggests: combining marks
	// stack vertically, CJK is double-width, and emoji are wider still.
	const saved = await saveQuiz(request, {
		title: 'Nickname stress',
		description: 'e2e',
		questions: [
			mc('Capital of Portugal?', [
				['Lisbon', true],
				['Porto', false]
			])
		]
	});
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(page, saved.body.id);

	const names = [
		'A' + '̴̵̶̷̸͇͈̈́͆ͅ'.repeat(4),
		'東京特許許可局'.repeat(7),
		'🐸'.repeat(25),
		'Supercalifragilisticexpialidociousx'.repeat(2).slice(0, 50)
	];
	const joined = [];
	for (const name of names) {
		const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
		const p = await ctx.newPage();
		// The PIN box is server-rendered and autofocused, so anything typed before
		// hydration is thrown away and the form never advances. The first version of this
		// test used a bare goto and sat on the PIN step until the 60s timeout.
		await gotoPlayHydrated(p);
		await p.getByRole('textbox', { name: 'Game PIN' }).fill(pin);
		await expect(p.getByRole('textbox', { name: 'Username' })).toBeVisible({
			timeout: 15_000
		});
		// The form's maxlength is bypassed the way a scripted client would bypass it, so
		// this tests the server's bound rather than the input's.
		await p
			.getByRole('textbox', { name: 'Username' })
			.evaluate((el: HTMLInputElement, v: string) => {
				el.value = v;
				el.dispatchEvent(new Event('input', { bubbles: true }));
			}, name);
		await p.getByRole('button', { name: 'Submit' }).click();
		await expect(p.getByText(/You're in/)).toBeVisible({ timeout: 15_000 });
		await expectNoHorizontalOverflow(p);
		joined.push(ctx);
	}

	// Four hostile names on one projector at once.
	await expect(page.getByText(/4|players/i).first()).toBeVisible();
	await expectNoHorizontalOverflow(page);

	for (const ctx of joined) await ctx.close();
});
