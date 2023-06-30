// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { PageLoad } from './$types';

export const load = (async ({ fetch }) => {
	const response = await fetch('/api/v1/search/', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			q: '*',
			sort: ['created_at:desc']
		})
	});
	return {
		results: await response.json()
	};
}) satisfies PageLoad;
