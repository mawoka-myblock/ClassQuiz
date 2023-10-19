<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	export let data;
	export let username;
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
					{$t('play_page.final_result_rank', {
						place: i + 1,
						username: player,
						points: data[player]
					})}
				</p>
			{/if}
		{/each}
	</div>
	{#if data[username]}
		<div class="fixed bottom-0 left-0 flex justify-center w-full mb-6">
			<div class="mx-auto p-2 border-[#B07156] border-4 rounded">
				<p class="text-center">{$t('play_page.your_score', { score: data[username] })}</p>
				{#each player_names as player, i}
					{#if player === username}
						<p class="text-center">{$t('play_page.your_place', { place: i + 1 })}</p>
					{/if}
				{/each}
			</div>
		</div>
	{/if}
{/if}
