<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	export let disabled = false;
	export let flex = false;

	export let href: undefined | string = undefined;
	export let target: undefined | string = '_self';
</script>

{#if href}
	<a
		{href}
		{target}
		class="w-full px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded text-center hover:bg-gray-300 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-gray-600"
		on:click
		class:flex
		class:block={!flex}
		class:justify-center={flex}
	>
		<slot />
	</a>
{:else}
	<button
		{disabled}
		class="w-full px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded text-center hover:bg-gray-300 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-gray-600"
		on:click
		class:flex
		class:justify-center={flex}
	>
		<slot />
	</button>
{/if}
