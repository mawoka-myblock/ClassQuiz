// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Building a quiz by hand in the editor, the way somebody without an account would,
// then checking what actually reached the server and that it plays.

import { expect, test, type Page } from '@playwright/test';
import { ANON_KEY, PHONE, expectNoHorizontalOverflow } from './helpers';
import { closeAll, connect, finalResults, joinAll, next, showQuestion } from './sockets';

test.afterEach(closeAll);

const titleBox = (page: Page) => page.getByRole('textbox', { name: /Rich Text Editor/ });
const saveButton = (page: Page) => page.getByRole('button', { name: 'Save' });

async function addQuestion(page: Page, kind: RegExp, title: string, answers: [string, boolean][]) {
	await page.getByRole('button', { name: 'Add new question' }).first().click();
	await page.getByRole('button', { name: kind }).click();
	await titleBox(page).fill(title);
	for (let i = 0; i < answers.length; i++)
		await page.getByRole('button', { name: 'Add an answer' }).click();
	const inputs = page.getByRole('textbox', { name: 'Enter an answer' });
	for (const [i, [text, right]] of answers.entries()) {
		await inputs.nth(i).fill(text);
		if (right)
			await page
				.getByRole('button', { name: `Mark as correct: ${text}`, exact: true })
				.click();
	}
}

async function startNewQuiz(page: Page, title: string) {
	await page.goto('/create');
	await titleBox(page).fill(title);
	await page.getByRole('textbox', { name: 'Description' }).fill('Made in the editor');
}

async function anonSecret(page: Page, id: string) {
	return page.evaluate(
		([k, i]) => JSON.parse(localStorage.getItem(k) ?? '{}')[i],
		[ANON_KEY, id]
	);
}

