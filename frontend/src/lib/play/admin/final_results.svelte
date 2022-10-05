<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import { onMount } from 'svelte';

	export let data;
	export let show_final_results: boolean;
	import { fly } from 'svelte/transition';
	import confetti from 'canvas-confetti';

	function sortObjectbyValue(obj) {
		const ret = {};
		Object.keys(obj)
			.sort((a, b) => obj[b] - obj[a])
			.forEach((s) => (ret[s] = obj[s]));
		return ret;
	}

	$: data = sortObjectbyValue(data);
	$: console.log(data, 'sorted, fina');

	let player_names;
	$: player_names = Object.keys(data).sort(function (a, b) {
		return data[b] - data[a];
	});

	let player_count_or_five;
	$: player_count_or_five = player_names.length >= 5 ? 5 : player_names.length;

	let canvas;
	onMount(() => {
		setTimeout(() => {
			confetti.create(canvas, {
				resize: true,
				useWorker: true
			});
			confetti({ particleCount: 200, spread: 160 });
		}, player_count_or_five * 1200 - 800);
	});
</script>

{#if show_final_results}
	<canvas bind:this={canvas} />
	<div>
		{#each player_names as player, i}
			{#if i <= player_count_or_five - 1}
				<p
					in:fly={{ y: -300, delay: player_count_or_five * 1200 - (i + 1) * 1000 }}
					style="font-size: {player_count_or_five - i / 2}rem"
					class="text-center"
				>
					{i + 1}
					: {player} with {data[player]} points
				</p>
			{/if}
		{/each}
	</div>
{/if}
