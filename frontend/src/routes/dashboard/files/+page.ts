// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { PageLoad } from './$types';

export const load = (async ({ fetch }) => {
	const res = await fetch('/api/v1/storage/list');
	return { files: await res.json() };
}) satisfies PageLoad;
