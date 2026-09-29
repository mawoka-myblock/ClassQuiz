// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// The signed-in side: registering, logging in, owning quizzes, claiming an anonymous one,
// publishing to Explore, and keeping game results.

import { expect, test, type Page } from '@playwright/test';
import { PASSWORD, apiLogin, registerUser, signedInContext } from './accounts';
import { expectNoHorizontalOverflow, mc, rememberAnonQuiz, saveQuiz } from './helpers';
import { closeAll, finalResults, hostGame, joinAll, next, showQuestion } from './sockets';

const quiz = (title: string, extra: Record<string, unknown> = {}) => ({
	title,
	description: 'e2e',
	questions: [
		mc('Capital of Portugal?', [
			['Lisbon', true],
			['Porto', false]
		])
	],
	...extra
});

test.afterEach(closeAll);

/** The login page is two forms: identify, then prove. Each has its own Continue. */
async function logInThroughUI(page: Page, email: string, password: string) {
	await page.getByRole('textbox', { name: 'Email or Username' }).fill(email);
	await page.getByRole('button', { name: 'Continue' }).click();
	await page.getByRole('textbox', { name: 'Password' }).fill(password);
	await page.getByRole('button', { name: 'Continue' }).last().click();
}

test('register and log in through the UI', async ({ page }) => {
	const username = `ui${Date.now().toString(36)}`;
	const email = `${username}@example.com`;
	await page.goto('/account/register');
	await page.getByRole('textbox', { name: 'E-mail address' }).fill(email);
	await page.getByRole('textbox', { name: 'Username' }).fill(username);
	await page.getByRole('textbox', { name: 'Password', exact: true }).fill(PASSWORD);
	await page.getByRole('textbox', { name: 'Repeat password' }).fill(PASSWORD);
	await page.getByRole('checkbox', { name: /Privacy policy/ }).check();
	await page.getByRole('checkbox', { name: /Terms of Service/ }).check();
	await page.getByRole('button', { name: 'Register' }).click();
	// It stays on the page and reports in place; with verification skipped, it is ready.
	await expect(page.getByRole('status')).toBeVisible();
	await expect(page.getByRole('status')).not.toHaveClass(/destructive/);
	await expectNoHorizontalOverflow(page);

	await page.getByRole('link', { name: 'Log in' }).last().click();
	await logInThroughUI(page, email, PASSWORD);
	await expect(page).toHaveURL(/\/my-quizzes/);
	await expectNoHorizontalOverflow(page);
});

test('a wrong password is refused and the page says so', async ({ page, request }) => {
	const { email } = await registerUser(request);
	await page.goto('/account/login');
	await logInThroughUI(page, email, 'not-the-password');
	await expect(page).toHaveURL(/\/account\/login/);
	await expect(page.getByText("That email address and password don't match.")).toBeVisible();
});

test("a signed-in user's quiz is on their My Quizzes, and nobody else's", async ({
	browser,
	request
}) => {
	const owner = await signedInContext(browser, request);
	const title = `Owned ${Date.now()}`;
	const saved = await saveQuiz(owner.context.request, quiz(title));
	expect(saved.status).toBe(200);
	expect(saved.secret, 'a signed-in save gets no anonymous secret').toBeFalsy();
	await owner.page.goto('/my-quizzes');
	await expect(owner.page.getByText(title)).toBeVisible();

	const other = await signedInContext(browser, request);
	await other.page.goto('/my-quizzes');
	await expect(other.page.getByRole('heading').first()).toBeVisible();
	await expect(other.page.getByText(title)).toHaveCount(0);
	// A private quiz is not startable by someone else either.
	const res = await other.context.request.post(
		`/api/v1/quiz/start/${saved.body.id}?game_mode=kahoot`
	);
	expect(res.status()).toBe(404);
	await owner.context.close();
	await other.context.close();
});

test('a signed-in owner can reopen a quiz in the editor and save a change', async ({
	browser,
	request
}) => {
	const owner = await signedInContext(browser, request);
	const saved = await saveQuiz(owner.context.request, quiz(`Editable ${Date.now()}`));
	await owner.page.goto(`/edit?quiz_id=${saved.body.id}`);
	await owner.page
		.getByRole('textbox', { name: 'Description' })
		.first()
		.fill('Changed by owner', { timeout: 20_000 });
	await owner.page.getByRole('button', { name: 'Save' }).click();
	// Every save lands on the quiz's view page, new or existing.
	await owner.page.waitForURL(new RegExp(`/view/${saved.body.id}`));
	const stored = await (
		await owner.context.request.get(`/api/v1/quiz/get/${saved.body.id}`)
	).json();
	expect(stored.description).toBe('Changed by owner');
	await owner.context.close();
});

