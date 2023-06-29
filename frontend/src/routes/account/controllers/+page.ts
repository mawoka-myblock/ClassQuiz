/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

import type { PageLoad } from './$types';

export const load = (async ({ fetch }) => {
	const resp = await fetch('/api/v1/box-controller/web/list');
	// const resp = await fetch("https://localhost/api/v1/box-controller/web/list")
	const controllers = await resp.json();
	return {
		controllers
	};
}) satisfies PageLoad;
