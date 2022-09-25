<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import { flip } from 'svelte/animate';
	import { fly } from 'svelte/transition';
	import { onMount } from 'svelte';

	export let data;

	export let new_data: Array<{
		username: string;
		answer: string;
		right: boolean;
		time_taken: number;
		score: number;
	}>;

	function sortObjectbyValue(obj) {
		const ret = {};
		Object.keys(obj)
			.sort((a, b) => obj[b] - obj[a])
			.forEach((s) => (ret[s] = obj[s]));
		return ret;
	}

	// let data_by_username = {};
	let score_by_username = {};

	for (const i of new_data) {
		/*		data_by_username[i.username] = {
			answer: i.answer,
			right: i.right,
			time_taken: i.time_taken,
			score: i.score
		};*/
		score_by_username[i.username] = i.score;
	}

	let player_names;

	if (JSON.stringify(data) === '{}') {
		for (const i of new_data) {
			data[i.username] = 0;
		}
	}

	$: data = sortObjectbyValue(data);
	$: player_names = Object.keys(data);

	let show_new_score_clicked = false;

	const show_new_score = () => {
		// for (let i = 0; i++; i < player_names.length) {
		// console.log(data)
		for (const i of player_names) {
			data[i] = score_by_username[i] + data[i];
		}
		show_new_score_clicked = true;
		setTimeout(() => {
			data = data;
		}, 800);

		// console.log(data)
	};

	onMount(() => {
		setTimeout(show_new_score, 1000);
	});

	// https://svelte.dev/repl/96a58afdea2248a5b7e489160ffba887?version=3.44.2
</script>

<main>
	<button on:click={show_new_score}>Show new Score</button>
	<div class="flex justify-center">
		<div>
			<table class="table-auto text-xl">
				<tr>
					<th class="p-2 border-r border-r-black border-b-2 border-b-black">Name</th>
					<th class="p-2 border-b-2 border-b-black">Points</th>
					{#if show_new_score_clicked}
						<th in:fly={{ x: 300 }} class="p-2 border-b-2 border-b-black"
							>Points added</th
						>
					{/if}
				</tr>
				{#each player_names as player, i (player)}
					<tr animate:flip>
						<td class:hidden={i > 3} class="p-2 border-r border-r-black">{player}</td>
						<td class:hidden={i > 3} class="p-2">{data[player]}</td>
						{#if show_new_score_clicked}
							<td
								in:fly={{ x: 300 }}
								class:hidden={i > 3}
								class="p-2"
								class:text-red-600={score_by_username[player] === 0}
							>
								+{score_by_username[player]}
							</td>
						{/if}
					</tr>
				{/each}
			</table>
		</div>
	</div>
</main>
