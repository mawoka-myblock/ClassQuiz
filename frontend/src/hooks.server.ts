/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

import * as cookie from 'cookie';
import type { Handle } from '@sveltejs/kit';

/** @type {import('@sveltejs/kit').Handle} */
export const handle: Handle = async ({ event, resolve }) => {
	const res = await fetch(`${process.env.API_URL}/api/v1/users/check`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Cookie: event.request.headers.get('cookie') || ''
		}
	});
	if (res.ok) {
		event.locals.email = await res.text();
		const resp = await resolve(event);
		try {
			resp.headers.set('Set-Cookie', res.headers.get('set-cookie'));
		} catch {
			console.log('Cannot mutate immutable header');
		}

		return resp;
	} else {
		event.locals.email = null;
		return resolve(event);
	}
};

/*export const getSession: GetSession = async (event) => {
	return {
		email: event.locals.email,
		authenticated: Boolean(event.locals.email)
	};
};*/
