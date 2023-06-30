// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { error } from '@sveltejs/kit';

export const load = async ({ params, parent }) => {
	const { quiz_id } = params;
	const res = await fetch(`${process.env.API_URL}/api/v1/quiz/get/public/${quiz_id}`);
	const { email } = await parent();
	if (res.status === 404 || res.status === 400) {
		throw error(404);
	} else if (res.status === 200) {
		const quiz = await res.json();
		return {
			quiz,
			logged_in: Boolean(email)
		};
	} else {
		throw error(500);
	}
};
