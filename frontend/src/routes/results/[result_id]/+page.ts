// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0
import type { PageLoad } from './$types';
import { is_id } from '$lib/ids';

export const load: PageLoad = async ({ params, fetch }) => {
	if (!is_id(params.result_id)) {
		return { results: undefined };
	}
	const res = await fetch(`/api/v1/results/${params.result_id}?include_quiz=true`);
	let json;
	if (res.ok) {
		json = await res.json();
	} else {
		json = undefined;
	}
	return {
		results: json
	};
};
