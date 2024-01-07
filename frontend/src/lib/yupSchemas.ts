// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

// skipcq: JS-C1003
import * as yup from 'yup';

export const ABCDQuestionSchema = yup
	.array()
	.of(
		yup.object({
			right: yup.boolean().required(),
			answer: yup.string().required('You need an answer')
		})
	)
	.min(2, 'You need at least 2 answers')
	.max(16, "You can't have more than 16 answers");

export const VotingQuestionSchema = yup
	.array()
	.of(
		yup.object({
			answer: yup.string().required('You need an answer'),
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
			answer: yup.string().required('You need an answer')
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
		.min(3, 'The title has to be longer than 3 characters')
		.max(300, 'The title has to be shorter than 300 characters'),
	description: yup
		.string()
		.required('The description is required!')
		.min(3, 'The description has to be longer than 3 characters')
		.max(500, 'The description has to be shorter than 500 characters'),
	questions: yup
		.array()
		.of(
			yup.object({
				question: yup.string().required('A question-title is required').max(299),
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
		.max(50, "You can't have more than 32 questions")
});
