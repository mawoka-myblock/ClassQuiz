import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = (async ({ url }) => {
	const code = url.searchParams.get('code');
	const id = url.searchParams.get('id');
	if (!id || !code) {
		throw error(404, JSON.stringify({ detail: 'id and/or code are/is missing' }));
	}
	return {
		id,
		code
	};
}) satisfies PageServerLoad;
