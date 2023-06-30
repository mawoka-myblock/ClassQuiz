// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { redirect } from '@sveltejs/kit';

export async function load({ parent, url }) {
	const verified = url.searchParams.get('verified');
	const returnTo =
		url.searchParams.get('returnTo') !== null ? url.searchParams.get('returnTo') : '/dashboard';

	const { email } = await parent();
	if (email) {
		throw redirect(302, returnTo);
	}
	return {
		verified: verified !== null
	};
}
