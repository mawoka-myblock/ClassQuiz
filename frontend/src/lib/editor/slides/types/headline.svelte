<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	export let data;
	export let editor = true;
</script>

{#if editor}
	<input
		bind:value={data}
		type="text"
		class="w-full h-full dark:text-black text-center text-3xl min-h-fit"
	/>
{:else}
	<h2 class="w-full h-full text-center text-3xl min-h-fit">
		{data}
	</h2>
{/if}
