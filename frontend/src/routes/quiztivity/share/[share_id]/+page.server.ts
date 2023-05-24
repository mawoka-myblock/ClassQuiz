/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

import { redirect } from '@sveltejs/kit';

import type { PageServerLoad } from './$types';

export const load = (({ params }) => {
	const quiz_id = params.share_id;
	throw redirect(301, `/quiztivity/play?id=${quiz_id}&share=true`);
}) satisfies PageServerLoad;
