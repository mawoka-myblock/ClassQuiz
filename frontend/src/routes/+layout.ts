// import { redirect } from '@sveltejs/kit';
import { signedIn } from '$lib/stores';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ data }) => {
	const { email } = data;
	if (email) {
		signedIn.set(true);
		// throw redirect(302, '/dashboard');
	} else {
		signedIn.set(false);
	}
	return {};
};
