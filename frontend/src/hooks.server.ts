// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { type Handle } from '@sveltejs/kit';
import * as jose from 'jose';

// Docker sets API_URL at runtime (http://api:80). On Netlify the value is baked in
// at build time instead, because build.environment does not reach the function runtime.
const API_BASE = process.env.API_URL ?? import.meta.env.VITE_API_ORIGIN;

/** @type {import('@sveltejs/kit').Handle} */
export const handle: Handle = async ({ event, resolve }) => {
	// Hidden routes are not guarded here any more. Throwing from `handle` runs before
	// the router, so SvelteKit answered with its built-in fallback page: bare "404 | Not
	// found", no navbar, no way home, no theme -- on exactly the sixteen URLs we hide.
	// `reroute` in hooks.ts sends them to a path with no route instead, so they 404
	// through the app and get the same page as any other wrong URL.
	const access_token = event.cookies.get('access_token');
	if (!access_token) {
		event.locals.email = null;
		return resolve(event);
	}
	const jwt = jose.decodeJwt(access_token.replace('Bearer ', ''));
	if (!jwt) {
		event.locals.email = null;
		return resolve(event);
	}
	// if token expires, do a request to get a new one and set the response-cookies on the response
	if (Date.now() >= jwt.exp * 1000) {
		// A backend that is down (restart, deploy) must not turn every page into a
		// 500 -- fall through to the token we already have and let the API say no.
		const res = await fetch(`${API_BASE}/api/v1/users/check`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				Cookie: event.request.headers.get('cookie') || ''
			}
		}).catch(() => null);
		if (res?.ok) {
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
	event.locals.email = jwt.sub;
	return resolve(event);
};
