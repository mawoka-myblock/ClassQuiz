// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// The second journey the product is for: somebody else's quiz. CLAUDE.md keeps the
// search bar specifically so people can find "quizzes made by other people on the team",
// so this walks that: publish, find, open, run.
//
// It also pins the boundary around it. A teammate can host your quiz but must not be
// able to read its answer key first -- on screen (D12) or as a spreadsheet (D18, closed
// 2026-10-02). Those two were tested separately and contradicted each other for a day;
// here they are asserted on the same page, as one person experiences them.

import { expect, test } from '@playwright/test';
import { signedInContext } from './accounts';
import { advanceToFinalResults, joinAsPlayer, mc, saveQuiz } from './helpers';

test('a teammate finds a colleague’s quiz, runs it, and never sees the answers', async ({
	browser,
	request
}) => {
	const title = `Shared round ${Date.now()}`;
	const owner = await signedInContext(browser, request);
	const mate = await signedInContext(browser, request);

	await test.step('the owner publishes a quiz', async () => {
		const saved = await saveQuiz(owner.context.request, {
			title,
			description: 'For the team',
			public: true,
			questions: [
				mc('Capital of Portugal?', [
					['Lisbon', true],
					['Porto', false]
				])
			]
		});
		expect(saved.status).toBe(200);
	});

	let viewUrl = '';
	await test.step('the teammate finds it in Discover', async () => {
		await mate.page.goto('/explore');
		await mate.page.getByRole('searchbox').first().fill(title);
		// Meilisearch indexes on save; the page searches from three characters up.
		const card = mate.page.getByText(title).first();
		await expect(card).toBeVisible({ timeout: 20_000 });
		await card.click();
		await mate.page.waitForURL(/\/view\//);
		viewUrl = mate.page.url();
	});

	await test.step('the page does not hand them the answer key', async () => {
		// D12 hides WHICH answer is right, not the answers themselves -- a visitor is meant
		// to see what the quiz asks, in a shuffled order, so they can decide whether to
		// play it. The first version of this test asserted the answer text was absent
		// entirely, and failed against correct behaviour.
		await expect(mate.page.getByText('Lisbon')).toBeVisible();
		// The marker is a ring plus a tick carrying an sr-only "Correct". That label is
		// the thing a visitor must never get.
		await expect(mate.page.getByText('Correct', { exact: true })).toHaveCount(0);
		// D18: nor as a spreadsheet. Both halves, because hiding a button is not a guard.
		await expect(mate.page.getByRole('button', { name: 'Download' })).toHaveCount(0);
		const id = new URL(viewUrl).pathname.split('/view/')[1];
		const res = await mate.context.request.get(`/api/v1/eximport/excel/${id}`);
		expect(res.status(), 'a teammate downloaded the answer key').toBe(404);
		// Editing is the owner's too.
		await expect(mate.page.getByRole('link', { name: 'Edit' })).toHaveCount(0);
	});

	await test.step('the owner, on the same page, does see which answer is right', async () => {
		// The other half of D12. Without this, the assertion above would pass just as well
		// if the marker had been deleted for everybody.
		await owner.page.goto(viewUrl);
		await expect(owner.page.getByText('Correct', { exact: true }).first()).toBeVisible();
	});

	await test.step('but they can run it, which is the point of sharing', async () => {
		await mate.page.getByRole('button', { name: 'Play', exact: true }).click();
		const dialog = mate.page.getByRole('dialog', { name: 'Start Game' });
		await expect(dialog).toBeVisible();
		await dialog.getByRole('button', { name: 'Start Game' }).click();
		await mate.page.waitForURL(/\/admin\?/);
		const pin = new URL(mate.page.url()).searchParams.get('pin')!;

		const player = await joinAsPlayer(browser, pin, 'ana');
		await expect(player.page.getByText(/You're in/)).toBeVisible();
		await mate.page.getByRole('button', { name: 'Start game' }).click();
		await mate.page.getByRole('button', { name: /Next Question/ }).click();
		await player.page.getByRole('button', { name: 'Lisbon' }).click();
		await mate.page.getByRole('button', { name: 'Show results' }).click();
		await advanceToFinalResults(mate.page);
		await expect(mate.page.getByText('ana', { exact: true }).first()).toBeVisible({
			timeout: 20_000
		});
		await player.context.close();
	});

	await owner.context.close();
	await mate.context.close();
});
