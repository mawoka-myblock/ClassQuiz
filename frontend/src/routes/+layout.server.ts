import { signedIn } from '$lib/stores';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ locals }) => {
	if (locals.email) {
		signedIn.set(true);
	} else {
		signedIn.set(false);
	}
	return {
		email: locals.email
	};
};