test('build a quiz by hand, save it, and play it', async ({ page, request }) => {
	const title = `Handmade ${Date.now()}`;
	await startNewQuiz(page, title);
	await addQuestion(page, /^Multiple-Choice/, 'Which is a frog?', [
		['Tree frog', true],
		['Gecko', false],
		['Newt', false]
	]);
	await addQuestion(page, /^Check Choice/, 'Which are amphibians?', [
		['Frog', true],
		['Lizard', false],
		['Salamander', true]
	]);
	await expect(page.getByText('2 questions').first()).toBeVisible();
	await saveButton(page).click();
	await page.waitForURL(/\/view\//);
	const id = page.url().split('/view/')[1];
	await expect(page.getByText("This quiz isn't saved to an account")).toBeVisible();
	const secret = await anonSecret(page, id);
	expect(secret, 'the editor remembered the anonymous secret').toBeTruthy();

	// What reached the server is what was typed.
	const stored = await (await request.get(`/api/v1/quiz/get/public/${id}`)).json();
	test.info().annotations.push({
		type: 'stored',
		description: JSON.stringify(stored.questions).slice(0, 400)
	});
	expect(stored.questions.map((q: { type: string }) => q.type)).toEqual(['ABCD', 'CHECK']);
	expect(
		stored.questions[0].answers
			.filter((a: { right: boolean }) => a.right)
			.map((a: { answer: string }) => a.answer)
	).toEqual(['Tree frog']);

	// And it plays: the multiple-answer question scores the exact set, and nothing else.
	const start = await request.post(
		`/api/v1/quiz/start/${id}?game_mode=kahoot&captcha_enabled=False`,
		{
			headers: { 'X-Anon-Secret': secret }
		}
	);
	expect(start.status()).toBe(200);
	const { game_pin, game_id } = await start.json();
	const host = await connect();
	const registered = next(host, 'registered_as_admin');
	host.emit('register_as_admin', { game_pin, game_id });
	expect(await registered).not.toBeNull();
	const [right, partial] = await joinAll(String(game_pin), ['exactset', 'halfset']);
	host.emit('start_game', {});
	await showQuestion(host, 0);
	// Spaced out on purpose: simultaneous answers hit the lost-update race that
	// live-socket.e2e.ts records, and this test is about scoring, not that.
	right.emit('submit_answer', { question_index: 0, answer: 'Tree frog' });
	await new Promise((r) => setTimeout(r, 200));
	partial.emit('submit_answer', { question_index: 0, answer: 'Gecko' });
	await new Promise((r) => setTimeout(r, 300));
	await showQuestion(host, 1);
	right.emit('submit_answer', { question_index: 1, answer: '02' });
	await new Promise((r) => setTimeout(r, 200));
	partial.emit('submit_answer', { question_index: 1, answer: '0' });
	await new Promise((r) => setTimeout(r, 300));
	const results = await finalResults(host);
	const row = (q: string, u: string) => results[q].find((r) => r.username === u)!;
	expect(row('0', 'exactset').right).toBe(true);
	expect(row('0', 'halfset').right).toBe(false);
	expect(row('1', 'exactset').right).toBe(true);
	expect(row('1', 'halfset').right).toBe(false);
});

// MVP.md D14: nothing is marked missing until the first Save, an unfinished quiz is kept
// as a draft rather than refused, and the editor saves on its own.
test('nothing is marked red before Save, and Save with no questions says what is needed', async ({
	page
}) => {
	await startNewQuiz(page, `Guard ${Date.now()}`);
	await addQuestion(page, /^Multiple-Choice/, '', [
		['', false],
		['', false]
	]);
	await expect(page.getByText('Incomplete')).toHaveCount(0);
	await expect(page.locator('.ring-destructive')).toHaveCount(0);

	await page.goto('/create');
	await titleBox(page).fill(`Empty ${Date.now()}`);
	await saveButton(page).click();
	await expect(
		page.getByText('Give the quiz a title and at least one question to save it')
	).toBeVisible();
	await expect(page).toHaveURL(/\/create$/);
});

test('an unfinished quiz saves as a draft, and Save shows what is left', async ({
	page,
	request
}) => {
	await startNewQuiz(page, `Draft ${Date.now()}`);
	await addQuestion(page, /^Multiple-Choice/, 'No right answer yet', [
		['One', false],
		['Two', false]
	]);
	await saveButton(page).click();
	await expect(
		page.getByText('Saved as a draft. 1 question needs finishing before it can be played')
	).toBeVisible();
	await expect(page.getByText('Incomplete').first()).toBeAttached();
	// It stayed in the editor, which now edits the stored quiz.
	await expect(page).toHaveURL(/\/edit\?quiz_id=/);
	const id = new URL(page.url()).searchParams.get('quiz_id')!;
	const secret = await anonSecret(page, id);
	const start = await request.post(`/api/v1/quiz/start/${id}?game_mode=kahoot`, {
		headers: { 'X-Anon-Secret': secret }
	});
	expect(start.status(), 'the server will not start a draft').toBe(400);

	// Finishing it clears the message, and Save then goes to the quiz.
	await page.getByRole('button', { name: 'Mark as correct: Two', exact: true }).click();
	await expect(page.getByText(/Saved as a draft/)).toHaveCount(0);
	await saveButton(page).click();
	await page.waitForURL(new RegExp(`/view/${id}$`));
});

test('the editor saves on its own, and a reload reopens the saved quiz', async ({
	page,
	request
}) => {
	const title = `Autosaved ${Date.now()}`;
	await startNewQuiz(page, title);
	await addQuestion(page, /^Multiple-Choice/, 'Kept without Save', [
		['A', true],
		['B', false]
	]);
	await expect(page).toHaveURL(/\/edit\?quiz_id=/, { timeout: 15_000 });
	await expect(page.getByText('Saved', { exact: true })).toBeVisible();
	const id = new URL(page.url()).searchParams.get('quiz_id')!;
	const stored = await (await request.get(`/api/v1/quiz/get/public/${id}`)).json();
	expect(stored.title).toContain('Autosaved');
	expect(stored.questions[0].answers.map((a: { answer: string }) => a.answer)).toEqual([
		'A',
		'B'
	]);

	await page.reload();
	await expect(titleBox(page).first()).toContainText('Autosaved', { timeout: 20_000 });

	// A later edit is saved too: an update, not a second quiz.
	await page.getByRole('textbox', { name: 'Description' }).first().fill('Changed later');
	await expect
		.poll(
			async () =>
				(await (await request.get(`/api/v1/quiz/get/public/${id}`)).json()).description,
			{
				timeout: 15_000
			}
		)
		.toBe('Changed later');
});

test('the timer field cannot produce a timer the game cannot run', async ({ page, request }) => {
	await startNewQuiz(page, `Timer ${Date.now()}`);
	await addQuestion(page, /^Multiple-Choice/, 'Timed', [
		['A', true],
		['B', false]
	]);
	const timer = page.getByRole('spinbutton', { name: /Time in seconds/ });
	for (const bad of ['0', '-5']) {
		await timer.fill(bad);
		await saveButton(page).click();
		// Save is always pressable now (D14); an unusable timer keeps the quiz a draft, and
		// the server refuses to store one.
		await page.waitForTimeout(1000);
		expect(page.url()).not.toMatch(/\/view\//);
		const id = new URL(page.url()).searchParams.get('quiz_id');
		if (id) {
			const stored = await (await request.get(`/api/v1/quiz/get/public/${id}`)).json();
			test.info().annotations.push({
				type: `timer ${bad} stored as`,
				description: stored.questions[0].time
			});
			expect(Number(stored.questions[0].time), `timer "${bad}" was saved`).toBeGreaterThan(0);
		}
	}
});

test('an existing anonymous quiz can be reopened, edited and saved', async ({ page, request }) => {
	await startNewQuiz(page, `Before ${Date.now()}`);
	await addQuestion(page, /^Multiple-Choice/, 'Q', [
		['A', true],
		['B', false]
	]);
	await saveButton(page).click();
	await page.waitForURL(/\/view\//);
	const id = page.url().split('/view/')[1];

	await page.goto(`/edit?quiz_id=${id}`);
	await expect(titleBox(page).first()).toContainText('Before', { timeout: 20_000 });
	await page.getByRole('textbox', { name: 'Description' }).first().fill('Edited description');
	await saveButton(page).click();
	await page.waitForURL(/\/view\//);
	const stored = await (await request.get(`/api/v1/quiz/get/public/${id}`)).json();
	expect(stored.description).toBe('Edited description');
});

test('the editor fits a phone', async ({ browser }) => {
	const ctx = await browser.newContext({ viewport: PHONE });
	const page = await ctx.newPage();
	await startNewQuiz(page, `Phone ${Date.now()}`);
	await expectNoHorizontalOverflow(page);
	await ctx.close();
});

test.describe('regressions', () => {
	test('a question with no correct answer cannot reach the view page', async ({ page }) => {
		await startNewQuiz(page, `No right ${Date.now()}`);
		await addQuestion(page, /^Multiple-Choice/, 'No right answer', [
			['One', false],
			['Two', false]
		]);
		await saveButton(page).click();
		// It is kept as a draft and says why, rather than saving an unplayable quiz silently.
		await expect(page.getByText(/1 question needs finishing/)).toBeVisible();
		expect(page.url()).not.toMatch(/\/view\//);
	});

	test("the editor's Back link does not send an anonymous user to a login wall", async ({
		page
	}) => {
		await startNewQuiz(page, `Back ${Date.now()}`);
		page.on('dialog', (d) => d.accept());
		await page.getByRole('link', { name: 'Back' }).click();
		await page.waitForURL((u) => !u.pathname.startsWith('/create'), { timeout: 15_000 });
		test.info().annotations.push({ type: 'landed on', description: page.url() });
		expect(page.url()).not.toMatch(/\/account\/login/);
	});
});
