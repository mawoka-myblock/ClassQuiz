// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Practice was rebuilt (MVP.md D3): the old screens threw on the first answer click, so
// there was no working practice at all. Download is Excel only (D5).

import { expect, test } from '@playwright/test';
import { signedInContext } from './accounts';
import { expectNoHorizontalOverflow, mc, PHONE, saveQuiz } from './helpers';

const quiz = (title: string) => ({
	title,
	description: 'e2e',
	public: true,
	questions: [
		mc('<p>Capital of <b>France</b>?</p>', [
			['Paris', true],
			['Lyon', false]
		]),
		{
			question: 'Pick the frogs',
			time: '20',
			type: 'CHECK' as const,
			answers: [
				{ answer: 'Bullfrog', right: true },
				{ answer: 'Newt', right: false },
				{ answer: 'Tree frog', right: true }
			]
		},
		mc('Last one', [
			['Right', true],
			['Wrong', false]
		])
	]
});

test('practice runs a quiz end to end and scores it like the game', async ({ page, request }) => {
	const title = `Practice ${Date.now()}`;
	const saved = await saveQuiz(request, quiz(title));
	expect(saved.status).toBe(200);
	const id = saved.body.id;

	await page.setViewportSize(PHONE);
	await page.goto(`/view/${id}`);
	await page.getByRole('link', { name: 'Practice' }).click();
	await expect(page).toHaveURL(new RegExp(`/practice\\?quiz_id=${id}`));
	await expect(page.getByRole('heading', { name: title })).toBeVisible();
	await expect(page.getByText('3 questions.')).toBeVisible();
	await expectNoHorizontalOverflow(page);

	await page.getByRole('button', { name: 'Start practising' }).click();

	// ABCD: one click reveals. The title is rendered, not shown as raw HTML.
	await expect(page.getByRole('heading', { name: 'Capital of France?' })).toBeVisible();
	await page.getByRole('button', { name: 'Paris' }).click();
	await expect(page.getByRole('status')).toHaveText('Right!');
	await expect(page.getByText('1 of 1 right')).toBeVisible();
	await page.getByRole('button', { name: 'Next' }).click();

	// CHECK: toggles, then submit. Missing one right answer is wrong.
	const submit = page.getByRole('button', { name: 'Submit' });
	await expect(submit).toBeDisabled();
	await page.getByRole('button', { name: 'Bullfrog' }).click();
	await expect(page.getByRole('button', { name: 'Bullfrog' })).toHaveAttribute(
		'aria-pressed',
		'true'
	);
	await submit.click();
	await expect(page.getByRole('status')).toHaveText('Not quite');
	await expect(page.getByText('1 of 2 right')).toBeVisible();
	await expectNoHorizontalOverflow(page);
	await page.getByRole('button', { name: 'Next' }).click();

	await page.getByRole('button', { name: 'Right' }).click();
	await page.getByRole('button', { name: 'See my score' }).click();
	await expect(page.getByText('2 / 3')).toBeVisible();

	await page.getByRole('button', { name: 'Practice again' }).click();
	await expect(page.getByRole('heading', { name: 'Capital of France?' })).toBeVisible();
	await page.getByRole('link', { name: 'Back to quiz' }).click();
	await expect(page).toHaveURL(new RegExp(`/view/${id}$`));
});

test('practice on a missing quiz says so and offers a way out', async ({ page }) => {
	await page.goto('/practice?quiz_id=00000000-0000-0000-0000-000000000000');
	await expect(page.getByText("This quiz couldn't be opened.")).toBeVisible();
	await expect(page.getByRole('link', { name: 'Discover' }).last()).toBeVisible();
});

test('Download offers the Excel file and fetches a real spreadsheet', async ({
	browser,
	request
}) => {
	const { context, page } = await signedInContext(browser, request);
	const title = `Sheet ${Date.now()}`;
	// Saved through the signed-in context, so this user owns it. Download is owner-only
	// (MVP.md D18); saving through the bare `request` fixture makes an anonymous quiz,
	// which is what this test used to do.
	const saved = await saveQuiz(context.request, quiz(title));
	await page.goto(`/view/${saved.body.id}`);

	// Download is server-rendered enabled for a signed-in visitor, so a click that lands
	// before hydration is lost. Retry until the dialog opens.
	const dialog = page.getByRole('dialog');
	await expect(async () => {
		await page.getByRole('button', { name: 'Download' }).click();
		await expect(dialog.getByRole('heading', { name: 'Download this quiz' })).toBeVisible({
			timeout: 1000
		});
	}).toPass();

	const [download] = await Promise.all([
		page.waitForEvent('download'),
		dialog.getByRole('link', { name: 'Download .xlsx' }).click()
	]);
	expect(download.suggestedFilename()).toBe(`frogQuiz-${title}.xlsx`);
	await expect(dialog).toBeHidden();

	const res = await context.request.get(`/api/v1/eximport/excel/${saved.body.id}`);
	expect(res.headers()['content-type']).toContain('spreadsheetml');
	// An .xlsx is a zip archive.
	expect((await res.body()).subarray(0, 2).toString()).toBe('PK');
	await context.close();
});

test("Download is not offered on, or reachable for, somebody else's quiz", async ({
	browser,
	request
}) => {
	// The sheet carries the answer key, so a teammate who is about to play your quiz must
	// not be able to read the answers out of it (MVP.md D18). It was any signed-in user
	// until 2026-10-02, and the page offered the button to them.
	const owner = await signedInContext(browser, request);
	const title = `Not yours ${Date.now()}`;
	const saved = await saveQuiz(owner.context.request, { ...quiz(title), public: true });
	expect(saved.status).toBe(200);

	const other = await signedInContext(browser, request);
	await other.page.goto(`/view/${saved.body.id}`);
	// Public, so the page itself opens and offers Play. Download is simply absent.
	await expect(other.page.getByRole('button', { name: 'Play' })).toBeVisible();
	await expect(other.page.getByRole('button', { name: 'Download' })).toHaveCount(0);

	// And the endpoint behind it refuses, so hiding the button is not the only guard.
	const res = await other.context.request.get(`/api/v1/eximport/excel/${saved.body.id}`);
	expect(res.status()).toBe(404);

	await owner.context.close();
	await other.context.close();
});
