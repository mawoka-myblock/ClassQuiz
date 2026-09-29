// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { describe, expect, it } from 'vitest';
import { QuizQuestionType, type Question } from '$lib/quiz_types';
import { isCorrect, isPracticable, isScored } from './score';

const q = (type: QuizQuestionType | undefined, rights: boolean[]): Question =>
	({
		type,
		question: 'Q',
		time: '20',
		answers: rights.map((right, i) => ({ answer: String(i), right }))
	}) as unknown as Question;

describe('practice scoring matches the live game', () => {
	it('ABCD: the picked answer must be a right one', () => {
		const question = q(QuizQuestionType.ABCD, [false, true, false]);
		expect(isCorrect(question, [false, true, false])).toBe(true);
		expect(isCorrect(question, [true, false, false])).toBe(false);
		expect(isCorrect(question, [false, false, false])).toBe(false);
	});

	it('a question with no type is an old ABCD question', () => {
		expect(isCorrect(q(undefined, [true, false]), [true, false])).toBe(true);
		expect(isScored(q(undefined, [true, false]))).toBe(true);
	});

	it('CHECK is all or nothing', () => {
		const question = q(QuizQuestionType.CHECK, [true, false, true]);
		expect(isCorrect(question, [true, false, true])).toBe(true);
		expect(isCorrect(question, [true, false, false]), 'one right answer missing').toBe(false);
		expect(isCorrect(question, [true, true, true]), 'one wrong answer ticked').toBe(false);
		expect(isCorrect(q(QuizQuestionType.CHECK, []), []), 'no answers is no free point').toBe(
			false
		);
	});

	it('VOTING runs but is not scored; the other types are not practicable', () => {
		expect(isPracticable(q(QuizQuestionType.VOTING, [false, false]))).toBe(true);
		expect(isScored(q(QuizQuestionType.VOTING, [false, false]))).toBe(false);
		for (const t of [QuizQuestionType.RANGE, QuizQuestionType.ORDER, QuizQuestionType.TEXT]) {
			expect(isPracticable(q(t, []))).toBe(false);
		}
	});
});
