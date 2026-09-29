// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Edge cases sent straight to the API, skipping the editor's own checks -- the server is
// the only thing a crafted client has to get past. No browser needed.

import { expect, test, type APIRequestContext } from '@playwright/test';
import { mc, saveQuiz, type Question } from './helpers';

const quizWith = (questions: Question[], extra: Record<string, unknown> = {}) => ({
	title: 'Edge',
	description: 'edge',
	questions,
	...extra
});

const start = (request: APIRequestContext, id: string, secret?: string) =>
	request.post(`/api/v1/quiz/start/${id}?game_mode=kahoot&captcha_enabled=False`, {
		headers: secret ? { 'X-Anon-Secret': secret } : {}
	});

const note = (key: string, value: unknown) =>
	test.info().annotations.push({ type: key, description: String(value) });

// Known bugs are written as the behaviour we want, wrapped in test.fail: the run stays
// green while they exist, and turns red ("expected to fail but passed") once one is fixed,
// which is the prompt to delete the test.fail line.

test.describe('malformed questions', () => {
	test('an ABCD question with no answers is rejected, not a 500', async ({ request }) => {
		const res = await saveQuiz(
			request,
			quizWith([{ question: 'q', time: '20', type: 'ABCD', answers: [] }])
		);
		note('status', res.status);
		expect(res.status, String(res.body).slice(0, 300)).not.toBe(500);
		expect(res.status).toBeGreaterThanOrEqual(400);
	});

	test('a CHECK question with no answers is rejected, not a 500', async ({ request }) => {
		const res = await saveQuiz(
			request,
			quizWith([{ question: 'q', time: '20', type: 'CHECK', answers: [] }])
		);
		note('status', res.status);
		expect(res.status, String(res.body).slice(0, 300)).not.toBe(500);
		expect(res.status).toBeGreaterThanOrEqual(400);
	});

	// The editor stops at four, but a Kahoot import can carry six, so the server's cap is
	// ten: the most a CHECK answer's concatenated indices can express unambiguously.
	test('six answers save (Kahoot imports have them); eleven are rejected', async ({
		request
	}) => {
		const answers = (n: number) =>
			Array.from({ length: n }, (_, i) => [`a${i}`, i === 0] as [string, boolean]);
		const six = await saveQuiz(request, quizWith([mc('six', answers(6))]));
		expect(six.status).toBe(200);
		const eleven = await saveQuiz(request, quizWith([mc('eleven', answers(11))]));
		note('eleven status', eleven.status);
		expect(eleven.status).not.toBe(500);
		expect(eleven.status, 'eleven answers were accepted').toBeGreaterThanOrEqual(400);
	});

	for (const time of ['abc', '-5', '0', '99999', '']) {
		test(`timer "${time}" is rejected`, async ({ request }) => {
			const res = await saveQuiz(
				request,
				quizWith([
					mc(
						't',
						[
							['a', true],
							['b', false]
						],
						time
					)
				])
			);
			note('status', res.status);
			expect(res.status).not.toBe(500);
			expect(res.status, `timer "${time}" was accepted`).toBeGreaterThanOrEqual(400);
		});
	}

	// Both save. Since drafts (MVP.md D14) a question with no correct answer is unfinished,
	// so the quiz is a draft and will not start; every answer correct is still playable.
	test('no correct answer saves as a draft that will not start; every answer correct starts', async ({
		request
	}) => {
		const none_right = mc('none right', [
			['a', false],
			['b', false]
		]);
		const all_right = mc('all right', [
			['a', true],
			['b', true]
		]);
		const draft = await saveQuiz(request, quizWith([none_right, all_right]));
		expect(draft.status).toBe(200);
		const refused = await start(request, draft.body.id, draft.secret);
		expect(refused.status()).toBe(400);
		expect((await refused.json()).detail).toContain('question 1');

		const playable = await saveQuiz(request, quizWith([all_right]));
		expect(playable.status).toBe(200);
		expect((await start(request, playable.body.id, playable.secret)).status()).toBe(200);
	});
});

