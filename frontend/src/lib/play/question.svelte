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
	export let solution;

	$: console.log(question_index, question, 'hi!');

	console.log(question);
	if (question.type === undefined) {
		question.type = QuizQuestionType.ABCD;
	} else {
		question.type = QuizQuestionType[question.type];
	}

	/*	if (typeof question_index === 'string') {
			question_index = parseInt(question_index);
		} else {
			throw new Error('question_index must be a string or number');
		}*/

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
	socket.on('everyone_answered', (_) => {
		timer_res = '0';
	});

	timer(question.time);

	$: {
		if (solution !== undefined) {
			timer_res = '0';
		}
	}

	const selectAnswer = (answer: string) => {
		selected_answer = answer;
		//timer_res = '0';
		socket.emit('submit_answer', {
			question_index: question_index,
			answer: answer
		});
	};

	let text_input = '';

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
		} catch {
			circular_prgoress = 0;
		}
	}

	const get_div_height = (): string => {
		if (game_mode === 'normal') {
			if (question.image) {
				return '66.666667';
			} else {
				return '83.333333';
			}
		} else {
			return '100';
		}
	};
	$: console.log(slider_value, 'values');
</script>

<div class="h-screen w-screen">
	{#if game_mode === 'normal'}
		<div
			class="flex flex-col justify-start w-screen"
			style="height: {question.image ? '33.333333' : '16.666667'}%"
		>
			<h1 class="text-3xl text-center text-black dark:text-white mt-2">
				{@html question.question}
			</h1>
			{#if question.image !== null && game_mode !== 'kahoot'}
				<div class="max-h-full">
					<img
						src={question.image}
						class="object-cover mx-auto mb-8 max-h-[90%]"
						alt="Content for Question"
					/>
				</div>
			{/if}
		</div>
	{/if}
	{#if timer_res !== '0'}
		{#if question.type === QuizQuestionType.ABCD || question.type === QuizQuestionType.VOTING}
			<div class="w-full relative" style="height: {get_div_height()}%">
				<div
					class="absolute top-0 bottom-0 left-0 right-0 m-auto rounded-full h-fit w-fit border-2 border-black shadow-2xl"
				>
					<CircularTimer
						bind:text={timer_res}
						bind:progress={circular_prgoress}
						color="#ef4444"
					/>
				</div>

				<div class="grid grid-cols-2 gap-2 w-full p-4 h-full">
					{#each question.answers as answer, i}
						<button
							class="rounded-lg h-full flex align-middle justify-center disabled:opacity-60 p-3"
							style="background-color: {answer.color ?? '#B45309'}"
							disabled={selected_answer !== undefined}
							on:click={() => selectAnswer(answer.answer)}
						>
							{#if game_mode === 'kahoot'}
								<img
									class="w-10 inline-block m-auto"
									alt="Icon"
									src={kahoot_icons[i]}
								/>
							{:else}
								<p class="m-auto">{answer.answer}</p>
							{/if}
						</button>
					{/each}
				</div>
			</div>
		{:else if question.type === QuizQuestionType.RANGE}
			{#await import('svelte-range-slider-pips')}
				<Spinner />
			{:then c}
				<div class:pointer-events-none={selected_answer !== undefined} class="mt-14">
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
						class="w-1/2 text-3xl bg-[#B07156] my-2 disabled:opacity-60 border border-white"
						disabled={selected_answer !== undefined}
						on:click={() => selectAnswer(slider_value[0])}
						>{$t('words.submit')}
					</button>
				</div>
			{/await}
		{:else if question.type === QuizQuestionType.TEXT}
			<div class="flex justify-center">
				<p class="text-black dark:text-white">Enter your answer</p>
			</div>
			<div class="flex justify-center m-2">
				<input
					type="text"
					bind:value={text_input}
					class="bg-gray-50 focus:ring text-gray-900 rounded-lg focus:ring-blue-500 block w-full p-2 dark:bg-gray-700 dark:text-white dark:focus:ring-blue-500 outline-none transition text-center"
				/>
			</div>

			<div class="flex justify-center">
				<button
					class="bg-[#B07156] hover:bg-amber-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed mt-2"
					type="button"
					disabled={!text_input}
					on:click={() => {
						selectAnswer(text_input);
					}}
				>
					{$t('words.submit')}
				</button>
			</div>
		{/if}
	{:else if question.type === QuizQuestionType.ABCD}
		{#if solution === undefined}
			<Spinner />
		{:else}
			<div class="grid grid-cols-2 gap-2 w-full p-4">
				{#each solution.answers as answer}
					{#if answer.right}
						<button
							class="text-3xl rounded-lg h-fit flex align-middle justify-center p-3 bg-green-600"
							disabled
							class:opacity-30={answer.answer !== selected_answer}
							>{answer.answer}</button
						>
					{:else}
						<button
							class="text-3xl rounded-lg h-fit flex align-middle justify-center p-3 bg-red-500"
							disabled
							class:opacity-30={answer.answer !== selected_answer}
							>{answer.answer}</button
						>
					{/if}
				{/each}
			</div>
		{/if}
	{:else if question.type === QuizQuestionType.RANGE}
		{#if solution === undefined}
			<Spinner />
		{:else}
			<p class="text-center">
				Every number between {solution.answers.min_correct} and {solution.answers
					.max_correct} was correct. You got {selected_answer}, so you have been
				{#if solution.answers.min_correct <= parseInt(selected_answer) && parseInt(selected_answer) <= solution.answers.max_correct}
					correct
				{:else}
					wrong.
				{/if}
			</p>
		{/if}
		<!--{:else if question.type === QuizQuestionType.VOTING}
	{#await import('$lib/play/admin/voting_results.svelte')}
		<Spinner />
	{:then c}
		<svelte:component this={c.default} bind:data={question_results}
						  bind:question={quiz_data.questions[selected_question]} />
	{/await}-->
	{/if}
</div>
