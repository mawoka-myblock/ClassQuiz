// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { reach } from 'yup';
import { ABCDQuestionSchema, dataSchema } from '$lib/yupSchemas';
import { QuizQuestionType } from '$lib/quiz_types';

// The two types the MVP offers (D2), and old questions saved before `type` existed.
const CHECKED_TYPES = [undefined, null, QuizQuestionType.ABCD, QuizQuestionType.CHECK];

/**
 * Whether a question is actually runnable: it has a title, at least two answers, every
 * answer has text, and one of them is marked correct.
 *
 * The rail's per-question dot and the header's "n questions need attention" count are both
 * this one function. They started as two hand-written copies of the same rule and already
 * disagreed -- one asked yup, the other trimmed the string -- so a title made only of
 * spaces counted as done in one place and unfinished in the other.
 *
 * It is also the draft rule (MVP.md D14): the server refuses to start a quiz with an
 * unfinished question, using `frogquiz/helpers/completeness.py`. That file and this one
 * must say the same thing.
 */
export const isQuestionComplete = (question): boolean => {
	if (!reach(dataSchema, 'questions[].question').isValidSync(question?.question)) {
		return false;
	}
	// The cut question types can no longer be created, but old quizzes still open, and
	// their rules are not these ones -- a TEXT question has one answer and no `right`. This
	// used to check only for a non-array, which caught RANGE and SLIDE and flagged every
	// TEXT, VOTING and ORDER question as unfinished.
	if (!CHECKED_TYPES.includes(question.type) || !Array.isArray(question.answers)) {
		return true;
	}
	if (question.answers.length < 2) {
		return false;
	}
	if (!question.answers.some((a) => a.right)) {
		return false;
	}
	return question.answers.every((a) => reach(ABCDQuestionSchema, 'answer').isValidSync(a.answer));
};
