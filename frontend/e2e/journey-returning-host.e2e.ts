// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// The second time somebody uses frogQuiz, which is the version that decides whether they
// keep using it: log in, find the quiz you made last month, change it, run it again.
//
// This is the journey D9 is about -- "an account is what makes a quiz permanent"
// (François, 2026-10-02). If any step here breaks, an account buys nothing.

import { expect, test } from '@playwright/test';
import { PASSWORD, apiLogin, registerUser } from './accounts';
import {
	advanceToFinalResults,
	joinAsPlayer,
	mc,
	saveQuiz,
	saveQuizButton,
	titleBox
} from './helpers';

test('somebody comes back, finds their quiz, changes it and runs it again', async ({
	page,
	request,
	browser
}) => {
	const stamp = Date.now();
	const originalTitle = `Last month ${stamp}`;
	const newDescription = 'Updated before the second run';

	const user = await registerUser(request);
	await apiLogin(request, user.email);
	const saved = await saveQuiz(request, {
		title: originalTitle,
		description: 'As first written',
		questions: [
			mc('Capital of Portugal?', [
				['Lisbon', true],
				['Porto', false]
			])
		]
	});
	expect(saved.status).toBe(200);
	expect(saved.secret, 'a signed-in save is not anonymous').toBeFalsy();

	await test.step('they log in', async () => {
		await page.goto('/account/login');
		await page.getByRole('textbox', { name: 'Email or Username' }).fill(user.email);
		await page.getByRole('button', { name: 'Continue' }).click();
		await page.getByRole('textbox', { name: 'Password' }).fill(PASSWORD);
		await page.getByRole('button', { name: 'Continue' }).last().click();
		await page.waitForURL((u) => !u.pathname.startsWith('/account/login'), {
			timeout: 15_000
		});
	});

	await test.step('their quiz is waiting on My Quizzes', async () => {
		await page.goto('/my-quizzes');
		await expect(page.getByText(originalTitle)).toBeVisible();
		// It belongs to the account, so it carries no browser-expiry warning.
		await expect(page.getByText(/deleted after 30 days/i)).toHaveCount(0);
	});

	await test.step('they open it, change it, and the change sticks', async () => {
		await page.goto(`/edit?quiz_id=${saved.body.id}`);
		// The title is a CKEditor contenteditable, not an input, so toHaveValue throws
		// "Not an input element" rather than failing on the value.
		await expect(titleBox(page)).toHaveText(originalTitle, { timeout: 20_000 });
		await page
			.getByRole('textbox', { name: 'Description' })
			.first()
			.fill(newDescription, { timeout: 20_000 });
		await saveQuizButton(page).click();
		await page.waitForURL(new RegExp(`/view/${saved.body.id}`));

		// Read back from the server, not from the page that just wrote it.
		const stored = await (await page.request.get(`/api/v1/quiz/get/${saved.body.id}`)).json();
		expect(stored.description).toBe(newDescription);
	});

	await test.step('and they run it again', async () => {
		await page.getByRole('button', { name: 'Play', exact: true }).click();
		const dialog = page.getByRole('dialog', { name: 'Start Game' });
		await expect(dialog).toBeVisible();
		await dialog.getByRole('button', { name: 'Start Game' }).click();
		await page.waitForURL(/\/admin\?/);
		const pin = new URL(page.url()).searchParams.get('pin')!;

		const player = await joinAsPlayer(browser, pin, 'ana');
		await expect(player.page.getByText(/You're in/)).toBeVisible();
		await page
			.getByRole('button', { name: /Start game/ })
			.first()
			.click();
		await page
			.getByRole('button', { name: /Next Question/ })
			.first()
			.click();
		await player.page.getByRole('button', { name: 'Lisbon' }).click();
		await page
			.getByRole('button', { name: /Show results/ })
			.first()
			.click();
		await advanceToFinalResults(page);
		await expect(page.getByText('ana', { exact: true }).first()).toBeVisible({
			timeout: 20_000
		});
		await player.context.close();
	});

	await test.step('and it is still on My Quizzes afterwards', async () => {
		await page.goto('/my-quizzes');
		await expect(page.getByText(originalTitle)).toBeVisible();
	});
});
