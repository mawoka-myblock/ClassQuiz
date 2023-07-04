<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { OrderQuizAnswer, Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { fly } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';
	import Spinner from '$lib/Spinner.svelte';
	import { flip } from 'svelte/animate';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';

	export let question: Question;

	const { t } = getLocalization();

	let selected_answer = undefined;
	let timer_res = question.time;
	let show_results = false;

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
	let slider_value = [0];
	if (question.type === QuizQuestionType.RANGE) {
		slider_value[0] = (question.answers.max - question.answers.min) / 2 + question.answers.min;
	}
	let slider_values = [question.answers.min_correct ?? 0, question.answers.max_correct ?? 0];

	let text_input;
	timer(question.time);

	let check_choice_selected = [false, false, false, false];

	function shuffleArray(a) {
		for (let i = a.length - 1; i > 0; i--) {
			const j = Math.floor(Math.random() * (i + 1));
			[a[i], a[j]] = [a[j], a[i]];
		}
		return a;
	}

	const swapArrayElements = (arr, a: number, b: number) => {
		let _arr = [...arr];
		let temp = _arr[a];
		_arr[a] = _arr[b];
		_arr[b] = temp;
		return _arr;
	};

	let original_order: OrderQuizAnswer[] = [];

	if (question.type === QuizQuestionType.ORDER) {
		for (let i = 0; i < question.answers.length; i++) {
			question.answers[i] = { answer: question.answers[i].answer, id: i };
		}
		original_order = [...question.answers];
		console.log(original_order);
		shuffleArray(question.answers);
	}

	let order_corrected = false;
	const select_complex_answer = () => {
		/*		const correct_order_ids = []
                for (const e of original_order) {
                    correct_order_ids.push(e.id)
                }
                const user_set_ids = []
                for (const e of answer) {
                    correct_order_ids.push(e.id)
                }*/
		question.answers = original_order;
		order_corrected = true;
		timer_res = '0';
	};
</script>

<div class="w-full px-6 lg:px-20 h-[80vh] absolute" in:fly={{ x: 100 }} out:fly={{ x: -100 }}>
	<h1 class="text-3xl text-center">{@html question.question}</h1>
	{#if question.image !== null}
		<div>
			<MediaComponent
				src={question.image}
				css_classes="max-h-[40vh] object-cover mx-auto mb-8 w-auto"
			/>
		</div>
	{/if}
	<p class="text-center">{timer_res}</p>
	{#if question.type === QuizQuestionType.ABCD}
		{#if show_results}
			<div>
				{#each question.answers as answer, i}
					<button
						disabled
						class:bg-green-500={question.answers[i].right}
						class:bg-red-500={!question.answers[i].right}
						class:text-xl={i === selected_answer}
						class:underline={i === selected_answer}
						class="p-2 rounded-lg flex justify-center w-full transition my-5 text-black"
						>{answer.answer}</button
					>
				{/each}
			</div>
		{:else}
			<div>
				{#each question.answers as answer, i}
					<button
						disabled={selected_answer !== undefined || timer_res === '0'}
						type="button"
						class="p-2 rounded-lg flex justify-center w-full transition bg-amber-300 my-5 disabled:grayscale text-black"
						on:click={() => {
							selected_answer = i;
							timer_res = '0';
						}}>{answer.answer}</button
					>
				{/each}
				{#if timer_res === '0'}
					<button
						class="bg-orange-500 p-2 rounded-lg flex justify-center w-full transition my-5 text-black"
						type="button"
						on:click={() => {
							show_results = true;
						}}>{$t('admin_page.get_results')}</button
					>
				{/if}
			</div>
		{/if}
	{:else if question.type === QuizQuestionType.RANGE}
		{#if timer_res === '0'}
			{#await import('svelte-range-slider-pips')}
				<Spinner />
			{:then c}
				<div class="grayscale pointer-events-none w-full">
					<svelte:component
						this={c.default}
						bind:values={slider_values}
						bind:min={question.answers.min}
						bind:max={question.answers.max}
						pips
						float
						all="label"
					/>
				</div>
			{/await}
		{:else}
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
						type="button"
						class="w-1/3 text-3xl bg-[#B07156] my-2 disabled:opacity-60 rounded-lg p-1 transition"
						disabled={selected_answer !== undefined}
						on:click={() => {
							selected_answer = slider_value[0];
							timer_res = '0';
						}}
						>{$t('words.submit')}
					</button>
				</div>
			{/await}
		{/if}
	{:else if question.type === QuizQuestionType.VOTING}
		{#each question.answers as answer, i}
			<button
				type="button"
				disabled={selected_answer !== undefined || timer_res === '0'}
				class="p-2 rounded-lg flex justify-center w-full transition bg-amber-300 my-5 disabled:grayscale text-black"
				on:click={() => {
					selected_answer = i;
					timer_res = '0';
				}}>{answer.answer}</button
			>
		{/each}
		{#if timer_res === '0'}
			<p>No correct answers, since this is a poll-question</p>
		{/if}
	{:else if question.type === QuizQuestionType.SLIDE}
		{#await import('$lib/play/admin/slide.svelte')}
			<Spinner my={false} />
		{:then c}
			<div class="max-h-[90%] max-w-[90%]">
				<svelte:component this={c.default} bind:question />
			</div>
		{/await}
	{:else if question.type === QuizQuestionType.TEXT}
		{#if timer_res === '0'}
			{#each question.answers as answer, i}
				<div
					class="p-2 rounded-lg flex justify-center w-full transition bg-gray-200 my-5 text-black"
				>
					{answer.answer}
				</div>
			{/each}
		{:else}
			<div class="flex justify-center mt-2">
				<input
					type="text"
					bind:value={text_input}
					class="bg-gray-50 focus:ring text-gray-900 rounded-lg focus:ring-blue-500 block w-full p-2 dark:bg-gray-700 dark:text-white dark:focus:ring-blue-500 outline-none transition text-center"
				/>
			</div>
			<div class="flex justify-center">
				<button
					type="button"
					disabled={!text_input}
					class="w-1/3 text-3xl bg-[#B07156] my-2 disabled:opacity-60 rounded-lg p-1 transition"
					on:click={() => {
						selected_answer = text_input;
						timer_res = '0';
					}}>{$t('words.submit')}</button
				>
			</div>
		{/if}
	{:else if question.type === QuizQuestionType.ORDER}
		<div class="flex flex-col w-full h-full gap-4 px-4 py-6">
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
						disabled={i === 0 || order_corrected}
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
						disabled={i === question.answers.length - 1 || order_corrected}
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
			<button
				class="bg-[#B07156] hover:bg-amber-700 text-white font-bold py-2 px-4 rounded-lg mt-2 transition w-full"
				type="button"
				disabled={timer_res === '0'}
				on:click={() => {
					select_complex_answer();
				}}
			>
				{$t('words.submit')}
			</button>
		</div>
	{:else if question.type === QuizQuestionType.CHECK}
		{#if show_results}
			<div>
				{#each question.answers as answer, i}
					<button
						type="button"
						disabled
						class:bg-green-500={question.answers[i].right}
						class:bg-red-500={!question.answers[i].right}
						class="p-2 rounded-lg flex justify-center w-full transition my-5 text-black"
						>{answer.answer}</button
					>
				{/each}
			</div>
		{:else}
			<div>
				{#each question.answers as answer, i}
					<button
						type="button"
						disabled={selected_answer !== undefined || timer_res === '0'}
						class="p-2 rounded-lg flex justify-center w-full transition bg-amber-300 my-5 disabled:grayscale text-black opacity-50"
						class:opacity-100={check_choice_selected[i]}
						on:click={() => {
							check_choice_selected[i] = !check_choice_selected[i];
						}}>{answer.answer}</button
					>
				{/each}
				<BrownButton
					type="button"
					on:click={() => {
						timer_res = '0';
					}}>{$t('words.submit')}</BrownButton
				>
				{#if timer_res === '0'}
					<button
						type="button"
						class="bg-orange-500 p-2 rounded-lg flex justify-center w-full transition my-5 text-black"
						on:click={() => {
							show_results = true;
						}}>{$t('admin_page.get_results')}</button
					>
				{/if}
			</div>
		{/if}
	{/if}
</div>
