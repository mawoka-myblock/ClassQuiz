<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import VotingResults from './voting_results.svelte';
	import { flip } from 'svelte/animate';
	import { fly } from 'svelte/transition';
	import { onMount } from 'svelte';
	import { getLocalization } from '$lib/i18n';
	import type { Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';

	const { t } = getLocalization();

	interface Props {
		data: any;
		question: Question;
		new_data: Array<{
			username: string;
			answer: string;
			right: boolean;
			time_taken: number;
			score: number;
		}>;
	}

	let { data = $bindable(), question, new_data }: Props = $props();

	function sortObjectbyValue(obj: object) {
		const ret = {};
		Object.keys(obj)
			.sort((a, b) => obj[b] - obj[a])
			.forEach((s) => (ret[s] = obj[s]));
		return ret;
	}

	let sorted_data = $derived(sortObjectbyValue(data));

	// let data_by_username = {};

	const group_username_by_score = (new_d: any[]): object => {
		let ret_data = {};
		for (const i of new_data) {
			ret_data[i.username] = i.score;
		}
		return ret_data;
	};
	let score_by_username = $derived(group_username_by_score(new_data));

	let player_names = $derived(Object.keys(sorted_data));

	if (JSON.stringify(data) === '{}') {
		for (const i of new_data) {
			data[i.username] = 0;
		}
	}

	let show_new_score_clicked = $state(false);

	const show_new_score = () => {
		for (const i of player_names) {
			if (isNaN(data[i])) {
				data[i] = 0;
			}
			console.log(score_by_username[i], '1');
			data[i] = (score_by_username[i] ?? 0) + data[i];
		}
		for (const i of new_data) {
			if (!data[i.username]) {
				data[i.username] = score_by_username[i.username];
			}
		}
		show_new_score_clicked = true;
		setTimeout(() => {
			data = data;
		}, 800);
	};

	onMount(() => {
		setTimeout(show_new_score, 1000);
	});

	// https://svelte.dev/repl/96a58afdea2248a5b7e489160ffba887?version=3.44.2
</script>

<div class="h-full flex flex-col">
	<div class="flex justify-center">
		<div>
			<table class="table-auto text-xl">
				<thead>
					<tr>
						<th class="p-2 border-r border-r-black border-b-2 border-b-black"
							>{$t('words.name')}</th
						>
						<th class="p-2 border-b-2 border-b-black"
							>{$t('words.point', { count: 2 })}</th
						>
						{#if show_new_score_clicked}
							<th in:fly|global={{ x: 300 }} class="p-2 border-b-2 border-b-black"
								>{$t('play_page.points_added')}
							</th>
						{/if}
					</tr>
				</thead>
				<tbody>
					{#each player_names as player, i (player)}
						<tr animate:flip>
							<td class:hidden={i > 3} class="p-2 border-r border-r-black"
								>{player}</td
							>
							<td class:hidden={i > 3} class="p-2">{sorted_data[player]}</td>
							{#if show_new_score_clicked}
								<td
									in:fly|global={{ x: 300 }}
									class:hidden={i > 3}
									class="p-2"
									class:text-red-600={score_by_username[player] === 0 ||
										score_by_username[player] === undefined}
								>
									+{score_by_username[player] ?? '0'}
								</td>
							{/if}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
	{#if [QuizQuestionType.ABCD, QuizQuestionType.VOTING, QuizQuestionType.TEXT].includes(question.type)}
		<div class="mt-12">
			<VotingResults data={new_data} {question} />
		</div>
	{/if}
</div>
