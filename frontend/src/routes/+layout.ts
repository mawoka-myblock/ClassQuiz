// import { redirect } from '@sveltejs/kit';
import { signedIn, premium } from '$lib/stores';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ data }) => {
	const { email } = data;
	premium.set(data.premium);
	if (email) {
		signedIn.set(true);
		// throw redirect(302, '/dashboard');
	} else {
		signedIn.set(false);
	}
	return {};
};
