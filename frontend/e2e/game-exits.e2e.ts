// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Every way out of a live game, driven through the UI: the host cancelling from the
// lobby or ending mid-game, a player leaving, and the join screen's own way home.
// Before these existed the only exit from any of them was closing the tab.

import { expect, test } from '@playwright/test';
import {
	gotoPlayHydrated,
	hostFromViewPage,
	joinAsPlayer,
	mc,
	rememberAnonQuiz,
	saveQuiz
} from './helpers';

const QUIZ = {
	title: 'Exits',
	description: 'e2e',
	questions: [
		mc('One?', [
			['yes', true],
			['no', false]
		]),
		mc('Two?', [
			['yes', true],
			['no', false]
		])
	]
};

async function hostAnon(page, request) {
	const saved = await saveQuiz(request, QUIZ);
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);
	return hostFromViewPage(page, saved.body.id);
}

test('the join screen has a way home and says what is wrong inline', async ({ page }) => {
	let dialogs = 0;
	page.on('dialog', (d) => {
		dialogs++;
		d.dismiss();
	});
	await gotoPlayHydrated(page);
	await expect(page.getByRole('link', { name: 'Home' })).toHaveAttribute('href', '/');
	await page.getByRole('textbox', { name: 'Game PIN' }).fill('000000');
	await expect(page.getByRole('alert')).toContainText('No game with that PIN');
	expect(dialogs, 'a browser alert() was shown').toBe(0);
});

test('a two-letter nickname can join', async ({ page, browser, request }) => {
	const pin = await hostAnon(page, request);
	const { context, page: phone } = await joinAsPlayer(browser, pin, 'Al');
	await expect(phone.getByText("You're in, Al")).toBeVisible();
	await context.close();
});

test('the host cancels from the lobby: host goes to My Quizzes, player is told', async ({
	page,
	browser,
	request
}) => {
	const pin = await hostAnon(page, request);
	const { context, page: phone } = await joinAsPlayer(browser, pin, 'waiter');
	await expect(page.getByRole('button', { name: /waiter/ })).toBeVisible();

	await page.getByRole('button', { name: 'Cancel game' }).click();
	await page.getByRole('alertdialog').getByRole('button', { name: 'Cancel game' }).click();
	await page.waitForURL(/\/my-quizzes/);
	await expect(phone.getByText('The host ended the game')).toBeVisible();
	await expect(phone.getByRole('link', { name: 'Home' })).toBeVisible();
	await context.close();
});

test('a player leaves the lobby: back on the join screen, gone from the host', async ({
	page,
	browser,
	request
}) => {
	const pin = await hostAnon(page, request);
	const { context, page: phone } = await joinAsPlayer(browser, pin, 'leaver');
	await expect(page.getByRole('button', { name: /leaver/ })).toBeVisible();

	await phone.getByRole('button', { name: 'Leave game' }).click();
	await phone.getByRole('alertdialog').getByRole('button', { name: 'Leave game' }).click();
	await expect(phone.getByRole('textbox', { name: 'Game PIN' })).toBeVisible();
	await expect(page.getByRole('button', { name: /leaver/ })).toHaveCount(0);
	await context.close();
});

test('the host ends mid-game: everyone gets the podium, Back goes to My Quizzes', async ({
	page,
	browser,
	request
}) => {
	const pin = await hostAnon(page, request);
	const { context, page: phone } = await joinAsPlayer(browser, pin, 'player');
	await expect(page.getByRole('button', { name: /player/ })).toBeVisible();
	await page.getByRole('button', { name: 'Start game' }).click();

	await page.getByRole('button', { name: 'End game' }).click();
	await page.getByRole('alertdialog').getByRole('button', { name: 'End game' }).click();
	await expect(page.getByRole('link', { name: 'Back' })).toHaveAttribute('href', '/my-quizzes');
	await expect(phone.getByRole('link', { name: 'Home' })).toBeVisible();
	await context.close();
});
