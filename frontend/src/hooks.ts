// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import type { Reroute } from '@sveltejs/kit';
import { isHidden, HIDDEN_PATH } from '$lib/hidden_routes';

/**
 * Hidden routes resolve to a path with no route, so they 404 through the app's own
 * error page rather than through SvelteKit's built-in fallback. Shared hook: this runs
 * for the first request and for client-side navigation alike, so a link to a hidden
 * page behaves the same whether it was typed or clicked.
 */
export const reroute: Reroute = ({ url }) => (isHidden(url.pathname) ? HIDDEN_PATH : undefined);
