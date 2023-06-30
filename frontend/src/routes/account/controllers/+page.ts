// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { PageLoad } from './$types';

export const load = (async ({ fetch }) => {
	const resp = await fetch('/api/v1/box-controller/web/list');
	// const resp = await fetch("https://localhost/api/v1/box-controller/web/list")
	const controllers = await resp.json();
	return {
		controllers
	};
}) satisfies PageLoad;
