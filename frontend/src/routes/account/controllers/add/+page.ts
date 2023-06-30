// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { PageLoad } from './$types';

export const load = (async ({ fetch }) => {
	const resp = await fetch('/api/v1/users/me');
	const json = await resp.json();
	return {
		username: json.username
	};
}) satisfies PageLoad;
