import { signedIn } from '$lib/stores';

export async function load({ session }) {
	if (session.authenticated) {
		signedIn.set(true);
	} else {
		signedIn.set(false);
	}
	return {};
}
