// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Running a quiz on a video call, which is how this team will mostly use it.
//
// Nobody is looking at a shared screen, so the host turns on "Show questions and answers
// on players' devices" (MVP.md D16, François 2026-10-02: "make it like Kahoot" -- and
// Kahoot ships exactly this setting, free, off by default). player-screen.e2e.ts proves
// the switch changes one question; this plays a whole game through it, because the
// failure that matters is a player who can read question 1 and then finds question 2
// blank.

import { expect, test } from '@playwright/test';
import {
	advanceToFinalResults,
	advancePastResults,
	expectNoHorizontalOverflow,
	hostFromViewPage,
	joinAsPlayer,
	mc,
	rememberAnonQuiz,
	saveQuiz
} from './helpers';

const Q1 = 'Capital of Portugal?';
const Q2 = 'Which is a frog?';

test('a host with nobody in the room runs the whole game on everyone’s phones', async ({
	page,
	request,
	browser
}) => {
	const saved = await saveQuiz(request, {
		title: `Call round ${Date.now()}`,
		description: 'e2e',
		questions: [
			mc(Q1, [
				['Lisbon', true],
				['Porto', false]
			]),
			mc(Q2, [
				['Tree frog', true],
				['Gecko', false]
			])
		]
	});
	expect(saved.status).toBe(200);
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);

	let pin = '';
	await test.step('the host turns the setting on before starting', async () => {
		pin = await hostFromViewPage(page, saved.body.id, { showOnDevices: true });
	});

	const ana = await joinAsPlayer(browser, pin, 'ana');
	const bruno = await joinAsPlayer(browser, pin, 'bruno');
	for (const p of [ana, bruno]) await expect(p.page.getByText(/You're in/)).toBeVisible();

	await test.step('question one is readable on the phone, not just the host screen', async () => {
		await page
			.getByRole('button', { name: /Start game/ })
			.first()
			.click();
		await page
			.getByRole('button', { name: /Next Question/ })
			.first()
			.click();

		for (const p of [ana, bruno]) {
			await expect(p.page.getByText(Q1)).toBeVisible({ timeout: 15_000 });
			await expect(p.page.getByText('Lisbon', { exact: true })).toBeVisible();
			await expect(p.page.getByText('Porto', { exact: true })).toBeVisible();
			// The whole point is a phone held alone; it has to fit one.
			await expectNoHorizontalOverflow(p.page);
		}

		await ana.page.getByRole('button', { name: 'Lisbon' }).click();
		await bruno.page.getByRole('button', { name: 'Porto' }).click();
		await page
			.getByRole('button', { name: /Show results/ })
			.first()
			.click();
		await expect(ana.page.getByText('Correct!')).toBeVisible({ timeout: 15_000 });
		await expect(bruno.page.getByText('Not this time')).toBeVisible();
	});

	await test.step('and so is question two, which is where this would break', async () => {
		await advancePastResults(page);
		for (const p of [ana, bruno]) {
			await expect(p.page.getByText(Q2)).toBeVisible({ timeout: 15_000 });
			await expect(p.page.getByText('Tree frog', { exact: true })).toBeVisible();
		}
		await ana.page.getByRole('button', { name: 'Tree frog' }).click();
		await bruno.page.getByRole('button', { name: 'Tree frog' }).click();
		await page
			.getByRole('button', { name: /Show results/ })
			.first()
			.click();
	});

	await test.step('the game ends on the podium as usual', async () => {
		await advanceToFinalResults(page);
		await expect(page.getByText('ana', { exact: true }).first()).toBeVisible({
			timeout: 20_000
		});
		for (const p of [ana, bruno]) await expectNoHorizontalOverflow(p.page);
	});

	await ana.context.close();
	await bruno.context.close();
});
