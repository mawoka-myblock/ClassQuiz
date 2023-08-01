// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0
import type { PageLoad } from './$types';

export const load = (async ({ fetch, url }) => {
	const page = url.searchParams.get('page') ?? '1';
	const all = Boolean(url.searchParams.get('all')) ?? false;
	const resp = await fetch(
		`/api/v1/moderation/quizzes?page=${page}&all=${all ? 'true' : 'false'}`
	);
	const quizzes = await resp.json();
	return {
		page,
		all,
		quizzes
	};
}) satisfies PageLoad;
