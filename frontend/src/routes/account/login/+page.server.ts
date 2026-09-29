// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { redirect } from '@sveltejs/kit';
import { safeReturnTo } from '$lib/return_to';

export async function load({ parent, url }) {
	// One channel for every "something just happened to your account" notice, since
	// they all land on this page and only one can be true at a time.
	//
	// The raw value, not a boolean: /api/v1/users/verify sends people here with
	// verified=expired when the link has already been used or superseded, and
	// `verified !== null` showed those the "confirmed!" badge.
	let notice = url.searchParams.get('verified');
	if (notice === null && url.searchParams.get('deleted') === 'true') {
		notice = 'deleted';
	}
	if (notice === null && url.searchParams.get('password_changed') === 'true') {
		notice = 'password_changed';
	}
	const returnTo = safeReturnTo(url.searchParams.get('returnTo'), '/my-quizzes');

	const { email } = await parent();
	// Deleting an account and changing a password both clear the cookies server-side,
	// so `email` should already be gone. If one survives -- a proxy eating Set-Cookie,
	// a partial failure -- showing the notice beats bouncing someone into a dashboard
	// that will 401 them straight back here.
	if (email && notice !== 'deleted' && notice !== 'password_changed') {
		redirect(302, returnTo);
	}
	return {
		notice
	};
}
