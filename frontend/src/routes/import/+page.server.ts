// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { redirect } from '@sveltejs/kit';
import { signedIn } from '$lib/stores';
export async function load({ parent }) {
	const { email } = await parent();
	if (!email) {
		throw redirect(302, '/account/login?returnTo=/import');
	} else {
		if (email) {
			signedIn.set(true);
		}
	}
	return {
		email
	};
}
