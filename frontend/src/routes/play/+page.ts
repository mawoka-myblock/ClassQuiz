import { signedIn } from '$lib/stores';

export async function load({ url, session }) {
	if (session.authenticated) {
		signedIn.set(true);
	}
	const token = url.searchParams.get('pin');
	return {
		game_pin: token === null ? '' : token
	};
}
