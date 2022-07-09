import { sveltekit } from '@sveltejs/kit/vite';

/** @type {import('vite').UserConfig} */
const config = {
	plugins: [sveltekit()],
	optimizeDeps: {
		include: ['swiper']
	},
	build: {
		sourcemap: true
	}
};

export default config;
