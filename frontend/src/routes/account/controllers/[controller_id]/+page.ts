// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';

export const load = (async ({ fetch, params }) => {
	const res = await fetch(`/api/v1/box-controller/web/controller?id=${params.controller_id}`);
	if (res.status !== 200) {
		throw error(res.status, await res.text());
	}
	const json: {
		id: string;
		player_name: string;
		last_seen?: string;
		first_seen?: string;
		name: string;
		os_version?: string;
		wanted_os_version?: string;
	} = await res.json();
	return {
		controller: json
	};
}) satisfies PageLoad;
