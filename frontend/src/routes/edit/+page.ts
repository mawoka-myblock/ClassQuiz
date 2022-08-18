import { redirect, error } from '@sveltejs/kit';
import { signedIn } from '$lib/stores';

export async function load({ url, session }) {
	const quiz_id = url.searchParams.get('quiz_id');
	if (!session.authenticated) {
		throw redirect(302, `/account/login?returnTo=/edit?quiz_id=${quiz_id}`);
	}

	if (session.authenticated) {
		signedIn.set(true);
	}

	if (quiz_id === null) {
		throw error(404);
	}
	return {
		quiz_id
	};
}
