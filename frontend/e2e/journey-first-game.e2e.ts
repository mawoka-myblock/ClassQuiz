// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// The journey the product is built around, start to finish and without an account:
// Create -> Edit -> Start -> Play -> Finish -> Return.
//
// Every step here is covered somewhere else by a test of the mechanism -- the editor
// column, the socket protocol, the podium. What nothing covered is the whole thing
// hanging together from the landing page, which is the only version of it a new
// colleague will ever experience. A journey test fails for a different reason than a
// feature test: not "this control is wrong" but "you cannot get from here to there".

import { expect, test } from '@playwright/test';
import {
	addQuestion,
	advancePastResults,
	advanceToFinalResults,
	expectNoHorizontalOverflow,
	joinAsPlayer,
	saveQuizButton,
	startNewQuiz
} from './helpers';

test('a new colleague makes a quiz and runs it for two people, with no account', async ({
	page,
	browser
}) => {
	const title = `Team round ${Date.now()}`;

	await test.step('they arrive and find the way in without signing up', async () => {
		await page.goto('/');
		// Creating must not be behind a login: the whole anonymous path depends on this
		// being the obvious next click on the landing page.
		await page
			.getByRole('link', { name: /^Create/ })
			.first()
			.click();
		await expect(page).toHaveURL(/\/create/);
	});

	await test.step('they write two questions', async () => {
		await startNewQuiz(page, title);
		await addQuestion(page, /^Multiple-Choice/, 'Which of these is a frog?', [
			['Tree frog', true],
			['Gecko', false]
		]);
		await addQuestion(page, /^Check Choice/, 'Which are amphibians?', [
			['Frog', true],
			['Salamander', true],
			['Lizard', false]
		]);
		await saveQuizButton(page).click();
		await page.waitForURL(/\/view\//);
	});

	await test.step('the quiz is theirs, in this browser, and says so', async () => {
		// The one thing an anonymous user has to understand, or they will lose work.
		await expect(page.getByText("This quiz isn't saved to an account")).toBeVisible();
	});

	let pin = '';
	await test.step('they start a game', async () => {
		await page.getByRole('button', { name: 'Play', exact: true }).click();
		const dialog = page.getByRole('dialog', { name: 'Start Game' });
		await expect(dialog).toBeVisible();
		await dialog.getByRole('button', { name: 'Start Game' }).click();
		await page.waitForURL(/\/admin\?/);
		pin = new URL(page.url()).searchParams.get('pin')!;
		expect(pin, 'the lobby shows a PIN to read out').toMatch(/^\d{6}$/);
	});

	const players = [];
	await test.step('two colleagues join on their phones', async () => {
		for (const name of ['ana', 'bruno']) players.push(await joinAsPlayer(browser, pin, name));
		for (const p of players) {
			await expect(p.page.getByText(/You're in/)).toBeVisible();
			await expectNoHorizontalOverflow(p.page);
		}
		// The host can see who is in the room before starting.
		for (const name of ['ana', 'bruno'])
			await expect(page.getByText(name, { exact: true })).toBeVisible();
	});

	const [ana, bruno] = players.map((p) => p.page);
	await test.step('they play both questions', async () => {
		await page.getByRole('button', { name: 'Start game' }).click();
		await page.getByRole('button', { name: /Next Question/ }).click();

		await ana.getByRole('button', { name: 'Tree frog' }).click();
		await bruno.getByRole('button', { name: 'Gecko' }).click();
		await page.getByRole('button', { name: 'Show results' }).click();
		// Each player is told how they did, which is the whole point of playing.
		await expect(ana.getByText(/correct/i).first()).toBeVisible({ timeout: 15_000 });

		await advancePastResults(page);
		// A multi-answer question needs every right answer and no wrong one.
		await ana.getByRole('button', { name: 'Frog' }).click();
		await ana.getByRole('button', { name: 'Salamander' }).click();
		await ana.getByRole('button', { name: /Submit|Done|Confirm/i }).click();
		await bruno.getByRole('button', { name: 'Frog' }).click();
		await bruno.getByRole('button', { name: /Submit|Done|Confirm/i }).click();
		await page.getByRole('button', { name: 'Show results' }).click();
	});

	await test.step('the game finishes on the podium', async () => {
		await advanceToFinalResults(page);
		// ana got both right and bruno did not, so the order is not a coin toss.
		await expect(page.getByText('ana', { exact: true }).first()).toBeVisible({
			timeout: 20_000
		});
		await expectNoHorizontalOverflow(page);
		for (const p of [ana, bruno]) await expectNoHorizontalOverflow(p);
	});

	await test.step('and they land back where their quizzes are', async () => {
		await page
			.getByRole('button', { name: /Back|My Quizzes|Finish/i })
			.first()
			.click();
		await page.waitForURL(/\/my-quizzes/);
		// The quiz they just made is still there afterwards, in this browser.
		await expect(page.getByText(title)).toBeVisible();
	});

	for (const p of players) await p.context.close();
});
