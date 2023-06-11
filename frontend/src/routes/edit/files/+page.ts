/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */
import type { PageLoad } from './$types';

export interface ImageData {
	id: string;
	uploaded_at: string;
	mime_type: string;
	hash?: string;
	size?: number;
	deleted_at?: string;
	alt_text?: string;
	filename?: string;
	thumbhash?: string;
	server?: string;
	imported: boolean;
	quizzes: { id: string }[];
	quiztivities: { id: string }[];
}

export const load = (async ({ fetch }) => {
	const res = await fetch('/api/v1/storage/list');
	const json: ImageData[] = await res.json();
	return {
		images: json
	};
}) satisfies PageLoad;
