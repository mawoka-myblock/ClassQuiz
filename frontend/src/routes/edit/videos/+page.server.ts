/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

import type { PageServerLoad } from './$types';

export const load = (async ({ setHeaders }) => {
	setHeaders({
		'Cross-Origin-Embedder-Policy': 'require-corp',
		'Cross-Origin-Opener-Policy': 'same-origin'
	});
}) satisfies PageServerLoad;
