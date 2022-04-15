import adapter from '@sveltejs/adapter-node';
import preprocess from 'svelte-preprocess';
import { isoImport } from 'vite-plugin-iso-import';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://github.com/sveltejs/svelte-preprocess
	// for more information about preprocessors
	preprocess: [
		preprocess({
			postcss: true
		})
	],

	kit: {
		adapter: adapter({
			out: 'build',
			precompress: true
		}),
		vite: {
			optimizeDeps: {
				include: ['swiper']
			},
			build: {
				sourcemap: true
			},
			plugins: [isoImport()]
		}
	}
};

export default config;
