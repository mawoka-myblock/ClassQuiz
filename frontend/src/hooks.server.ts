// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { error, type Handle } from '@sveltejs/kit';
import * as jose from 'jose';

// Docker sets API_URL at runtime (http://api:80). On Netlify the value is baked in
// at build time instead, because build.environment does not reach the function runtime.
const API_BASE = process.env.API_URL ?? import.meta.env.VITE_API_ORIGIN;

// Features whose entry points PR #5 removed from the UI. The routes themselves stayed
// reachable by typing the URL, which is obscurity rather than access control. Their API
// routers are gated by ENABLE_QUIZTIVITY / ENABLE_BOX_CONTROLLER on the backend; this is
// the matching frontend half. Delete an entry to bring a feature back.
const DISABLED_ROUTES = [
	'/quiztivity',
	'/controller',
	'/account/controllers',
	// Nothing is left on this page once TOTP and backup codes are gone.
	'/account/settings/security',
	// Upstream's public docs (MVP.md §2). The legal pages -- tos, privacy-policy,
	// attribution -- stay, and so does import-from-kahoot while /import links to it.
	// Each hidden page also has prerender turned off; see its +page.js.
	'/docs/self-host',
	'/docs/develop',
	'/docs/roadmap',
	'/docs/pow',
	'/docs/features',
	'/docs/frogquizcontroller',
	'/docs/quiz',
	// Hidden for the MVP by Gonçalo, 2026-09-29 (MVP.md D4, D6, D15). Their APIs stay up:
	// hiding a page is not access control, and none of these endpoints is a risk.
	'/docs/import-from-kahoot',
	'/import',
	'/results',
	'/edit/files',
	'/dashboard/files',
	'/edit/videos',
	'/remote',
	'/user',
	'/account/settings/avatar'
];

// Hidden themselves, but with children that stay: matched exactly, not as a prefix.
const DISABLED_EXACT = ['/docs'];

/** @type {import('@sveltejs/kit').Handle} */
export const handle: Handle = async ({ event, resolve }) => {
	const path = event.url.pathname.replace(/\/$/, '') || '/';
	if (
		DISABLED_EXACT.includes(path) ||
		DISABLED_ROUTES.some((p) => path === p || path.startsWith(`${p}/`))
	) {
		error(404, 'Not found');
	}
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
