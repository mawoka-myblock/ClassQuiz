import { redirect } from '@sveltejs/kit';

export async function load({ session }) {
	if (!session.authenticated) {
		throw redirect(302, '/account/login?returnTo=/account/settings');
	}
	return {
		email: session.email
	};
}
