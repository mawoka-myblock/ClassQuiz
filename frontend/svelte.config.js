// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import adapter from '@sveltejs/adapter-node';
import preprocess from 'svelte-preprocess';
import { mdsvex } from 'mdsvex';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://github.com/sveltejs/svelte-preprocess
	// for more information about preprocessors
	preprocess: [
		preprocess({
			postcss: true
		}),
		mdsvex()
	],
	extensions: ['.svelte', '.svx'],

	kit: {
		adapter: adapter({
			out: 'build',
			precompress: true
		})
		// +++ SOON OBSOLETE +++
		/*
		vite: {
			optimizeDeps: {
				include: ['swiper']
			},
			build: {
				sourcemap: true
			}
		}
		*/
		// --- SOON OBSOLETE ---
	}
};

export default config;
