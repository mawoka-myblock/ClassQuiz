// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

/**
 * Routes whose entry points are hidden for the MVP (MVP.md §2 and §4.3).
 *
 * The code stays in the tree -- hide, don't delete -- and the API behind each one stays
 * up: hiding a page is not access control, and none of these endpoints is a risk. Delete
 * an entry to bring a feature back.
 */
export const DISABLED_ROUTES = [
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
	// Hidden for the MVP by Gonçalo, 2026-09-29 (MVP.md D4, D6, D15).
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

/** Hidden themselves, but with children that stay: matched exactly, not as a prefix. */
export const DISABLED_EXACT = ['/docs'];

/**
 * Where a hidden route is sent. Nothing routes here, so SvelteKit's own router answers
 * 404 and the app's `+error.svelte` renders it -- with the navbar, the theme and a way
 * home. Guarding in `handle` instead threw before the router ran, which got the
 * built-in fallback page: bare "404 | Not found" and no way out, on the sixteen URLs we
 * hide and nowhere else.
 */
export const HIDDEN_PATH = '/__hidden';

export const isHidden = (pathname: string): boolean => {
	const path = pathname.replace(/\/$/, '') || '/';
	return (
		DISABLED_EXACT.includes(path) ||
		DISABLED_ROUTES.some((p) => path === p || path.startsWith(`${p}/`))
	);
};
