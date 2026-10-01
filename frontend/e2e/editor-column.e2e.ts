// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// The editor is one scrolling column of question cards (MVP.md D7). What that has to do:
// open one card at a time, let you add in the middle, reorder, duplicate and delete, and
// keep the rest of the quiz readable while you work on one question.

import { expect, test, type Page } from '@playwright/test';
import { mc, saveQuiz, rememberAnonQuiz, PHONE } from './helpers';

const QUIZ = {
	title: 'Column',
	description: 'Three questions',
	questions: [
		mc('First question?', [
			['A', true],
			['B', false]
		]),
		mc('Second question?', [
			['C', true],
			['D', false]
		]),
		mc('Third question?', [
			['E', true],
			['F', false]
		])
	]
};

const cards = (page: Page) => page.locator('[data-question-card]');
const openCards = (page: Page) => page.getByRole('textbox', { name: 'Question text' });

async function openQuiz(page: Page, request) {
	const saved = await saveQuiz(request, QUIZ);
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);
	await page.goto(`/edit?quiz_id=${saved.body.id}`);
	await expect(cards(page)).toHaveCount(3);
	return saved.body.id as string;
}

test('every question is on the page, and one card is open at a time', async ({ page, request }) => {
	await openQuiz(page, request);
	// All three are visible as cards, so the shape of the quiz is never hidden.
	await expect(cards(page).filter({ hasText: 'Second question?' })).toBeVisible();
	await expect(cards(page).filter({ hasText: 'Third question?' })).toBeVisible();
	// Only the open one carries a rich-text field: twenty CKEditor instances is a stall,
	// and this is what keeps the column cheap.
	await expect(openCards(page)).toHaveCount(1);

	await page.getByRole('button', { name: /Third question/ }).last().click();
	await expect(openCards(page)).toHaveCount(1);
	await expect(page.getByRole('button', { name: 'Move down' })).toBeDisabled();
});

test('a question can be added between two others', async ({ page, request }) => {
	await openQuiz(page, request);
	await page.getByRole('button', { name: 'Add a question here' }).first().click();
	await page.getByRole('button', { name: /^Multiple-Choice/ }).click();
	await expect(cards(page)).toHaveCount(4);
	// It landed in the gap it was added from, not at the end.
	await openCards(page).fill('Inserted');
	const order = await cards(page).allInnerTexts();
	expect(order[0]).toContain('First question?');
	expect(order[1]).toContain('Inserted');
	expect(order[2]).toContain('Second question?');
});

test('True / False arrives with its answers already written', async ({ page, request }) => {
	await openQuiz(page, request);
	await page.getByRole('button', { name: 'Add new question' }).click();
	await page.getByRole('button', { name: /True \/ False/ }).click();
	const answers = page.getByRole('textbox', { name: 'Enter an answer' });
	await expect(answers).toHaveCount(2);
	await expect(answers.nth(0)).toHaveValue('True');
	await expect(answers.nth(1)).toHaveValue('False');
	// True is already the right answer, which is the whole point of the preset.
	await expect(page.getByRole('button', { name: 'Mark as correct: True', exact: true })).toHaveAttribute(
		'aria-pressed',
		'true'
	);
});

test('duplicate copies the question and does not share its answers', async ({ page, request }) => {
	await openQuiz(page, request);
	await page.getByRole('button', { name: 'Duplicate question' }).click();
	await expect(cards(page)).toHaveCount(4);
	// The copy opens, directly after the original.
	await openCards(page).fill('Changed on the copy');
	const texts = await cards(page).allInnerTexts();
	expect(texts[0]).toContain('First question?');
	expect(texts[1]).toContain('Changed on the copy');
	expect(texts[1]).not.toContain('First question?');
});

test('a question can be moved and deleted', async ({ page, request }) => {
	await openQuiz(page, request);
	await page.getByRole('button', { name: 'Move down' }).click();
	// The column re-renders and scrolls the moved card into view; let it settle before
	// pressing anything else, the way a hand would.
	await expect(cards(page).nth(0)).toContainText('Second question?');
	let texts = await cards(page).allInnerTexts();
	expect(texts[0]).toContain('Second question?');
	expect(texts[1]).toContain('First question?');
	// The card the author was editing travelled with them: it is still the open one.
	await expect(openCards(page)).toHaveCount(1);
	await expect(cards(page).nth(1).getByRole('textbox', { name: 'Question text' })).toBeVisible();

	// Delete asks first: there is no undo, and the editor autosaves.
	await page.getByRole('button', { name: 'Delete question' }).click();
	await page.getByRole('alertdialog').getByRole('button', { name: 'Delete' }).click();
	await expect(cards(page)).toHaveCount(2);
	texts = await cards(page).allInnerTexts();
	expect(texts.join(' ')).not.toContain('First question?');
});

test('the column is the navigation on a phone, and fits one', async ({ browser, request }) => {
	const ctx = await browser.newContext({ viewport: PHONE });
	const page = await ctx.newPage();
	await openQuiz(page, request);
	// No rail, no drawer: the cards themselves are the list, as in Forms and Kahoot.
	await expect(page.getByRole('navigation', { name: 'Questions' })).toBeHidden();
	const overflow = await page.evaluate(
		() => document.documentElement.scrollWidth - document.documentElement.clientWidth
	);
	expect(overflow, 'the editor scrolls sideways on a phone').toBeLessThanOrEqual(0);
	await ctx.close();
});
