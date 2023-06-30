// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { Handle } from '@sveltejs/kit';
import jws from 'jws';

/** @type {import('@sveltejs/kit').Handle} */
export const handle: Handle = async ({ event, resolve }) => {
	const access_token = event.cookies.get('access_token');
	if (!access_token) {
		event.locals.email = null;
		return resolve(event);
	}
	const jwt = jws.decode(access_token.replace('Bearer ', ''));
	// if token expires, do a request to get a new one and set the response-cookies on the response
	if (Date.now() >= jwt.payload.exp * 1000) {
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
				/* empty */
			}
			return resp;
		}
	}
	event.locals.email = jwt.payload.sub;
	return resolve(event);
};

/*export const getSession: GetSession = async (event) => {
	return {
		email: event.locals.email,
		authenticated: Boolean(event.locals.email)
	};
};*/
