import * as yup from 'yup';

export const dataSchema = yup.object({
	public: yup.boolean().required(),
	title: yup
		.string()
		.required('A title is required')
		.min(3, 'The title has to be longer than 3 characters')
		.max(300, 'The title has to be shorter than 300 characters'),
	description: yup
		.string()
		.required()
		.min(3, 'The title has to be longer than 3 characters')
		.max(300, 'The title has to be shorter than 300 characters'),
	questions: yup
		.array()
		.of(
			yup.object({
				question: yup.string().required('A question is required').max(299),
				time: yup.number().required().positive('The time has to be positive'),
				image: yup
					.string()
					.nullable()
					.matches(
						/^(http(|s):\/\/.*(|:)\d*\/api\/v1\/storage\/download\/.{36}--.{36}|https:\/\/i\.imgur\.com\/.{7}.(jpg|png|gif))$|^$/,
						"The image-url isn't valid"
					)
					.lowercase(),
				answers: yup
					.array()
					.of(
						yup.object({
							right: yup.boolean().required(),
							answer: yup.string().required('You need an answer')
						})
					)
					.min(2, 'You need at least 2 answers')
					.max(16, "You can't have more than 16 answers")
			})
		)
		.min(1, 'You need at least one question')
		.max(50, "You can't have more than 32 questions")
});
