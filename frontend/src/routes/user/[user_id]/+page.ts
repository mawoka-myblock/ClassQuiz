/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

import type { PageLoad } from './$types';

export const load = (async ({ params, fetch }) => {
	const user_req = await fetch(`/api/v1/community/user/${params.user_id}`);
	const user = await user_req.json();
	if (!user) {
		return {
			user: undefined,
			quizzes: undefined
		};
	}
	const quiz_req = await fetch(`/api/v1/community/quizzes/${params.user_id}?imported=false`);
	const quizzes = await quiz_req.json();
	return {
		user,
		quizzes
	};
}) satisfies PageLoad;
