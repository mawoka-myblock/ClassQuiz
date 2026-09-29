// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// A draft is a quiz with an unfinished question (or none at all) -- there is no draft
// column, it is computed client-side from `isQuestionComplete` (view page,
// $lib/editor/question_complete) and enforced server-side by
// frogquiz/helpers/completeness.py on POST /api/v1/quiz/start/{id}.

import { expect, test } from '@playwright/test';
import { expectNoHorizontalOverflow, mc, PHONE, rememberAnonQuiz, saveQuiz } from './helpers';

const draftQuiz = (title: string) => ({
	title,
	description: 'e2e draft',
	public: true,
	questions: [
		{
			question: 'Unfinished question',
			time: '20',
			type: 'ABCD' as const,
			// No answer is marked right: this is exactly what makes it a draft.
			answers: [
				{ answer: 'Paris', right: false },
				{ answer: 'Lyon', right: false }
			]
		}
	]
});

const completeQuiz = (title: string) => ({
	title,
	description: 'e2e complete',
	public: true,
	questions: [
		mc('Capital of France?', [
			['Paris', true],
			['Lyon', false]
		])
	]
});

test('a draft quiz shows the Draft badge and a disabled Play on the view page', async ({
	page,
	request
}) => {
	const title = `Draft view ${Date.now()}`;
	const saved = await saveQuiz(request, draftQuiz(title));
	expect(saved.status).toBe(200);
	const id = saved.body.id;

	await page.setViewportSize(PHONE);
	await page.goto(`/view/${id}`);
	await expect(page.getByRole('heading', { name: title })).toBeVisible();
	await expect(page.getByText('Draft', { exact: true })).toBeVisible();

	const play = page.getByRole('button', { name: 'Play', exact: true });
	await expect(play).toBeDisabled();
	await expectNoHorizontalOverflow(page);
});

test('a complete quiz shows no Draft badge', async ({ page, request }) => {
	const title = `Complete view ${Date.now()}`;
	const saved = await saveQuiz(request, completeQuiz(title));
	expect(saved.status).toBe(200);
	const id = saved.body.id;

	await page.goto(`/view/${id}`);
	await expect(page.getByRole('heading', { name: title })).toBeVisible();
	await expect(page.getByText('Draft', { exact: true })).toHaveCount(0);
});

test('a draft quiz shows Draft and a disabled Play on My Quizzes', async ({ page, request }) => {
	const title = `Draft my-quizzes ${Date.now()}`;
	const saved = await saveQuiz(request, draftQuiz(title));
	expect(saved.status).toBe(200);
	const id = saved.body.id;
	expect(saved.secret).toBeTruthy();

	await rememberAnonQuiz(page, id, saved.secret!);
	await page.setViewportSize(PHONE);
	await page.goto('/my-quizzes');

	const row = page.getByRole('listitem').filter({ hasText: title });
	await expect(row).toBeVisible();
	await expect(row.getByText('Draft', { exact: true })).toBeVisible();
	await expect(row.getByRole('button', { name: 'Play', exact: true })).toBeDisabled();
	await expectNoHorizontalOverflow(page);
});

test('the server refuses to start a draft quiz', async ({ request }) => {
	const saved = await saveQuiz(request, draftQuiz(`Draft start ${Date.now()}`));
	expect(saved.status).toBe(200);
	const id = saved.body.id;

	const res = await request.post(`/api/v1/quiz/start/${id}?game_mode=kahoot`, {
		headers: { 'X-Anon-Secret': saved.secret! }
	});
	// If this is 200 instead, the completeness check in
	// frogquiz/helpers/completeness.py / the quiz/start route isn't live in this run
	// (e.g. the API process hasn't been restarted since that backend change landed).
	expect(res.status(), await res.text()).toBe(400);
	const body = await res.json();
	expect(body.detail).toContain('draft');
});
