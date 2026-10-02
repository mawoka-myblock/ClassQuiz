// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// MVP.md D16: what a player sees on their own phone during a question.
//
// Kahoot's default puts the question and the answer text on the shared screen and gives
// the phone four coloured shapes, and it ships a free host-side setting -- "Show questions
// & answers on participants' devices" -- that moves them onto the phone as well. frogQuiz
// does the same, through `game_mode` ('kahoot' / 'normal'), which both render paths in
// `lib/play/question.svelte` have always honoured; until 2026-10-02 the start modal
// hardcoded 'kahoot' so the switch was unreachable.
//
// The assertions below are deliberately about VISIBLE text. The answer text is the
// button's `aria-label` in both modes, which is right for a screen reader and is how the
// other specs click answers by name -- so `getByRole('button', { name: 'Lisbon' })` finds
// the tile in shapes mode too and proves nothing here.

import { expect, test, type APIRequestContext, type Browser, type Page } from '@playwright/test';
import { hostFromViewPage, joinAsPlayer, mc, rememberAnonQuiz, saveQuiz } from './helpers';

const QUESTION = 'Capital of Portugal?';
const QUIZ = {
	title: 'Player screen',
	description: 'e2e',
	questions: [
		mc(QUESTION, [
			['Lisbon', true],
			['Porto', false]
		])
	]
};

/** Saves an anonymous quiz, hosts it, joins one player, and shows question 1. */
async function playTo1stQuestion(
	page: Page,
	request: APIRequestContext,
	browser: Browser,
	showOnDevices: boolean
) {
	const saved = await saveQuiz(request, QUIZ);
	expect(saved.status).toBe(200);
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(page, saved.body.id, { showOnDevices });
	const player = await joinAsPlayer(browser, pin, 'ana');
	await expect(player.page.getByText(/You're in/)).toBeVisible();
	await page.getByRole('button', { name: 'Start game' }).click();
	await page.getByRole('button', { name: /Next Question/ }).click();
	// The tile is up, so the question has reached the phone either way.
	await expect(player.page.getByRole('button', { name: 'Lisbon' })).toBeVisible({
		timeout: 15_000
	});
	return player;
}

test('by default the phone shows shapes, and the question stays on the shared screen', async ({
	page,
	request,
	browser
}) => {
	const player = await playTo1stQuestion(page, request, browser, false);

	// Neither the question nor the answer text is drawn on the phone.
	await expect(player.page.getByText(QUESTION)).toHaveCount(0);
	await expect(player.page.getByText('Lisbon', { exact: true })).toHaveCount(0);
	await expect(player.page.getByText('Porto', { exact: true })).toHaveCount(0);

	// The host's screen is where they are, which is the whole premise of the default.
	await expect(page.getByText(QUESTION)).toBeVisible();

	// The answer is still announced to a screen reader, so shapes-only is not an
	// accessibility regression -- it is a visual choice.
	await expect(player.page.getByRole('button', { name: 'Lisbon' })).toBeVisible();

	await player.context.close();
});

test('with the switch on, the phone carries the question and the answer text', async ({
	page,
	request,
	browser
}) => {
	const player = await playTo1stQuestion(page, request, browser, true);

	await expect(player.page.getByText(QUESTION)).toBeVisible();
	await expect(player.page.getByText('Lisbon', { exact: true })).toBeVisible();
	await expect(player.page.getByText('Porto', { exact: true })).toBeVisible();

	// And it still plays: the point is a second display, not a different game.
	await player.page.getByRole('button', { name: 'Lisbon' }).click();
	await expect(player.page.getByText(/Answer locked in/)).toBeVisible();

	await player.context.close();
});

test('the switch is off when the modal opens, and off again the next time', async ({
	page,
	request
}) => {
	// It is per game, not a remembered preference: a host who turns it on for a call
	// should not silently get it in the next room with a projector.
	const saved = await saveQuiz(request, QUIZ);
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);
	await page.goto(`/view/${saved.body.id}`);

	const dialog = page.getByRole('dialog', { name: 'Start Game' });
	const toggle = dialog.getByRole('switch', {
		name: "Show questions and answers on players' devices"
	});

	await page.getByRole('button', { name: 'Play', exact: true }).click();
	await expect(toggle).toHaveAttribute('aria-checked', 'false');
	await toggle.click();
	await expect(toggle).toHaveAttribute('aria-checked', 'true');

	await page.keyboard.press('Escape');
	await expect(dialog).toBeHidden();

	await page.getByRole('button', { name: 'Play', exact: true }).click();
	await expect(toggle).toHaveAttribute('aria-checked', 'false');
});
