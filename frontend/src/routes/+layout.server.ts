import { signedIn } from '$lib/stores';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
	if (locals.email) {
		signedIn.set(true);
	} else {
		signedIn.set(false);
	}
	return {
		email: locals.email
	};
};
