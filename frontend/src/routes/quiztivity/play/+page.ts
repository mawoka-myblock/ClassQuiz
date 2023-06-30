// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Data } from '$lib/quiztivity/types';

export const load = (async ({ url, fetch }) => {
	const id = url.searchParams.get('id');
	const share = url.searchParams.get('share') === 'true';
	if (!id) {
		throw error(400, 'id missing');
	}
	let resp: Response;
	if (share) {
		resp = await fetch(`/api/v1/quiztivity/shares/${id}`);
	} else {
		resp = await fetch(`/api/v1/quiztivity/${id}`);
	}
	if (!resp.ok) {
		throw error(resp.status);
	}
	const data: Data = await resp.json();
	return {
		quiztivity: data
	};
}) satisfies PageLoad;
