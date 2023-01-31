<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
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
		class="text-black hover:bg-opacity-80 w-full px-4 py-2 leading-5 text-black transition-all duration-200 transform bg-[#B07156] rounded text-center focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 outline-none"
		on:click
		class:flex
		class:justify-center={flex}
	>
		<slot />
	</a>
{:else}
	<button
		{disabled}
		class="text-black hover:opacity-80 w-full px-4 py-2 leading-5 text-black transition-all duration-200 transform bg-[#B07156] rounded text-center focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 outline-none"
		on:click
		class:flex
		class:justify-center={flex}
	>
		<slot />
	</button>
{/if}
