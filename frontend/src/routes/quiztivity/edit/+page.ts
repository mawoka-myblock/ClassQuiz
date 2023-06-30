// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Data } from '$lib/quiztivity/types';

export const load = (async ({ url, fetch }) => {
	const id = url.searchParams.get('id');
	if (!id) {
		throw error(400, 'id missing');
	}
	const resp = await fetch(`/api/v1/quiztivity/${id}`);
	if (!resp.ok) {
		throw error(404, 'quiztivity not found');
	}
	const data: Data = await resp.json();
	return {
		quiztivity: data
	};
}) satisfies PageLoad;
