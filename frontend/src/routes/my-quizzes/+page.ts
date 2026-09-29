// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import type { PageLoad } from './$types';

export const load = (async ({ fetch, data }) => {
	// This browser's anonymous quizzes are read from localStorage in the page, so
	// only the account list is loaded here.
	if (!data.email) {
		return { ...data, quizzes: null };
	}
	const res = await fetch('/api/v1/quiz/list?page_size=100');
	const quizzes = res.ok ? await res.json() : [];
	return { ...data, quizzes };
}) satisfies PageLoad;
