<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';

	export let data;
	export let question: Question;

	let quiz_answers = [];
	let quiz_colors = [];

	for (const i of question.answers) {
		quiz_answers.push(i.answer);
		quiz_colors.push(i.color);
	}

	let sorted_data = {};
	for (const i of quiz_answers) {
		sorted_data[i] = 0;
	}
	for (const i of data) {
		sorted_data[i.answer] += 1;
	}
</script>

<div class="flex justify-center w-full">
	<div
		class="m-auto w-fit gap-4 flex flex-col"
		style="grid-template-columns: repeat({quiz_answers.length}, minmax(0, 1fr));"
	>
		<div class="flex gap-4">
			{#each quiz_answers as answer}
				<span class="text-center self-end mx-auto"
					>{#if sorted_data[answer] > 0}{sorted_data[answer]}{/if}</span
				>
			{/each}
		</div>
		<div class="flex gap-4">
			{#each quiz_answers as answer, i}
				<div
					class="w-20 self-end flex justify-center"
					style="height: {(sorted_data[answer] * 20) /
						data.length}rem; background-color: {quiz_colors[i]
						? quiz_colors[i]
						: 'black'}"
				/>
			{/each}
		</div>
		<div class="flex gap-4">
			{#each quiz_answers as answer}
				<div class="w-20">
					<p class="-rotate-45">{@html answer}</p>
				</div>
			{/each}
		</div>
	</div>
</div>
