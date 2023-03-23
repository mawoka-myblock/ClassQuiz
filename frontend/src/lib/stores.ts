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
export const premium = writable(false);
