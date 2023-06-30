<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	let color_map = {
		r: 'red',
		g: 'green',
		y: 'yellow',
		b: 'blue'
	};
	export let code: string;
</script>

<div class="flex flex-row gap-2 mx-auto">
	{#each code as c}
		<div class="flex flex-col">
			<p class="text-center">{c}</p>
			<span
				style="background-color: {color_map[
					c.toLowerCase()
				]}; width: 2rem; height: {c.toLowerCase() == c ? '2' : '4'}rem"
			/>
		</div>
	{/each}
</div>
