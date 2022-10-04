<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { fly } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';
	import { QuizQuestionType } from '$lib/quiz_types';
	import Spinner from '$lib/Spinner.svelte';

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

	timer(question.time);
</script>

<div class="w-full px-6 lg:px-20 h-[80vh] absolute" in:fly={{ x: 100 }} out:fly={{ x: -100 }}>
	<h1 class="text-3xl text-center">{question.question}</h1>
	{#if question.image !== null}
		<div>
			<img
				src={question.image}
				class="max-h-[40vh] object-cover mx-auto mb-8 w-auto"
				alt="Content for Question"
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
						class="w-1/2 text-3xl bg-amber-700 my-2 disabled:opacity-60 border border-white"
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
	{/if}
</div>
