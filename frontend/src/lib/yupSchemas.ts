// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// skipcq: JS-C1003
import * as yup from 'yup';
import { htmlToPlainText } from './sanitize';

// The title is HTML (bold/italic/etc. from its rich-text editor), so its length has
// to be measured on the visible text, not the markup -- otherwise the budget gets
// eaten by tags a reader never sees. Description is plain text, so its own length
// check needs no such conversion. Exported so settings-card.svelte's live character
// counters share this exact number instead of a second hardcoded copy.
export const TITLE_MAX_LENGTH = 100;
export const DESCRIPTION_MAX_LENGTH = 500;
// Question text is rich text like the title, so it is measured the same way. Answers are
// plain. Both are new on 2026-10-02: the editor bounded the title and description and
// nothing bounded these, so a question or answer of any length could be typed, saved and
// then rendered to a whole room. The matching server-side bounds are MAX_QUESTION_LENGTH
// and MAX_ANSWER_LENGTH in frogquiz/db/models.py -- keep the four numbers in step.
export const QUESTION_MAX_LENGTH = 250;
export const ANSWER_MAX_LENGTH = 100;

export const ABCDQuestionSchema = yup
	.array()
	.of(
		yup.object({
			right: yup.boolean().required(),
			answer: yup
				.string()
				.trim()
				.required('You need an answer')
				.max(
					ANSWER_MAX_LENGTH,
					`An answer has to be shorter than ${ANSWER_MAX_LENGTH} characters`
				)
		})
	)
	.min(2, 'You need at least 2 answers')
	.max(16, "You can't have more than 16 answers");

export const VotingQuestionSchema = yup
	.array()
	.of(
		yup.object({
			answer: yup.string().trim().required('You need an answer'),
			image: yup.string().optional().nullable()
		})
	)
	.min(2, 'You need at least 2 answers')
	.max(16, "You can't have more than 16 answers");

export const RangeQuestionSchema = yup.object({
	min: yup.number(),
	max: yup.number(),
	min_correct: yup.number(),
	max_correct: yup.number()
});

export const TextQuestionSchema = yup
	.array()
	.of(
		yup.object({
			case_sensitive: yup.boolean().required(),
			answer: yup.string().trim().required('You need an answer')
		})
	)
	.min(1, 'You need at least 1 answer')
	.max(16, "You can't have more than 16 answers");

export const dataSchema = yup.object({
	public: yup.boolean().required(),
	type: yup.string(),
	title: yup
		.string()
		.required('A title is required')
		.test(
			'min-length',
			'The title has to be longer than 3 characters',
			(value) => htmlToPlainText(value ?? '').length >= 3
		)
		.test(
			'max-length',
			`The title has to be shorter than ${TITLE_MAX_LENGTH} characters`,
			(value) => htmlToPlainText(value ?? '').length <= TITLE_MAX_LENGTH
		),
	// Optional (MVP.md D14). It was required, at least three characters, and nothing on
	// the page said so -- the field had no label hint and no placeholder.
	description: yup
		.string()
		.max(
			DESCRIPTION_MAX_LENGTH,
			`The description has to be shorter than ${DESCRIPTION_MAX_LENGTH} characters`
		),
	questions: yup
		.array()
		.of(
			yup.object({
				// The question title comes out of the same rich-text editor as the quiz
				// title, so it is HTML and has to be measured on its visible text. A
				// trim() does not help: an emptied editor still hands back '<p></p>',
				// which is six non-blank characters to yup and blank on the projector.
				question: yup
					.string()
					.required('A question-title is required')
					.test(
						'not-blank',
						'A question-title is required',
						(value) => htmlToPlainText(value ?? '').length > 0
					)
					.test(
						'max-length',
						'The question-title has to be shorter than 299 characters',
						(value) => htmlToPlainText(value ?? '').length <= 299
					),
				time: yup.number().required().positive('The time has to be positive'),
				image: yup.string().nullable().lowercase(),
				answers: yup.lazy((v) => {
					if (Array.isArray(v)) {
						if (typeof v[0].right === 'boolean') {
							return ABCDQuestionSchema;
						} else if (typeof v[0].case_sensitive === 'boolean') {
							return TextQuestionSchema;
						} else if (v[0].id !== undefined) {
							return VotingQuestionSchema;
						} else if (v[0].answer !== undefined) {
							return VotingQuestionSchema;
						}
					} else if (typeof v === 'string' || v instanceof String) {
						return yup.string().required("The slide mustn't be empty").nullable();
					} else {
						return RangeQuestionSchema;
					}
				})
			})
		)
		.min(1, 'You need at least one question')
		.max(50, "You can't have more than 50 questions")
});
