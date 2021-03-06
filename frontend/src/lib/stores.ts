/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

import { writable } from 'svelte/store';

export const navbarVisible = writable(true);
export const signedIn = writable(false);
export const pathname = writable('/');

export const alertModal = writable({ open: false, title: '', body: '' });

import { goto } from '$app/navigation';
import { page } from '$app/stores';

const URLSearchParamsToObject = (params: URLSearchParams) => {
	const obj = {};
	params.forEach((v: string, k: string) => {
		obj[k] = v;
	});
	return obj;
};

export const createQueryParamsStore = (key: string) => {
	let params;
	page.subscribe((v) => {
		params = URLSearchParamsToObject(v.url.searchParams);
	});

	return {
		// eslint-disable-next-line @typescript-eslint/ban-types
		subscribe: (cb: Function) => {
			return page.subscribe((p) => {
				cb(p.url.searchParams.get(key));
			});
		},
		set: (value: string) => {
			params[key] = value;
			const urlSearchParams = new URLSearchParams(params);
			goto(`?${urlSearchParams.toString()}`, {
				keepfocus: true,
				replaceState: true,
				noscroll: true
			});
		}
	};
};
