/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

// import type { PageLoad } from './$types';

export const load = async ({ params, fetch }) => {
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
}; //satisfies PageLoad;
