// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { redirect } from '@sveltejs/kit';

export async function load({ parent, url }) {
	const { email } = await parent();
	if (!email) {
		throw redirect(302, '/account/login');
	}
	const token = url.searchParams.get('token');
	const pin = url.searchParams.get('pin');
	let auto_connect = url.searchParams.get('connect') !== null;
	if (token === null || pin === null) {
		auto_connect = false;
	}
	return {
		game_pin: pin === null ? '' : pin,
		game_token: token === null ? '' : token,
		auto_connect
	};
}
