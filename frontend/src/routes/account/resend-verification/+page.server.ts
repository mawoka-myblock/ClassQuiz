// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { redirect } from '@sveltejs/kit';

export async function load({ parent }) {
	const { email } = await parent();
	// Nobody signed in needs this page: an account that can log in is confirmed.
	if (email) {
		redirect(302, '/my-quizzes');
	}
	return {};
}
