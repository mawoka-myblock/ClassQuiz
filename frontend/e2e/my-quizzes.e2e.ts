// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// My Quizzes is one page for everyone (MVP.md decision D1): this browser's quizzes when
// signed out, the account's when signed in, with this browser's listed underneath to
// claim. It replaced /dashboard, which stays as a redirect.

import { expect, test } from '@playwright/test';
import { signedInContext } from './accounts';
import { expectNoHorizontalOverflow, mc, rememberAnonQuiz, saveQuiz } from './helpers';

const quiz = (title: string) => ({
	title,
	description: 'e2e',
	questions: [
		mc('Q?', [
			['yes', true],
			['no', false]
		])
	]
});

test('/dashboard and /overview land on My Quizzes', async ({ page }) => {
	await page.goto('/dashboard');
	await expect(page).toHaveURL(/\/my-quizzes$/);
	await page.goto('/overview');
	await expect(page).toHaveURL(/\/my-quizzes$/);
});

test('signed out: the navbar marks My Quizzes, and Create needs no account', async ({ page }) => {
	await page.goto('/my-quizzes');
	await expect(page.getByRole('heading', { name: 'My Quizzes', level: 1 })).toBeVisible();
	const nav = page.getByRole('navigation');
	await expect(nav.getByRole('link', { name: 'My Quizzes' }).first()).toHaveAttribute(
		'aria-current',
		'page'
	);
	await expect(nav.getByRole('link', { name: 'Join' }).first()).not.toHaveAttribute(
		'aria-current',
		'page'
	);
	await expect(page.getByText(/linked to this browser/)).toBeVisible();

	await page.getByRole('link', { name: 'Create a new quiz' }).first().click();
	await expect(page).toHaveURL(/\/create$/);
});

test('signed out: a browser quiz is listed with its expiry and can be deleted', async ({
	page,
	request
}) => {
	const title = `Mine ${Date.now()}`;
	const saved = await saveQuiz(request, quiz(title));
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);
	await page.goto('/my-quizzes');

	const row = page.getByRole('listitem').filter({ hasText: title });
	await expect(row).toBeVisible();
	await expect(row.getByText(/Expires in \d+ days?/)).toBeVisible();
	await expectNoHorizontalOverflow(page);

	await row.getByRole('button', { name: 'Delete' }).click();
	await page.getByRole('alertdialog').getByRole('button', { name: 'Delete' }).click();
	await expect(row).toHaveCount(0);
	const gone = await request.get(`/api/v1/quiz/get/public/${saved.body.id}`);
	expect(gone.status()).toBe(404);
});

test('signed in: browser quizzes sit under the account list and Claim moves them in', async ({
	browser,
	request
}) => {
	const user = await signedInContext(browser, request);
	const owned = `Owned ${Date.now()}`;
	await saveQuiz(user.context.request, quiz(owned));
	const loose = `Loose ${Date.now()}`;
	const anon = await saveQuiz(request, quiz(loose));
	await rememberAnonQuiz(user.page, anon.body.id, anon.secret!);

	await user.page.goto('/my-quizzes');
	await expect(user.page.getByRole('link', { name: owned })).toBeVisible();
	const section = user.page.getByRole('region', { name: 'On this browser' });
	await expect(section.getByRole('link', { name: loose })).toBeVisible();

	await section.getByRole('button', { name: 'Claim' }).click();
	await expect(user.page.getByRole('region', { name: 'On this browser' })).toHaveCount(0);
	await expect(user.page.getByRole('link', { name: loose })).toBeVisible();
	await user.context.close();
});
