<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { socket } from '$lib/socket';
	import Spinner from '../Spinner.svelte';
	import { getLocalization } from '$lib/i18n';
	import { kahoot_icons } from './kahoot_mode_assets/kahoot_icons';
	import CircularTimer from '$lib/play/circular_progress.svelte';
	import { flip } from 'svelte/animate';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { get_foreground_color } from '../helpers';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';

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

	const select_complex_answer = (data) => {
		selected_answer = 'a';
		const new_array = [];
		for (let i = 0; i < data.length; i++) {
			new_array.push({ answer: data[i].answer });
		}
		socket.emit('submit_answer', {
			question_index: question_index,
			answer: 'a',
			complex_answer: new_array
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

	if (question.type === QuizQuestionType.ORDER) {
		for (let i = 0; i < question.answers.length; i++) {
			question.answers[i] = { ...question.answers[i], id: i };
		}
	}

	const swapArrayElements = (arr, a: number, b: number) => {
		let _arr = [...arr];
		let temp = _arr[a];
		_arr[a] = _arr[b];
		_arr[b] = temp;
		return _arr;
	};
	$: set_answer_if_not_set_range(timer_res);
	let circular_progress = 0;
	$: {
		try {
			circular_progress = 1 - ((100 / question.time) * parseInt(timer_res)) / 100;
		} catch {
			circular_progress = 0;
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
	const default_colors = ['#D6EDC9', '#B07156', '#7F7057', '#4E6E58'];
</script>

<div class="h-screen w-screen">
	{#if game_mode === 'normal'}
		<div
			class="flex flex-col justify-start"
			class:mt-10={[QuizQuestionType.RANGE, QuizQuestionType.ORDER, QuizQuestionType.TEXT]}
			style="height: {question.image ? '33.333333' : '16.666667'}%"
		>
			<h1
				class="lg:text-2xl text-lg text-center text-black dark:text-white mt-2 break-normal mb-2"
			>
				{@html question.question}
			</h1>
			{#if question.image !== null && game_mode !== 'kahoot'}
				<div class="max-h-full">
					<MediaComponent
						src={question.image}
						css_classes="object-cover mx-auto mb-8 max-h-[90%]"
					/>
				</div>
			{/if}
		</div>
	{/if}
	{#if timer_res !== '0'}
		{#if question.type === QuizQuestionType.ABCD || question.type === QuizQuestionType.VOTING}
			<div class="w-full relative h-full" style="height: {get_div_height()}%">
				<div
					class="absolute top-0 bottom-0 left-0 right-0 m-auto rounded-full h-fit w-fit border-2 border-black shadow-2xl z-40"
				>
					<CircularTimer
						bind:text={timer_res}
						bind:progress={circular_progress}
						color="#ef4444"
					/>
				</div>

				<div class="grid grid-rows-2 grid-flow-col auto-cols-auto gap-2 w-full p-4 h-full">
					{#each question.answers as answer, i}
						<button
							class="rounded-lg h-full flex align-middle justify-center disabled:opacity-60 p-3 border-2 border-black"
							style="background-color: {answer.color ??
								default_colors[i]}; color: {get_foreground_color(
								answer.color ?? default_colors[i]
							)}"
							disabled={selected_answer !== undefined}
							on:click={() => selectAnswer(answer.answer)}
						>
							{#if game_mode === 'kahoot'}
								<img
									class="h-2/3 inline-block m-auto"
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
			<span
				class="fixed top-0 bg-red-500 h-8 transition-all"
				style="width: {(100 / parseInt(question.time)) * parseInt(timer_res)}vw"
			/>
			{#await import('svelte-range-slider-pips')}
				<Spinner />
			{:then c}
				<div class:pointer-events-none={selected_answer !== undefined} class="mt-24">
					<svelte:component
						this={c.default}
						bind:values={slider_value}
						bind:min={question.answers.min}
						bind:max={question.answers.max}
						id="pips-slider"
						pips
						float
						all="label"
					/>
				</div>
				<div class="flex justify-center">
					<div class="w-1/2">
						<BrownButton
							disabled={selected_answer !== undefined}
							on:click={() => selectAnswer(slider_value[0])}
							>{$t('words.submit')}
						</BrownButton>
					</div>
				</div>
			{/await}
		{:else if question.type === QuizQuestionType.TEXT}
			<div>
				<span
					class="fixed top-0 bg-red-500 h-8 transition-all"
					style="width: {(100 / parseInt(question.time)) * parseInt(timer_res)}vw"
				/>
				<div class="flex justify-center mt-10">
					<p class="text-black dark:text-white">Enter your answer</p>
				</div>
				<div class="flex justify-center m-2">
					<input
						type="text"
						bind:value={text_input}
						disabled={selected_answer}
						class="bg-gray-50 focus:ring text-gray-900 rounded-lg focus:ring-blue-500 block w-full p-2 dark:bg-gray-700 dark:text-white dark:focus:ring-blue-500 outline-none transition text-center disabled:opacity-50 disabled:cursor-not-allowed"
					/>
				</div>

				<div class="flex justify-center mt-2">
					<div class="w-1/3">
						<BrownButton
							type="button"
							disabled={selected_answer}
							on:click={() => {
								selectAnswer(text_input);
							}}
						>
							{$t('words.submit')}
						</BrownButton>
					</div>
				</div>
			</div>
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
		{:else if question.type === QuizQuestionType.ORDER}
			<!--			{#if solution === undefined}
                            <Spinner />
                        {:else}-->
			<span
				class="fixed top-0 bg-red-500 h-8 transition-all"
				style="width: {(100 / parseInt(question.time)) * parseInt(timer_res)}vw"
			/>
			<div class="flex flex-col w-full h-full gap-4 px-4 py-6 mt-10">
				{#each question.answers as answer, i (answer.id)}
					<div
						class="w-full h-fit flex-row rounded-lg p-2 align-middle"
						animate:flip={{ duration: 100 }}
						style="background-color: {answer.color ?? '#b07156'}"
					>
						<button
							on:click={() => {
								question.answers = swapArrayElements(question.answers, i, i - 1);
							}}
							class="disabled:opacity-50 transition shadow-lg bg-black bg-opacity-30 w-full flex justify-center rounded-lg p-2 hover:bg-opacity-20 transition"
							type="button"
							disabled={i === 0 || selected_answer}
						>
							<svg
								class="w-8 h-8"
								stroke-width="2"
								viewBox="0 0 24 24"
								fill="none"
								xmlns="http://www.w3.org/2000/svg"
								color="currentColor"
							>
								<path
									d="M12 22a2 2 0 110-4 2 2 0 010 4zM12 15V2m0 0l3 3m-3-3L9 5"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</button>
						<p class="w-full text-center p-2 text-2xl">{answer.answer}</p>

						<button
							on:click={() => {
								question.answers = swapArrayElements(question.answers, i, i + 1);
							}}
							class="disabled:opacity-50 transition shadow-lg bg-black bg-opacity-30 w-full flex justify-center rounded-lg p-2 hover:bg-opacity-20 transition"
							type="button"
							disabled={i === question.answers.length - 1 || selected_answer}
						>
							<svg
								class="w-8 h-8"
								stroke-width="2"
								viewBox="0 0 24 24"
								fill="none"
								xmlns="http://www.w3.org/2000/svg"
								color="currentColor"
							>
								<path
									d="M12 6a2 2 0 110-4 2 2 0 010 4zM12 9v13m0 0l3-3m-3 3l-3-3"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</button>
					</div>
				{/each}
				<div class="w-full mt-2">
					<BrownButton
						type="button"
						disabled={selected_answer}
						on:click={() => {
							select_complex_answer(question.answers);
						}}>{$t('words.submit')}</BrownButton
					>
				</div>
			</div>
			<!--{/if}-->
		{:else if question.type === QuizQuestionType.CHECK}
			{#await import('./questions/check.svelte')}
				<Spinner />
			{:then c}
				<svelte:component
					this={c.default}
					bind:question
					bind:selected_answer
					bind:game_mode
					{timer_res}
					{circular_progress}
				/>
				<div class="flex justify-center h-[5%]">
					<div class="w-1/2">
						<BrownButton
							disabled={!selected_answer}
							on:click={() => selectAnswer(selected_answer)}
							>{$t('words.submit')}
						</BrownButton>
					</div>
				</div>
			{/await}
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
