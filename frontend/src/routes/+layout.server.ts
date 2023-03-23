import { signedIn, premium } from '$lib/stores';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
	if (locals.email) {
		signedIn.set(true);
	} else {
		signedIn.set(false);
	}
	premium.set(locals.premium);
	return {
		email: locals.email,
		premium: locals.premium
	};
};
