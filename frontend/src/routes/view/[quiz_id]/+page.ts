import { error } from '@sveltejs/kit';
import type { PageLoad } from '@sveltejs/kit';

export const load: PageLoad = async ({ params, fetch, session }) => {
	const { quiz_id } = params;
	const res = await fetch(`/api/v1/quiz/get/public/${quiz_id}`);
	if (res.status === 404 || res.status === 400) {
		throw error(404);
	} else if (res.status === 200) {
		const quiz = await res.json();
		return {
			quiz: quiz,
			logged_in: session.authenticated
		};
	} else {
		throw error(500);
	}
};
