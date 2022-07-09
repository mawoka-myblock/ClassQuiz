import { sveltekit } from '@sveltejs/kit/vite';
import { isoImport } from 'vite-plugin-iso-import';

/** @type {import('vite').UserConfig} */
const config = {
	plugins: [sveltekit(), isoImport()],
	optimizeDeps: {
		include: ['swiper']
	},
	build: {
		sourcemap: true
	}
};

export default config;
