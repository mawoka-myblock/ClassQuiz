// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import type { RequestHandler } from '@sveltejs/kit';

// The dashboard and /my-quizzes were one list split by whether you were signed in.
// They are one page now (MVP.md decision D1); this keeps old links and bookmarks working.
export const GET: RequestHandler = () => {
	return new Response(undefined, {
		status: 302,
		headers: {
			Location: '/my-quizzes'
		}
	});
};
