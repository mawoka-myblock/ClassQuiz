import { redirect } from '@sveltejs/kit';
import { signedIn } from '$lib/stores';

export async function load({ session }) {
	if (!session.authenticated) {
		throw redirect(302, '/account/login?returnTo=/create');
	}
	if (session.authenticated) {
		signedIn.set(true);
	}
	return {};
}
