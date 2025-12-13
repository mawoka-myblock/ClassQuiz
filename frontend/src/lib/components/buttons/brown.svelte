<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	interface Props {
		disabled?: boolean;
		flex?: boolean;
		href?: undefined | string;
		target?: undefined | string;
		type?: 'button' | 'submit' | 'reset';
		children?: import('svelte').Snippet;
		onclick?: (event: MouseEvent) => void;
	}

	let {
		disabled = false,
		flex = false,
		href = undefined,
		target = '_self',
		type = 'button',
		children,
		onclick
	}: Props = $props();
</script>

{#if href}
	<a
		{href}
		{target}
		{disabled}
		class:opacity-50={disabled}
		class:cursor-not-allowed={disabled}
		class:pointer-events-none={disabled}
		class="text-black hover:bg-bg-[#B07156]/80 w-full px-4 py-2 leading-5 transition-all duration-200 transform bg-[#B07156] rounded-sm text-center outline-hidden hover:cursor-pointer"
		{onclick}
		class:flex
		class:justify-center={flex}
	>
		{@render children?.()}
	</a>
{:else}
	<button
		{disabled}
		{type}
		class="text-black hover:cursor-pointer hover:opacity-80 w-full px-4 py-2 leading-5 transition-all duration-200 transform bg-[#B07156] rounded-sm text-center focus:outline-hidden disabled:cursor-not-allowed disabled:opacity-50 outline-hidden"
		{onclick}
		class:flex
		class:justify-center={flex}
	>
		{@render children?.()}
	</button>
{/if}
