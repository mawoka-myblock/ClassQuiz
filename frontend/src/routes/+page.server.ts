// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { redirect } from '@sveltejs/kit';

export const load = async ({ parent }) => {
	const { email } = await parent();
	if (email) {
		redirect(302, '/dashboard');
	}
	return {
		email
	};
};
