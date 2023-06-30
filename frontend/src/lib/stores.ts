// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { writable } from 'svelte/store';

export const navbarVisible = writable(true);
export const signedIn = writable(false);
export const pathname = writable('/');

export const alertModal = writable({ open: false, title: '', body: '' });
