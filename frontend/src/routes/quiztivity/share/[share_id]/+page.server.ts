// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { redirect } from '@sveltejs/kit';

import type { PageServerLoad } from './$types';

export const load = (({ params }) => {
	const quiz_id = params.share_id;
	throw redirect(301, `/quiztivity/play?id=${quiz_id}&share=true`);
}) satisfies PageServerLoad;