test.describe('size', () => {
	test('a quiz with no questions cannot be started', async ({ request }) => {
		const res = await saveQuiz(request, quizWith([]));
		note('save status', res.status);
		expect(res.status).not.toBe(500);
		if (res.status === 200) {
			const s = await start(request, res.body.id, res.secret);
			note('start status', s.status());
			expect(s.status(), 'an empty quiz started a live game').toBeGreaterThanOrEqual(400);
		}
	});

	for (const count of [200, 500]) {
		test(`a ${count}-question quiz saves, reads back whole and starts`, async ({ request }) => {
			test.setTimeout(120_000);
			const questions = Array.from({ length: count }, (_, i) =>
				mc(`Question ${i + 1}?`, [
					[`right ${i}`, true],
					[`wrong ${i}`, false],
					['maybe', false],
					['never', false]
				])
			);
			const t0 = Date.now();
			const res = await saveQuiz(request, quizWith(questions));
			note('save ms', Date.now() - t0);
			expect(res.status).toBe(200);
			const back = await request.get(`/api/v1/quiz/get/public/${res.body.id}`);
			expect(back.status()).toBe(200);
			expect((await back.json()).questions).toHaveLength(count);
			const t1 = Date.now();
			expect((await start(request, res.body.id, res.secret)).status()).toBe(200);
			note('start ms', Date.now() - t1);
		});
	}

	test('very long text is either capped or stored intact, never a 500', async ({ request }) => {
		const long = 'x'.repeat(5000);
		const noSpaces = 'Supercalifragilistic'.repeat(250);
		const res = await saveQuiz(request, {
			title: long,
			description: long,
			questions: [
				mc(noSpaces, [
					[long, true],
					['b', false]
				])
			]
		});
		note('status', res.status);
		expect(res.status).not.toBe(500);
		if (res.status === 200) {
			note('stored title length', res.body.title.length);
			note('stored question length', res.body.questions[0].question.length);
		}
	});
});

test.describe('anonymous ownership', () => {
	test('the right secret starts and deletes; a wrong one looks like "not found"', async ({
		request
	}) => {
		const res = await saveQuiz(
			request,
			quizWith([
				mc('q', [
					['a', true],
					['b', false]
				])
			])
		);
		expect(res.status).toBe(200);
		const id = res.body.id;
		const wrong = 'f'.repeat(64);

		expect((await start(request, id, wrong)).status()).toBe(404);
		expect((await start(request, id)).status()).toBe(404);
		const edit = await request.post(`/api/v1/editor/start?edit=true&quiz_id=${id}`, {
			headers: { 'X-Anon-Secret': wrong }
		});
		expect(edit.status()).toBe(404);
		const del = await request.delete(`/api/v1/quiz/delete/${id}`, {
			headers: { 'X-Anon-Secret': wrong }
		});
		expect(del.status()).toBe(404);
		const missing = await request.delete(
			`/api/v1/quiz/delete/00000000-0000-0000-0000-000000000000`,
			{
				headers: { 'X-Anon-Secret': wrong }
			}
		);
		expect(missing.status(), 'wrong secret and unknown quiz must be indistinguishable').toBe(
			del.status()
		);

		expect((await start(request, id, res.secret)).status()).toBe(200);
		const ok = await request.delete(`/api/v1/quiz/delete/${id}`, {
			headers: { 'X-Anon-Secret': res.secret! }
		});
		expect(ok.status()).toBeLessThan(300);
		expect((await request.get(`/api/v1/quiz/get/public/${id}`)).status()).toBe(404);
	});

	test('an anonymous quiz is never public, even if the request asks for it', async ({
		request
	}) => {
		const res = await saveQuiz(
			request,
			quizWith(
				[
					mc('q', [
						['a', true],
						['b', false]
					])
				],
				{ public: true }
			)
		);
		expect(res.status).toBe(200);
		expect(res.body.public).toBe(false);
	});

	test('the public quiz endpoint does not leak the ownership hash', async ({ request }) => {
		const res = await saveQuiz(
			request,
			quizWith([
				mc('q', [
					['a', true],
					['b', false]
				])
			])
		);
		const pub = await (await request.get(`/api/v1/quiz/get/public/${res.body.id}`)).json();
		expect(pub).not.toHaveProperty('anon_secret');
	});
});
