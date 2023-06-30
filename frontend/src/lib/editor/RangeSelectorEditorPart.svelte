<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData } from '../quiz_types';
	import Spinner from '../Spinner.svelte';

	export let selected_question: number;
	export let data: EditorData;

	let question = data.questions[selected_question];
	if (question.answers.max === undefined || question.answers.min_correct === undefined) {
		question.answers = {
			max: 10,
			min: 0,
			max_correct: 7,
			min_correct: 3
		};
	}

	/*
	const correct_numbers = (data: number[]) => {
		console.log(data, data[1] <= data[0])
		if (data[1] <= data[0]) {
			range_arr[1] = range_arr[0] + 2
		}
		if (data[0] <= data[1]) {
			range_arr[0] = range_arr[1] - 2
		}
	}
	$: correct_numbers(range_arr)

 */
	let answer = question.answers;
	let range_arr = [answer.min_correct, answer.max_correct];
	$: data.questions[selected_question].answers.min_correct = range_arr[0];
	$: data.questions[selected_question].answers.max_correct = range_arr[1];
	$: data.questions[selected_question].answers.min =
		data.questions[selected_question].answers.min === null
			? 0
			: data.questions[selected_question].answers.min;
	$: data.questions[selected_question].answers.max =
		data.questions[selected_question].answers.max === null
			? 0
			: data.questions[selected_question].answers.max;

	function sleep(ms) {
		return new Promise((resolve) => setTimeout(resolve, ms));
	}
</script>

<div class="w-full mx-8">
	<div class="flex justify-center">
		<div class="grid grid-cols-2 gap-4">
			<input
				type="number"
				class="w-16 bg-transparent rounded-lg text-lg border-2 border-gray-500 p-1"
				max={data.questions[selected_question].answers.max - 2}
				bind:value={data.questions[selected_question].answers.min}
			/>
			<input
				type="number"
				class="w-16 bg-transparent rounded-lg text-lg border-2 border-gray-500 p-1"
				min={data.questions[selected_question].answers.min + 2}
				bind:value={data.questions[selected_question].answers.max}
			/>
		</div>
	</div>
	<div class="w-full">
		<!--		<RangeSlider bind:value={range_arr} bind:min={answer.min} bind:max={answer.max} range={true} slider={lol} /> -->

		{#await import('svelte-range-slider-pips')}
			<Spinner my_20={false} />
		{:then c}
			{#await sleep(100)}
				<Spinner my_20={false} />
			{:then _}
				<svelte:component
					this={c.default}
					bind:values={range_arr}
					bind:min={data.questions[selected_question].answers.min}
					bind:max={data.questions[selected_question].answers.max}
					pips
					float
					all="label"
					range
				/>
			{/await}
		{/await}
	</div>
</div>
