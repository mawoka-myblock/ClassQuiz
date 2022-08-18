import { redirect } from '@sveltejs/kit';

export async function load({ session, url }) {
	const verified = url.searchParams.get('verified');
	const returnTo =
		url.searchParams.get('returnTo') !== null ? url.searchParams.get('returnTo') : '/dashboard';
	if (session.authenticated) {
		throw redirect(302, returnTo);
	}
	return {
		verified: verified !== null
	};
}
