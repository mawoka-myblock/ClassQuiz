// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// One player, one phone, the whole arc: join, wait, answer, be told, wait again, answer
// again, see the podium, leave.
//
// Every screen here is asserted somewhere else -- player-feedback, player-medal,
// scoreboard, podium -- but each of those sets up its own game and looks at one screen.
// This is the only test that holds a single phone through all of them in order, which is
// the only way to catch a transition that works in isolation and strands the player when
// it follows the previous one. CLAUDE.md: neither half of a live game is the secondary
// case, and the player's half is always a phone.

import { expect, test } from '@playwright/test';
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

test('a player goes from the join screen to the podium and out, all on a phone', async ({
	page,
	request,
	browser
}) => {
	const saved = await saveQuiz(request, {
		title: `Phone round ${Date.now()}`,
		description: 'e2e',
		questions: [
			mc('Capital of Portugal?', [
				['Lisbon', true],
				['Porto', false]
			]),
			mc('Which is a frog?', [
				['Tree frog', true],
				['Gecko', false]
			])
		]
	});
	expect(saved.status).toBe(200);
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(page, saved.body.id);

	// A second player, so the standings have somebody to stand against.
	const rival = await joinAsPlayer(browser, pin, 'bruno');
	const me = await joinAsPlayer(browser, pin, 'ana');
	const phone = me.page;

	await test.step('they are in, and told so', async () => {
		await expect(phone.getByText(/You're in/)).toBeVisible();
		await expect(phone.getByText(/Waiting for the host/i)).toBeVisible();
		await expectNoHorizontalOverflow(phone);
	});

	await test.step('they answer the first question and are told they were right', async () => {
		await page
			.getByRole('button', { name: /Start game/ })
			.first()
			.click();
		await page
			.getByRole('button', { name: /Next Question/ })
			.first()
			.click();
		const lisbon = phone.getByRole('button', { name: 'Lisbon' });
		await lisbon.click();
		// The tiles stay up with their pick held until the timer ends -- "Answer locked
		// in" is the screen *after* that, not the acknowledgement of the tap. Kahoot does
		// the same. Asserting the copy here failed against correct behaviour; the page
		// snapshot showed the timer still at 10 with the tile [disabled] [pressed].
		await expect(lisbon).toBeDisabled();
		await expect(lisbon).toHaveAttribute('aria-pressed', 'true');
		await expect(phone.getByRole('button', { name: 'Porto' })).toBeDisabled();
		await expectNoHorizontalOverflow(phone);

		await rival.page.getByRole('button', { name: 'Porto' }).click();
		await page
			.getByRole('button', { name: /Show results/ })
			.first()
			.click();
		await expect(phone.getByText('Correct!')).toBeVisible({ timeout: 15_000 });
		// Points and standing, not just a tick -- the thing players actually look for.
		await expect(phone.getByText(/1 of 2/)).toBeVisible();
		await expectNoHorizontalOverflow(phone);
	});

	await test.step('they wait through the standings and answer the second', async () => {
		await advancePastResults(page);
		const gecko = phone.getByRole('button', { name: 'Gecko' });
		await gecko.click();
		await expect(gecko).toHaveAttribute('aria-pressed', 'true');
		await rival.page.getByRole('button', { name: 'Tree frog' }).click();
		await page
			.getByRole('button', { name: /Show results/ })
			.first()
			.click();
		await expect(phone.getByText('Not this time')).toBeVisible({ timeout: 15_000 });
	});

	await test.step('the podium reaches their phone too', async () => {
		await advanceToFinalResults(page);
		// They tied on one right each; whatever the order, their own screen names them.
		await expect(phone.getByText(/ana|place|Place/).first()).toBeVisible({ timeout: 20_000 });
		await expectNoHorizontalOverflow(phone);
	});

	await test.step('and there is a way out that actually leaves', async () => {
		await phone.getByRole('button', { name: 'Leave game' }).click();
		await phone.getByRole('alertdialog').getByRole('button', { name: 'Leave game' }).click();
		// Back where they started, ready to join another game.
		await expect(phone.getByRole('textbox', { name: 'Game PIN' })).toBeVisible({
			timeout: 15_000
		});
		await expectNoHorizontalOverflow(phone);
	});

	await me.context.close();
	await rival.context.close();
});
