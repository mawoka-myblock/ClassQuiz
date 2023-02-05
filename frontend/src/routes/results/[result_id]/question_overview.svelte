<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import { fly } from 'svelte/transition';
	import QuestionTab from './question_tab_thing.svelte';

	export let quiz: QuizData;
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
	<div class="w-11/12 flex flex-col w-full">
		{#each quiz.questions as question, i}
			<div>
				<div class="w-full bg-white bg-opacity-60 p-2 rounded grid grid-cols-3 z-40">
					<button
						class="text-center underline text-xl"
						on:click={() => {
							toggle_dropdown(i);
						}}>{question.question}</button
					>
					<p class="text-center text-sm my-auto">Average Score: {get_average_score(i)}</p>
					<p class="text-center text-sm my-auto">
						{get_number_of_correct_answers(i)} correct Answer(s)
					</p>
				</div>
				{#if question_open === i}
					<div transition:fly={{ y: -10 }}>
						<QuestionTab {question} answers={answers[i]} />
					</div>
				{/if}
			</div>
		{/each}
	</div>
</div>
