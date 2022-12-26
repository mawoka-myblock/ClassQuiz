/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

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

export const SlideQuestionSchema = yup.array().of(
	yup.object({
		type: yup.string().required(),
		x: yup.number(),
		y: yup.number(),
		height: yup.number(),
		width: yup.number(),
		data: yup.string().optional(),
		id: yup.number().required()
	})
);
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
				image: yup
					.string()
					.nullable()
					.matches(
						/^(http(|s):\/\/.*(|:)\d*\/api\/v1\/storage\/download\/.{36}--.{36}|https:\/\/i\.imgur\.com\/.{7}.(jpg|png|gif))$|^$/,
						"The image-url isn't valid"
					)
					.lowercase(),
				answers: yup.lazy((v) => {
					if (Array.isArray(v)) {
						try {
							if (typeof v[0].right === 'boolean') {
								// console.log('ABCDQuestionSchema');
								return ABCDQuestionSchema;
							} else if (v[0].answer !== undefined) {
								// console.log('VotingQuestionSchema');
								return VotingQuestionSchema;
							} else {
								// console.log('SlideQuestionSchema');
								return SlideQuestionSchema;
							}
						} catch {
							// console.log('SlideQuestionSchema');
							return SlideQuestionSchema;
						}
					} else {
						// console.log('RangeQuestionSchema');
						return RangeQuestionSchema;
					}
				})
			})
		)
		.min(1, 'You need at least one question')
		.max(50, "You can't have more than 32 questions")
});
