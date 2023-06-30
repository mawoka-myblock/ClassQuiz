<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { fly } from 'svelte/transition';
	import QuestionTab from './question_tab_thing.svelte';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	export let questions: Question[];
	export let answers: {
		username: string;
		answer: string;
		right: boolean;
		tike_taken: number;
		score: number;
	}[][];

	const get_average_score = (q_index: number): number => {
		const q_answers = answers[q_index];
		let summed_up_scores = 0;
		for (const answer of q_answers) {
			summed_up_scores = summed_up_scores + answer.score;
		}
		return summed_up_scores / q_answers.length;
	};

	const get_number_of_correct_answers = (q_index: number): number => {
		const q_answers = answers[q_index];
		let correct_answer = 0;
		for (const answer of q_answers) {
			if (answer.right) {
				correct_answer++;
			}
		}
		return correct_answer;
	};

	const toggle_dropdown = (q_index: number) => {
		if (question_open === q_index) {
			question_open = false;
		} else {
			question_open = q_index;
		}
	};
	let question_open: number | boolean = false;
</script>

<div class="w-full flex justify-center">
	<div class="w-11/12 flex flex-col w-full gap-4">
		{#each questions as question, i}
			<div class="transition-all">
				<div
					class="w-full bg-white p-2 rounded grid grid-cols-3 z-40 dark:bg-gray-700 bg-opacity-60 dark:bg-opacity-80"
				>
					<button
						class="text-center underline text-xl"
						on:click={() => {
							toggle_dropdown(i);
						}}>{@html question.question}</button
					>
					{#if question.type !== QuizQuestionType.VOTING}
						{@const correct_answers = get_number_of_correct_answers(i)}
						<p class="text-center text-sm my-auto">
							{$t('result_page.average_score', {
								average_score: get_average_score(i)
							})}
						</p>
						<p class="text-center text-sm my-auto">
							{$t('result_page.correct_answer', { count: correct_answers })}
							<!--							{correct_answers} correct
							{#if correct_answers === 1}Answer{:else}Answers{/if}-->
						</p>
					{/if}
				</div>
				{#if question_open === i}
					<div in:fly|local={{ y: -10 }}>
						<QuestionTab {question} answers={answers[i]} />
					</div>
				{/if}
			</div>
		{/each}
	</div>
</div>
