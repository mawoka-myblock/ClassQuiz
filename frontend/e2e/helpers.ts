// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { expect, type APIRequestContext, type Browser, type Page } from '@playwright/test';

export const ANON_KEY = 'frogquiz_anon_secrets';
export const PHONE = { width: 390, height: 844 };

export type Answer = { answer: string; right: boolean };
export type Question = {
	question: string;
	time: string;
	type?: 'ABCD' | 'CHECK';
	answers: Answer[] | unknown;
};
export type QuizInput = {
	title: string;
	description: string;
	public?: boolean;
	questions: Question[];
};

export const mc = (question: string, answers: [string, boolean][], time = '20'): Question => ({
	question,
	time,
	type: 'ABCD',
	answers: answers.map(([answer, right]) => ({ answer, right }))
});

/** Saves a quiz through the same two calls the editor makes. Anonymous unless a token is given. */
export async function saveQuiz(request: APIRequestContext, quiz: QuizInput, bearer?: string) {
	const headers: Record<string, string> = bearer ? { Authorization: `Bearer ${bearer}` } : {};
	const start = await request.post('/api/v1/editor/start?edit=false', { headers });
	expect(start.status(), await start.text()).toBe(200);
	const { token } = await start.json();
	const res = await request.post(`/api/v1/editor/finish?edit_id=${token}`, {
		headers,
		data: { public: false, ...quiz }
	});
	const body = res.status() === 200 ? await res.json() : await res.text();
	return {
		status: res.status(),
		body,
		secret: res.headers()['x-anon-secret'] as string | undefined
	};
}

export async function rememberAnonQuiz(page: Page, id: string, secret: string) {
	await page.goto('/');
	await page.evaluate(
		([key, quizId, s]) => {
			const all = JSON.parse(localStorage.getItem(key) ?? '{}');
			all[quizId] = s;
			localStorage.setItem(key, JSON.stringify(all));
		},
		[ANON_KEY, id, secret]
	);
}

/** From the quiz view page, through the start modal, into the host lobby. Returns the PIN. */
export async function hostFromViewPage(
	page: Page,
	quizId: string,
	opts: { showOnDevices?: boolean } = {}
): Promise<string> {
	await page.goto(`/view/${quizId}`);
	await page.getByRole('button', { name: 'Play', exact: true }).click();
	const dialog = page.getByRole('dialog', { name: 'Start Game' });
	await expect(dialog).toBeVisible();
	if (opts.showOnDevices) {
		// Kahoot's "Show questions & answers on participants' devices" (MVP.md D16). Off
		// by default, so a test that wants it has to say so.
		const toggle = dialog.getByRole('switch', {
			name: "Show questions and answers on players' devices"
		});
		await expect(toggle).toHaveAttribute('aria-checked', 'false');
		await toggle.click();
		await expect(toggle).toHaveAttribute('aria-checked', 'true');
	}
	await dialog.getByRole('button', { name: 'Start Game' }).click();
	await page.waitForURL(/\/admin\?/);
	const pin = new URL(page.url()).searchParams.get('pin');
	expect(pin).toMatch(/^\d{6}$/);
	return pin!;
}

/**
 * The PIN box is server-rendered and autofocused, so it accepts input before the page
 * hydrates -- and anything entered then is lost. /play logs "Connected!" once its
 * socket is up, which is after hydration.
 */
export async function gotoPlayHydrated(page: Page) {
	const connected = page.waitForEvent('console', {
		predicate: (m) => m.text() === 'Connected!',
		timeout: 15_000
	});
	await page.goto('/play');
	await connected;
}

export async function joinAsPlayer(browser: Browser, pin: string, username: string) {
	const context = await browser.newContext({ viewport: PHONE });
	const page = await context.newPage();
	await gotoPlayHydrated(page);
	// The PIN form has no submit handler: the sixth digit advances it on its own.
	await page.getByRole('textbox', { name: 'Game PIN' }).fill(pin);
	await page.getByRole('textbox', { name: 'Username' }).fill(username);
	await page.getByRole('button', { name: 'Submit' }).click();
	return { context, page };
}

/** Horizontal overflow is a recurring bug here (w-screen); assert it wherever a page is visited. */
export async function expectNoHorizontalOverflow(page: Page) {
	const overflow = await page.evaluate(
		() => document.documentElement.scrollWidth - document.documentElement.clientWidth
	);
	expect(overflow, 'page scrolls horizontally').toBeLessThanOrEqual(0);
}

/**
 * Clears the host's standings step, if it is showing.
 *
 * A round is three host steps, not two: the answers, then the standings, then move on
 * (`show_scoreboard_step` in `lib/play/admin/controls.svelte`, added to match how Kahoot
 * sequences a round). It sits before "Next Question" *and* before "Get final results",
 * so every spec that drives a host through a results screen has to pass it. Specs
 * written before that step hung on a screen offering "Scoreboard".
 *
 * Conditional rather than assumed: a slide, a hide-results question and a question
 * whose results have not arrived yet have no standings moment.
 */
export async function clearScoreboardStep(page: Page) {
	const scoreboard = page.getByRole('button', { name: 'Scoreboard' });
	if (await scoreboard.isVisible().catch(() => false)) {
		await scoreboard.click();
	}
}

/** Standings, then the next question. */
export async function advancePastResults(page: Page) {
	await clearScoreboardStep(page);
	await page.getByRole('button', { name: /Next Question/ }).click();
}

/** Standings, then the podium. */
export async function advanceToFinalResults(page: Page) {
	await clearScoreboardStep(page);
	await page.getByRole('button', { name: /final results/i }).click();
}

// ---- Driving the editor ----------------------------------------------------
// Lifted out of editor.e2e.ts on 2026-10-02 so the journey specs build a quiz the way a
// person does, through the editor, rather than posting one to the API.

export const titleBox = (page: Page) => page.getByRole('textbox', { name: 'Quiz title' });
export const questionBox = (page: Page) => page.getByRole('textbox', { name: 'Question text' });
export const saveQuizButton = (page: Page) => page.getByRole('button', { name: 'Save' });
export const cards = (page: Page) => page.locator('[data-question-card]');

export async function addQuestion(
	page: Page,
	kind: RegExp,
	title: string,
	answers: [string, boolean][]
) {
	await page
		.getByRole('button', { name: /Add new question|Add your first question/ })
		.first()
		.click();
	await page.getByRole('button', { name: kind }).click();
	// Only the open card holds a rich-text field; the others are collapsed to plain text.
	await questionBox(page).fill(title);
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

export async function startNewQuiz(page: Page, title: string) {
	await page.goto('/create');
	await titleBox(page).fill(title);
	await page.getByRole('textbox', { name: 'Description' }).fill('Made in the editor');
}
