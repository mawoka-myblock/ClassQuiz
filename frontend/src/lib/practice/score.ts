// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Scoring for practice mode, matching the live game's rules so practice tells you the
// truth about how the game will mark you:
// - ABCD: right if the one answer picked is marked right (check_answer in the backend
//   compares against any right answer, so a question with two right answers accepts
//   either).
// - CHECK: all or nothing -- the ticked set must equal the right set exactly
//   (check_check_question in frogquiz/socket_server/helpers.py).
// - VOTING has no right answer and is not scored.
import { QuizQuestionType, type Question } from '$lib/quiz_types';

type Tile = { right?: boolean };

/** Question types practice can run. The rest open, say so, and let you move on. */
export const isPracticable = (q: Question): boolean =>
	q.type === undefined ||
	q.type === QuizQuestionType.ABCD ||
	q.type === QuizQuestionType.CHECK ||
	q.type === QuizQuestionType.VOTING;

export const isScored = (q: Question): boolean =>
	q.type === undefined || q.type === QuizQuestionType.ABCD || q.type === QuizQuestionType.CHECK;

export function isCorrect(q: Question, picked: boolean[]): boolean {
	const answers = q.answers as Tile[];
	if (q.type === QuizQuestionType.CHECK) {
		return (
			answers.length > 0 && answers.every((a, i) => Boolean(a.right) === Boolean(picked[i]))
		);
	}
	const chosen = picked.findIndex(Boolean);
	return chosen !== -1 && Boolean(answers[chosen]?.right);
}
