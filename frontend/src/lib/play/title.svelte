<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	export let title: string;
	export let description: string;
	export let cover_image: string | undefined;
</script>

<div class="flex flex-col justify-center w-screen h-screen">
	<h1 class="text-7xl text-center">{@html title}</h1>
	<p class="text-3xl pt-8 text-center">{@html description}</p>
	{#if cover_image}
		<div class="flex justify-center align-middle items-center">
			<div class="h-[30vh] m-auto w-auto mt-12">
				<img class="max-h-full max-w-full  block" src={cover_image} alt="Not provided" />
			</div>
		</div>
	{/if}
</div>
