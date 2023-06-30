// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

// import type { PageLoad } from './$types';

export const load = async ({ params, fetch }) => {
	const user_req = await fetch(`/api/v1/community/user/${params.user_id}`);
	const user = await user_req.json();
	if (!user) {
		return {
			user: undefined,
			quizzes: undefined
		};
	}
	const quiz_req = await fetch(`/api/v1/community/quizzes/${params.user_id}?imported=false`);
	let quizzes;
	if (quiz_req.status === 404) {
		quizzes = [];
	} else {
		quizzes = await quiz_req.json();
	}
	return {
		user,
		quizzes
	};
}; // satisfies PageLoad;
