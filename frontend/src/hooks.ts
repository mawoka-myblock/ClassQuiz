/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

import * as cookie from 'cookie';
import type { Handle, GetSession } from '@sveltejs/kit';

/** @type {import('@sveltejs/kit').Handle} */
export const handle: Handle = async ({ event, resolve }) => {
	const cookies = cookie.parse(event.request.headers.get('cookie') || '');
	const jwt = /^Bearer (.*)$/gm.exec(cookies.access_token);
	const rememberme_token = cookies.rememberme_token;
	if (rememberme_token) {
		const res = await fetch(`${process.env.API_URL}/api/v1/users/auth/internal`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				rememberme: rememberme_token,
				jwt: jwt === null ? undefined : jwt[0]
			})
		});
		let new_jwt;
		if (jwt) {
			new_jwt = jwt[0];
		} else {
			new_jwt = cookie.parse(res.headers.get('set-cookie')).access_token;
		}
		event.locals.email = await (
			await fetch(`${process.env.API_URL}/api/v1/users/auth/internal/email`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					jwt: new_jwt
				})
			})
		).text();
		const resp = await resolve(event);
		resp.headers.set('Set-Cookie', res.headers.get('set-cookie'));
		return resp;
	} else {
		event.locals.email = null;
		return resolve(event);
	}
};

export const getSession: GetSession = async (event) => {
	return {
		email: event.locals.email,
		authenticated: Boolean(event.locals.email)
	};
};
