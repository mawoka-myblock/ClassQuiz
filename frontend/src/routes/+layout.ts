// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

// import { redirect } from '@sveltejs/kit';
import { signedIn } from '$lib/stores';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = ({ data }) => {
	const { email } = data;
	if (email) {
		signedIn.set(true);
		// throw redirect(302, '/dashboard');
	} else {
		signedIn.set(false);
	}
	return {};
};
