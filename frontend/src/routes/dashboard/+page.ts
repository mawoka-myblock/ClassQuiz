import { redirect } from '@sveltejs/kit';

export async function load({ session }) {
	if (!session.authenticated) {
		throw redirect(302, '/account/login?returnTo=/dashboard');
	}
	return {
		email: session.email
	};
}
