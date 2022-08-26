/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

import { redirect } from '@sveltejs/kit';

export const load = async ({ parent }) => {
	const { email } = await parent();
	if (email) {
		throw redirect(302, '/dashboard');
	}
	return {
		email
	};
};
