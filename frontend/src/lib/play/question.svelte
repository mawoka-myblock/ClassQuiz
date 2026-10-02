<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { ANSWER_COLORS } from '$lib/play/answer_colors';
	import Check from '@lucide/svelte/icons/check';
	import Clock from '@lucide/svelte/icons/clock';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { socket } from '$lib/socket';
	import Spinner from '../Spinner.svelte';
	import { getLocalization } from '$lib/i18n';
	import AnswerShape from './kahoot_mode_assets/AnswerShape.svelte';
	import CircularTimer from '$lib/play/circular_progress.svelte';
	import { flip } from 'svelte/animate';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { get_foreground_color } from '../helpers';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { sanitizeTitleHtml } from '$lib/sanitize';
	import { onDestroy } from 'svelte';
	import X from '@lucide/svelte/icons/x';

	const { t } = getLocalization();

	interface Props {
		question: Question;
		game_mode: any;
		question_index: string | number;
		solution: any;
	}

	let {
		question = $bindable(),
		game_mode = $bindable(),
		question_index,
		solution
	}: Props = $props();

	if (question.type === undefined) {
		question.type = QuizQuestionType.ABCD;
	} else {
		question.type = QuizQuestionType[question.type];
	}

	let timer_res = $state(question.time);
	let selected_answer: string = $state();

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
	// The server can refuse an answer, and used to do it in silence: `question_not_active`
	// and `already_replied` had no listener anywhere in the frontend. The screen sets
	// `selected_answer` the moment a tile is tapped, so a refused answer still read
	// "Answer locked in" and the player only found out from a +0 on the results screen.
	//
	// `refused` is the honest version of that: the answer did not count and the question
	// is over. It is deliberately not a retry prompt -- by the time this arrives the
	// timer has run out or the host has revealed the answers, so there is nothing to
	// tap. `already_replied` is not an error for the player: it means an earlier answer
	// of theirs was recorded, so "locked in" is already true and nothing should change.
	let refused = $state(false);

	const on_everyone_answered = () => {
		timer_res = '0';
	};
	const on_question_not_active = () => {
		// Only if this screen was claiming otherwise. A refusal for a question the player
		// never answered needs no correction -- they are already seeing "time is up".
		if (selected_answer !== undefined) {
			refused = true;
		}
		timer_res = '0';
	};

	socket.on('everyone_answered', on_everyone_answered);
	socket.on('question_not_active', on_question_not_active);
	// The play page recreates this component per question (`{#key unique}`), so a
	// listener added here and never removed accumulated one copy per question, each
	// holding a destroyed component's state alive and writing to it.
	onDestroy(() => {
		socket.off('everyone_answered', on_everyone_answered);
		socket.off('question_not_active', on_question_not_active);
	});

	timer(question.time);

	$effect(() => {
		if (solution !== undefined) {
			timer_res = '0';
		}
	});

	const selectAnswer = (answer: string) => {
		selected_answer = answer;
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

	let text_input = $state('');

	let slider_value = $state([0]);
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
	$effect(() => {
		set_answer_if_not_set_range(timer_res);
	});
	let circular_progress = $derived.by(() => {
		try {
			return 1 - ((100 / question.time) * parseInt(timer_res)) / 100;
		} catch {
			return 0;
		}
	});

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
	const default_colors = ANSWER_COLORS;
</script>

<div class="h-screen w-screen">
	{#if game_mode === 'normal'}
		<div
			class="flex flex-col justify-start"
			class:mt-10={[QuizQuestionType.RANGE, QuizQuestionType.ORDER, QuizQuestionType.TEXT]}
			style="height: {question.image ? '33.333333' : '16.666667'}%"
		>
			<h1
				class="lg:text-2xl text-lg text-center text-black dark:text-white mt-2 wrap-anywhere mb-2"
			>
				{@html sanitizeTitleHtml(question.question)}
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
					<CircularTimer text={timer_res} progress={circular_progress} color="#ef4444" />
				</div>

				<div class="grid grid-rows-2 grid-flow-col auto-cols-auto gap-3 w-full p-4 h-full">
					{#each question.answers as answer, i}
						{@const picked = selected_answer === answer.answer}
						{@const waiting = selected_answer !== undefined && !picked}
						<button
							class="answer-tile group relative overflow-hidden rounded-2xl h-full
								flex items-center justify-center
								transition-[transform,opacity,filter] duration-200 ease-out
								motion-safe:animate-in motion-safe:fade-in motion-safe:zoom-in-95
								focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-white/80
								not-disabled:active:scale-[0.96] not-disabled:hover:scale-[1.02]"
							class:is-picked={picked}
							class:is-waiting={waiting}
							style="background-color: {answer.color ??
								default_colors[i]}; color: {get_foreground_color(
								answer.color ?? default_colors[i]
							)}; animation-delay: {i * 70}ms"
							disabled={selected_answer !== undefined}
							aria-label={answer.answer}
							aria-pressed={picked}
							onclick={() => selectAnswer(answer.answer)}
						>
							<!-- Gloss and floor shading give the tile a pressable body rather
							     than a flat rectangle. Purely decorative. -->
							<span
								aria-hidden="true"
								class="pointer-events-none absolute inset-0 bg-gradient-to-b from-white/25 via-transparent to-black/15"
							></span>
							{#if game_mode === 'kahoot'}
								<AnswerShape
									index={i}
									class="relative h-1/2 max-h-24 w-auto drop-shadow-sm transition-transform duration-200 group-active:scale-90"
								/>
							{:else}
								<p
									class="relative m-auto text-lg font-semibold px-3 text-balance wrap-anywhere"
								>
									{answer.answer}
								</p>
							{/if}
							{#if picked}
								<span
									aria-hidden="true"
									class="absolute inset-0 ring-4 ring-inset ring-white rounded-2xl motion-safe:animate-in motion-safe:zoom-in-95"
								></span>
							{/if}
						</button>
					{/each}
				</div>
			</div>
		{:else if question.type === QuizQuestionType.RANGE}
			<span
				class="fixed top-0 bg-red-500 h-8 transition-all"
				style="width: {(100 / parseInt(question.time)) * parseInt(timer_res)}vw"
			></span>
			{#await import('svelte-range-slider-pips')}
				<Spinner />
			{:then c}
				<div class:pointer-events-none={selected_answer !== undefined} class="mt-24">
					<c.default
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
						<BrownButton onclick={() => selectAnswer(slider_value[0])}
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
				></span>
				<div class="flex justify-center mt-10">
					<p class="text-black dark:text-white">Enter your answer</p>
				</div>
				<div class="flex justify-center m-2">
					<input
						type="text"
						bind:value={text_input}
						disabled={selected_answer !== undefined}
						class="bg-gray-50 focus:ring text-gray-900 rounded-lg focus:ring-blue-500 block w-full p-2 dark:bg-gray-700 dark:text-white dark:focus:ring-blue-500 outline-hidden transition text-center disabled:opacity-50 disabled:cursor-not-allowed"
					/>
				</div>

				<div class="flex justify-center mt-2">
					<div class="w-1/3">
						<BrownButton
							type="button"
							disabled={!text_input || text_input.length === 0}
							onclick={() => {
								selectAnswer(text_input);
							}}
						>
							{$t('words.submit')}
						</BrownButton>
					</div>
				</div>
			</div>
		{:else if question.type === QuizQuestionType.ORDER}
			<!--			{#if solution === undefined}
                            <Spinner />
                        {:else}-->
			<span
				class="fixed top-0 bg-red-500 h-8 transition-all"
				style="width: {(100 / parseInt(question.time)) * parseInt(timer_res)}vw"
			></span>
			<div class="flex flex-col w-full h-full gap-4 px-4 py-6 mt-10">
				{#each question.answers as answer, i (answer.id)}
					<div
						class="w-full h-fit flex-row rounded-lg p-2 align-middle"
						animate:flip={{ duration: 100 }}
						style="background-color: {answer.color ?? '#b07156'}"
					>
						<button
							onclick={() => {
								question.answers = swapArrayElements(question.answers, i, i - 1);
							}}
							class="disabled:opacity-50 shadow-lg bg-black/30 w-full flex justify-center rounded-lg p-2 hover:bg-black/20 transition"
							type="button"
							aria-label="Move item up"
							disabled={i === 0 || Boolean(selected_answer)}
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
							onclick={() => {
								question.answers = swapArrayElements(question.answers, i, i + 1);
							}}
							class="disabled:opacity-50 shadow-lg bg-black/30 w-full flex justify-center rounded-lg p-2 hover:bg-black/20 transition"
							type="button"
							aria-label="Move item down"
							disabled={i === question.answers.length - 1 || Boolean(selected_answer)}
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
						disabled={Boolean(selected_answer)}
						onclick={() => {
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
				<c.default
					{question}
					bind:selected_answer
					{game_mode}
					{timer_res}
					{circular_progress}
				/>
				<div class="flex justify-center h-[5%]">
					<div class="w-1/2">
						<BrownButton
							type="button"
							disabled={selected_answer === undefined}
							onclick={() => selectAnswer(selected_answer)}
							>{$t('words.submit')}
						</BrownButton>
					</div>
				</div>
			{/await}
		{/if}
	{:else}
		{@const answered = selected_answer !== undefined}
		<!-- Time is up (or everyone has answered) but the results have not arrived yet.
		     Without this the player's screen went completely blank, giving no confirmation
		     that their answer was registered. The `answered` split matters: gating the whole
		     block on a submitted answer left anyone who ran out of time staring at nothing,
		     which is the worse case, because they cannot tell the app from a dead connection. -->
		<div class="flex h-full w-full items-center justify-center p-6">
			<div
				class="motion-safe:animate-in motion-safe:fade-in motion-safe:zoom-in-95 flex flex-col items-center gap-4 text-center"
			>
				<span
					class="bg-foreground/5 ring-border flex h-16 w-16 items-center justify-center rounded-full ring-1"
				>
					{#if refused}
						<X class="text-foreground/70 h-8 w-8" />
					{:else if answered}
						<Check class="text-foreground/70 h-8 w-8" />
					{:else}
						<Clock class="text-foreground/70 h-8 w-8" />
					{/if}
				</span>
				<div class="space-y-1">
					<p class="text-xl font-semibold tracking-tight">
						{#if refused}
							{$t('words.answer_too_late')}
						{:else if answered}
							{$t('words.answer_locked_in')}
						{:else}
							{$t('words.time_is_up')}
						{/if}
					</p>
					<p class="text-muted-foreground text-sm">{$t('words.waiting_for_results')}</p>
				</div>
				<span class="flex gap-1.5" aria-hidden="true">
					{#each [0, 1, 2] as d}
						<span
							class="waiting-dot bg-foreground/30 h-2 w-2 rounded-full"
							style="animation-delay: {d * 160}ms"
						></span>
					{/each}
				</span>
			</div>
		</div>
	{/if}
</div>

<style>
	.waiting-dot {
		animation: waiting-pulse 1.1s ease-in-out infinite;
	}

	@keyframes waiting-pulse {
		0%,
		100% {
			opacity: 0.25;
			transform: translateY(0);
		}
		50% {
			opacity: 0.9;
			transform: translateY(-3px);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.waiting-dot {
			animation: none;
		}
	}

	.answer-tile:disabled {
		cursor: default;
	}

	/* The chosen tile stays bright and lifts; the rest recede so a glance at the
	   phone shows what you picked without reading anything. */
	.answer-tile.is-picked {
		transform: scale(1.03);
	}

	.answer-tile.is-waiting {
		opacity: 0.45;
		filter: saturate(0.5);
		transform: scale(0.97);
	}
</style>
