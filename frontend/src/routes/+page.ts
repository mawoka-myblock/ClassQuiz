// import { redirect } from '@sveltejs/kit';
import { signedIn } from '$lib/stores';

export async function load({ session }) {
	if (session.authenticated) {
		signedIn.set(true);
		// throw redirect(302, '/dashboard');
	} else {
		signedIn.set(false);
	}
	return {};
}
