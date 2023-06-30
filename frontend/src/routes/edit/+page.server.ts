// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { redirect, error } from '@sveltejs/kit';
import { signedIn } from '$lib/stores';

export async function load({ url, parent }) {
	const quiz_id = url.searchParams.get('quiz_id');
	const { email } = await parent();
	if (!email) {
		throw redirect(302, `/account/login?returnTo=/edit?quiz_id=${quiz_id}`);
	}

	if (email) {
		signedIn.set(true);
	}

	if (quiz_id === null) {
		throw error(404);
	}
	return {
		quiz_id
	};
}
