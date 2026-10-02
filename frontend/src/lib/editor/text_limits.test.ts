// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// The editor's text bounds and the server's have to agree, and they are written in two
// files in two languages. They did not agree before 2026-10-02: the editor enforced a
// title and description cap and the server enforced nothing at all, so anything that
// skipped the editor -- the API directly, a Kahoot import, a scripted client -- could
// store a 5000-character title. It did; that is how this was found.

import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const read = (p: string) => readFileSync(resolve(process.cwd(), p), 'utf8');

/** An `int` constant out of models.py, underscores and all. */
function serverLimit(name: string): number {
	const src = read('../frogquiz/db/models.py');
	const m = src.match(new RegExp(`^${name} = ([0-9_]+)`, 'm'));
	if (!m) throw new Error(`${name} is gone from frogquiz/db/models.py`);
	return Number(m[1].replace(/_/g, ''));
}

function clientLimit(name: string): number {
	const src = read('src/lib/yupSchemas.ts');
	const m = src.match(new RegExp(`export const ${name} = ([0-9_]+)`));
	if (!m) throw new Error(`${name} is gone from yupSchemas.ts`);
	return Number(m[1].replace(/_/g, ''));
}

describe('text limits', () => {
	it.each([
		['TITLE_MAX_LENGTH', 'MAX_TITLE_LENGTH'],
		['DESCRIPTION_MAX_LENGTH', 'MAX_DESCRIPTION_LENGTH'],
		['QUESTION_MAX_LENGTH', 'MAX_QUESTION_LENGTH'],
		['ANSWER_MAX_LENGTH', 'MAX_ANSWER_LENGTH'],
		// The editor was looser than the server on answers (16 vs 10), the question title
		// (299 vs 250) and the timer (unbounded vs 999), so a quiz the editor accepted
		// 422'd on save. These pin editor == server so that cannot come back.
		['MAX_ANSWERS_PER_QUESTION', 'MAX_ANSWERS_PER_QUESTION'],
		['MAX_QUESTIONS_PER_QUIZ', 'MAX_QUESTIONS_PER_QUIZ'],
		['MAX_QUESTION_SECONDS', 'MAX_QUESTION_SECONDS']
	])('%s matches the server’s %s', (client, server) => {
		expect(clientLimit(client)).toBe(serverLimit(server));
	});

	it('bounds every field that reaches a projector', () => {
		// A missing bound is the bug this whole file is about, so absence is asserted
		// rather than left to whoever adds the next field.
		for (const name of [
			'MAX_TITLE_LENGTH',
			'MAX_DESCRIPTION_LENGTH',
			'MAX_QUESTION_LENGTH',
			'MAX_ANSWER_LENGTH'
		]) {
			expect(serverLimit(name)).toBeGreaterThan(0);
		}
	});

	it('measures rich text on the visible characters, not the markup', () => {
		// Title and question come out of the editor as HTML. Counting the raw string
		// would spend the budget on tags the writer never typed, and would make the same
		// sentence pass or fail depending on whether a word in it is bold.
		const models = read('../frogquiz/db/models.py');
		expect(models).toMatch(/def _visible_length/);
		expect(models).toMatch(/bleach\.clean\(value, tags=\[\], strip=True\)/);
		// And the client half does the same, or the two disagree on identical input.
		expect(read('src/lib/yupSchemas.ts')).toMatch(/htmlToPlainText/);
	});

	it('leaves room for a real question, and stops well short of a broken layout', () => {
		// Sanity rails rather than exact values: the point is that nobody "fixes" a
		// failing save by moving a limit to 5000.
		expect(serverLimit('MAX_TITLE_LENGTH')).toBeGreaterThanOrEqual(60);
		expect(serverLimit('MAX_TITLE_LENGTH')).toBeLessThanOrEqual(200);
		expect(serverLimit('MAX_QUESTION_LENGTH')).toBeGreaterThanOrEqual(120);
		expect(serverLimit('MAX_QUESTION_LENGTH')).toBeLessThanOrEqual(500);
		expect(serverLimit('MAX_ANSWER_LENGTH')).toBeGreaterThanOrEqual(50);
		expect(serverLimit('MAX_ANSWER_LENGTH')).toBeLessThanOrEqual(200);
	});
});
