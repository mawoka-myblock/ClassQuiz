<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import '../app.css';
	import Navbar from '$lib/navbar.svelte';
	import { pathname } from '$lib/stores';
	import { navbarVisible } from '$lib/stores.svelte';

	import { initLocalizationContext } from '$lib/i18n';
	import { browser } from '$app/environment';
	import CommandPalette from '$lib/components/commandpalette.svelte';
	interface Props {
		children?: import('svelte').Snippet;
	}

	let { children }: Props = $props();
	const plausible_data_url = import.meta.env.VITE_PLAUSIBLE_DATA_URL;

	if (browser) {
		pathname.set(window.location.pathname);
		if (
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches)
		) {
			document.documentElement.classList.add('dark');
		} else {
			document.documentElement.classList.remove('dark');
		}
	}
	let start_language = 'en';
	if (browser) {
		start_language = localStorage.getItem('language') ?? 'en';
	}
	initLocalizationContext(start_language);
</script>

<svelte:head>
	{#if plausible_data_url}
		<script
			defer
			data-domain={plausible_data_url}
			src="https://plausible.nexus.mawoka.eu/js/script.file-downloads.outbound-links.pageview-props.tagged-events.js"
		></script>
		<script>
			window.plausible =
				window.plausible ||
				function () {
					(window.plausible.q = window.plausible.q || []).push(arguments);
				};
		</script>
	{/if}
</svelte:head>

{#if navbarVisible.visible}
	<Navbar />
	<div class="pt-16">
		<div class="z-40"></div>
	</div>
{/if}
{@render children?.()}
<CommandPalette />

<style lang="scss">
	:global(html:not(.dark)) {
		// height: 100%;
		// width: 100%;

		// bg-gradient-to-r from-[#009444] via-[#39b54a] to-[#8dc63f]
		//background: linear-gradient(to right, #009444, #39b54a, #8dc63f) repeat-y;
		background-color: #d6edc9;
		background-size: cover;
		/*background: linear-gradient(-225deg, #231557 0%, #44107A 29%, #FF1361 67%, #FFF800 100%); */
		/*background: linear-gradient(-225deg, #22E1FF 0%, #1D8FE1 48%, #625EB1 100%); */
		color: black;

		// background-size: 400% 400%;

		//animation: background_animation 5s ease infinite;
	}

	:global(html.dark) {
		//background-color: #0f2702;
		background-color: #4e6e58;
		background-size: cover;
		color: white;

		:global(#pips-slider) {
			--pip: white;
			--pip-active: white;
		}
	}

	@keyframes background_animation {
		0% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
		100% {
			background-position: 0% 50%;
		}
	}
</style>
