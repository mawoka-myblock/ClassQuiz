<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { socket } from '$lib/socket';
	import Spinner from '../Spinner.svelte';
	import { getLocalization } from '$lib/i18n';
	import { kahoot_icons } from './kahoot_mode_assets/kahoot_icons';
	import CircularTimer from '$lib/play/circular_progress.svelte';

	const { t } = getLocalization();

	export let question: Question;
	export let game_mode;
	export let question_index: string | number;

	if (typeof question_index === 'string') {
		question_index = parseInt(question_index);
	} else {
		throw new Error('question_index must be a string or number');
	}

	let timer_res = question.time;
	let selected_answer: string;

	// Stop the timer if the question is answered
	const timer = (time: string) => {
		let seconds = Number(time);
		let timer_interval = setInterval(() => {
			if (timer_res === '0') {
				clearInterval(timer_interval);
				return;
			} else {
				seconds--;
			}

			timer_res = seconds.toString();
		}, 1000);
	};

	timer(question.time);

	const selectAnswer = (answer: string) => {
		selected_answer = answer;
		//timer_res = '0';
		socket.emit('submit_answer', {
			question_index: question_index,
			answer: answer
		});
	};

	let slider_value = [0];
	if (question.type === QuizQuestionType.RANGE) {
		slider_value[0] = (question.answers.max - question.answers.min) / 2 + question.answers.min;
	}
	const set_answer_if_not_set_range = (time) => {
		if (question.type !== QuizQuestionType.RANGE) {
			return;
		}
		if (selected_answer === undefined && time === '0') {
			selected_answer = `${slider_value[0]}`;
			selectAnswer(selected_answer);
		}
	};
	$: set_answer_if_not_set_range(timer_res);
	let circular_prgoress = 0;
	$: {
		try {
			circular_prgoress = 1 - ((100 / question.time) * parseInt(timer_res)) / 100;
		} catch {}
	}
</script>

<div class="flex flex-col justify-center w-screen h-1/6">
	<h1 class="text-6xl text-center">
		{question.question}
	</h1>
	<div class="mx-auto my-2">
		<CircularTimer bind:text={timer_res} bind:progress={circular_prgoress} color="#ef4444" />
	</div>
</div>
{#if question.image !== null}
	<div>
		<img
			src={question.image}
			class="h-2/5 object-cover mx-auto mb-8"
			alt="Content for Question"
		/>
	</div>
{/if}
{#if timer_res !== '0'}
	{#if question.type === QuizQuestionType.ABCD}
		{#if game_mode === 'normal'}
			<div class="flex flex-wrap">
				{#each question.answers as answer}
					<button
						class="w-1/2 text-3xl my-2 disabled:opacity-60 border border-white"
						style="background-color: {answer.color ?? '#B45309'}"
						disabled={selected_answer !== undefined}
						on:click={() => selectAnswer(answer.answer)}>{answer.answer}</button
					>
				{/each}
			</div>
		{:else if game_mode === 'kahoot'}
			<div class="grid grid-cols-2 gap-2 w-full p-4">
				{#each question.answers as answer, i}
					<button
						class="rounded-lg h-fit flex align-middle justify-center disabled:opacity-60 p-3"
						style="background-color: {answer.color ?? '#B45309'}"
						disabled={selected_answer !== undefined}
						on:click={() => selectAnswer(answer.answer)}
					>
						<img class="w-10 inline-block" alt="Icon" src={kahoot_icons[i]} />
					</button>
				{/each}
			</div>
		{:else}
			<p>Error</p>
		{/if}
	{:else if question.type === QuizQuestionType.RANGE}
		{#await import('svelte-range-slider-pips')}
			<Spinner />
		{:then c}
			<div class:pointer-events-none={selected_answer !== undefined}>
				<svelte:component
					this={c.default}
					bind:values={slider_value}
					bind:min={question.answers.min}
					bind:max={question.answers.max}
					pips
					float
					all="label"
				/>
			</div>
			<div class="flex justify-center">
				<button
					class="w-1/2 text-3xl bg-amber-700 my-2 disabled:opacity-60 border border-white"
					disabled={selected_answer !== undefined}
					on:click={() => selectAnswer(slider_value[0])}
					>{$t('words.submit')}
				</button>
			</div>
		{/await}
	{/if}
{:else if question.type === QuizQuestionType.ABCD}
	<div class="flex flex-wrap">
		{#each question.answers as answer}
			{#if answer.right}
				<button
					class="w-1/2 text-3xl bg-green-600 border border-white"
					disabled
					class:opacity-30={answer.answer !== selected_answer}>{answer.answer}</button
				>
			{:else}
				<button
					class="w-1/2 text-3xl bg-red-500 border border-white"
					disabled
					class:opacity-30={answer.answer !== selected_answer}>{answer.answer}</button
				>
			{/if}
		{/each}
	</div>
{:else if question.type === QuizQuestionType.RANGE}
	<p class="text-center">
		Every number between {question.answers.min_correct} and {question.answers.max_correct} was correct.
		You got {selected_answer}, so you have been
		{#if question.answers.min_correct <= parseInt(selected_answer) && parseInt(selected_answer) <= question.answers.max_correct}
			correct
		{:else}
			wrong.
		{/if}
	</p>
{/if}
