// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { signedIn } from '$lib/stores';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = ({ locals }) => {
	if (locals.email) {
		signedIn.set(true);
	} else {
		signedIn.set(false);
	}
	return {
		email: locals.email
	};
};
