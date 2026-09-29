// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import type { PageServerLoad } from './$types';

// Open to everyone: signed out it lists this browser's quizzes, signed in the account's.
export const load: PageServerLoad = async ({ parent }) => {
	const { email } = await parent();
	return { email };
};