test('an anonymous quiz can be claimed after signing up', async ({ browser, request }) => {
	const title = `Claim me ${Date.now()}`;
	const saved = await saveQuiz(request, quiz(title));
	const user = await signedInContext(browser, request);
	await rememberAnonQuiz(user.page, saved.body.id, saved.secret!);
	await user.page.goto(`/view/${saved.body.id}`);
	// The notice is a collapsed banner; its actions live inside it.
	await user.page.getByRole('button', { name: /isn't saved to an account/ }).click();
	await user.page.getByRole('button', { name: 'Claim this quiz to your account' }).click();
	await expect(user.page.getByText("This quiz isn't saved to an account")).toHaveCount(0);
	await user.page.goto('/my-quizzes');
	await expect(user.page.getByText(title)).toBeVisible();

	// Claimed means the secret is spent: it no longer starts or deletes anything.
	const anon = await request.post(`/api/v1/quiz/start/${saved.body.id}?game_mode=kahoot`, {
		headers: { 'X-Anon-Secret': saved.secret! }
	});
	expect(anon.status()).toBe(404);
	const again = await user.context.request.post(`/api/v1/quiz/claim/${saved.body.id}`, {
		headers: { 'X-Anon-Secret': saved.secret! }
	});
	expect(again.status(), 'claiming twice').toBe(404);
	await user.context.close();
});

test('a public quiz shows up in Explore search; a private one does not', async ({
	browser,
	request
}) => {
	const owner = await signedInContext(browser, request);
	const tag = `zebrafrog${Date.now().toString(36)}`;
	expect(
		(await saveQuiz(owner.context.request, quiz(`Public ${tag}`, { public: true }))).status
	).toBe(200);
	expect((await saveQuiz(owner.context.request, quiz(`Private ${tag}`))).status).toBe(200);
	const page = await browser.newPage();
	await expect
		.poll(
			async () => {
				await page.goto(`/explore?q=${tag}`);
				return page.getByText(`Public ${tag}`).count();
			},
			{ timeout: 20_000 }
		)
		.toBeGreaterThan(0);
	await expect(page.getByText(`Private ${tag}`)).toHaveCount(0);
	await expectNoHorizontalOverflow(page);
	await owner.context.close();
	await page.close();
});

test('a signed-in host can save results and find them on the results page', async ({
	browser,
	request
}) => {
	const owner = await signedInContext(browser, request);
	const title = `Results ${Date.now()}`;
	const { host, pin } = await hostGame(owner.context.request, quiz(title));
	const [p] = await joinAll(pin, ['scorer']);
	host.emit('start_game', {});
	await showQuestion(host, 0);
	p.emit('submit_answer', { question_index: 0, answer: 'Lisbon' });
	await new Promise((r) => setTimeout(r, 300));
	await finalResults(host);
	const saved = next(host, 'results_saved_successfully', 5000);
	host.emit('save_quiz');
	expect(await saved).not.toBeNull();

	await owner.page.goto('/results');
	await expect(owner.page.getByText(title)).toBeVisible();
	await expectNoHorizontalOverflow(owner.page);
	await owner.context.close();
});

test.describe('regressions', () => {
	test('signing up from "keep this quiz" brings you back to the quiz', async ({
		page,
		request
	}) => {
		const saved = await saveQuiz(request, quiz(`Return ${Date.now()}`));
		await rememberAnonQuiz(page, saved.body.id, saved.secret!);
		await page.goto(`/view/${saved.body.id}`);
		await page.getByRole('button', { name: /isn't saved to an account/ }).click();
		await page.getByRole('link', { name: 'Create an account to keep this quiz' }).click();
		await expect(page).toHaveURL(/returnTo=/);
		const username = `rt${Date.now().toString(36)}`;
		await page.getByRole('textbox', { name: 'E-mail address' }).fill(`${username}@example.com`);
		await page.getByRole('textbox', { name: 'Username' }).fill(username);
		await page.getByRole('textbox', { name: 'Password', exact: true }).fill(PASSWORD);
		await page.getByRole('textbox', { name: 'Repeat password' }).fill(PASSWORD);
		await page.getByRole('checkbox', { name: /Privacy policy/ }).check();
		await page.getByRole('checkbox', { name: /Terms of Service/ }).check();
		await page.getByRole('button', { name: 'Register' }).click();
		await expect(page.getByRole('status')).toBeVisible();
		await page.getByRole('link', { name: 'Log in' }).last().click();
		await logInThroughUI(page, `${username}@example.com`, PASSWORD);
		await expect(page).toHaveURL(new RegExp(`/view/${saved.body.id}`));
	});

	test('signing in does not lock you out of a quiz you made anonymously', async ({
		browser,
		request
	}) => {
		const saved = await saveQuiz(request, quiz(`Mine ${Date.now()}`));
		const user = await registerUser(request);
		const ctx = await browser.newContext();
		await apiLogin(ctx.request, user.email);
		const headers = { 'X-Anon-Secret': saved.secret! };
		const start = await ctx.request.post(
			`/api/v1/quiz/start/${saved.body.id}?game_mode=kahoot`,
			{ headers }
		);
		const del = await ctx.request.delete(`/api/v1/quiz/delete/${saved.body.id}`, { headers });
		test.info().annotations.push({
			type: 'status',
			description: `start ${start.status()}, delete ${del.status()}`
		});
		expect(start.status()).toBe(200);
		expect(del.status()).toBeLessThan(300);
		await ctx.close();
	});
});
