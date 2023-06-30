// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { PageLoad } from './$types';
import type { PrivateImageData } from '$lib/quiz_types';

export const load = (async ({ fetch }) => {
	const res = await fetch('/api/v1/storage/list');
	const res2 = await fetch('/api/v1/storage/limit');
	let json: PrivateImageData[];
	if (res.ok) {
		json = await res.json();
	} else {
		json = [];
	}
	const storage_usage: { limit: number; limit_reached: boolean; used: number } =
		await res2.json();
	return {
		images: json,
		storage_usage
	};
}) satisfies PageLoad;
