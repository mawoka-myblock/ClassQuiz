// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { redirect } from '@sveltejs/kit';

export async function load({ parent }) {
	const { email } = await parent();
	if (!email) {
		throw redirect(302, '/account/login?returnTo=/create');
	}
	return {};
}
