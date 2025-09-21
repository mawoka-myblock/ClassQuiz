<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Abcd } from '$lib/quiztivity/types';

	interface Props {
		data: Abcd | undefined;
	}

	let { data }: Props = $props();

	let selected_answer: number | undefined = $state();

	const select_answer = (i: number) => {
		selected_answer = i;
		console.log(data);
	};
</script>

<div>
	<h1 class="text-center text-4xl">{data.question}</h1>

	<div class="grid grid-cols-1 lg:grid-cols-2 m-4 gap-4">
		{#each data.answers as answer, i}
			<button
				class="rounded-sm p-6 bg-gray-700 flex transition-all"
				onclick={() => {
					select_answer(i);
				}}
				class:opacity-50={selected_answer !== undefined && !answer.correct}
				class:text-2xl={selected_answer === i}
			>
				<span class="m-auto text-white">{answer.answer}</span>
			</button>
		{/each}
	</div>
</div>
