<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import VotingResults from './voting_results.svelte';
	import { onMount } from 'svelte';
	import type { Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { sanitizeTitleHtml } from '$lib/sanitize';

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

	// let data_by_username = {};

	const group_username_by_score = (_new_d: any[]): object => {
		let ret_data = {};
		for (const i of new_data) {
			ret_data[i.username] = i.score;
		}
		return ret_data;
	};
	let score_by_username = $derived(group_username_by_score(new_data));

	let player_names = $derived(
		Object.keys(data).sort((a, b) => {
			const scoreA = parseFloat(data[a]) || 0;
			const scoreB = parseFloat(data[b]) || 0;
			return scoreB - scoreA;
		})
	);

	if (JSON.stringify(data) === '{}') {
		for (const i of new_data) {
			data[i.username] = 0;
		}
	}

	const show_new_score = () => {
		for (const i of player_names) {
			if (isNaN(data[i])) {
				data[i] = 0;
			}
			data[i] = (score_by_username[i] ?? 0) + data[i];
		}
		for (const i of new_data) {
			if (!data[i.username]) {
				data[i.username] = score_by_username[i.username];
			}
		}
	};

	onMount(() => {
		// This question's points land as soon as the answers are up, because the
		// scoreboard is the next screen and it reads these totals -- a host who advances
		// quickly used to arrive at standings that had not been added up yet. Still
		// cancelled on unmount: left running it would add the points after the host had
		// moved on, on top of the podium's rebuilt totals.
		const pending = setTimeout(show_new_score, 0);
		return () => clearTimeout(pending);
	});
</script>

<div class="fq-stage">
	<!-- What the answer was and how the room split. Where that leaves the standings is
	     the next screen (scoreboard.svelte), which the host advances into.
	     This card is a fixed light "paper" surface rather than the bg-card token --
	     it sits on the quiz author's own background colour, not the app's theme, so
	     in dark mode bg-card made it near-black with equally dark text, unreadable
	     regardless of what colour the game background happened to be. -->
	<div
		class="w-full max-w-2xl overflow-hidden rounded-2xl border border-neutral-200 bg-white text-neutral-900 shadow-sm lg:max-w-4xl"
	>
		{#if [QuizQuestionType.ABCD, QuizQuestionType.VOTING, QuizQuestionType.TEXT].includes(question.type)}
			<section class="flex flex-col gap-[var(--fq-space-group)] p-6 sm:p-8">
				<!-- This screen is read from the back of a room, not from a laptop: the question
				     screen before it sets its type at ~90px and this one was still at 18px. -->
				<h2
					class="text-center text-lg font-semibold tracking-tight text-balance lg:text-3xl"
				>
					{@html sanitizeTitleHtml(question.question)}
				</h2>
				<VotingResults data={new_data} {question} />
			</section>
		{/if}
	</div>
</div>
