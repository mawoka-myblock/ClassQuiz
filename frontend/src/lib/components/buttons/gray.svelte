<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { createBubbler } from 'svelte/legacy';

	const bubble = createBubbler();

	interface Props {
		disabled?: boolean;
		flex?: boolean;
		href?: undefined | string;
		target?: undefined | string;
		children?: import('svelte').Snippet;
	}

	let {
		disabled = false,
		flex = false,
		href = undefined,
		target = '_self',
		children
	}: Props = $props();
</script>

{#if href}
	<a
		{href}
		{target}
		class="w-full px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded-sm text-center hover:bg-gray-300 focus:outline-hidden disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-gray-600"
		onclick={bubble('click')}
		class:flex
		class:block={!flex}
		class:justify-center={flex}
	>
		{@render children?.()}
	</a>
{:else}
	<button
		{disabled}
		class="w-full px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded-sm text-center hover:bg-gray-300 focus:outline-hidden disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-gray-600"
		onclick={bubble('click')}
		class:flex
		class:justify-center={flex}
	>
		{@render children?.()}
	</button>
{/if}
