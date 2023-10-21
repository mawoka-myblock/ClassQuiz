<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { get_foreground_color } from '$lib/helpers';
	import { kahoot_icons } from '$lib/play/kahoot_mode_assets/kahoot_icons';
	import CircularTimer from '$lib/play/circular_progress.svelte';
	// import CircularTimer from '$lib/play/circular_progress.svelte';
	const default_colors = ['#D6EDC9', '#B07156', '#7F7057', '#4E6E58'];
	export let question: Question;
	export let selected_answer = '';
	export let game_mode;

	export let timer_res;

	export let circular_progress;
	let _selected_answers = [false, false, false, false];

	const selectAnswer = (i: number) => {
		_selected_answers[i] = !_selected_answers[i];
		selected_answer = '';
		for (let i = 0; i < _selected_answers.length; i++) {
			if (_selected_answers[i]) {
				selected_answer += String(i);
			}
		}
		selected_answer = selected_answer;
		console.log(_selected_answers, selected_answer);
	};
</script>

<div class="w-full h-[95%]">
	<!--
        <div
            class="absolute top-0 bottom-0 left-0 right-0 m-auto rounded-full h-fit w-fit border-2 border-black shadow-2xl z-50"
        >
            <CircularTimer
                bind:text={timer_res}
                bind:progress={circular_prgoress}
                color="#ef4444"
            />
        </div>
    -->
	<div
		class="absolute top-0 bottom-0 left-0 right-0 m-auto rounded-full h-fit w-fit border-2 border-black shadow-2xl z-40"
	>
		<CircularTimer bind:text={timer_res} bind:progress={circular_progress} color="#ef4444" />
	</div>

	<div class="grid grid-rows-2 grid-flow-col auto-cols-auto gap-2 w-full p-4 h-full">
		{#each question.answers as answer, i}
			<button
				class="rounded-lg h-full flex align-middle justify-center disabled:opacity-60 p-3 border-2 border-black transition-all"
				style="background-color: {answer.color ??
					default_colors[i]}; color: {get_foreground_color(
					answer.color ?? default_colors[i]
				)}"
				on:click={() => selectAnswer(i)}
				class:opacity-100={_selected_answers[i]}
				class:opacity-50={!_selected_answers[i]}
			>
				{#if game_mode === 'kahoot'}
					<img class="h-2/3 inline-block m-auto" alt="Icon" src={kahoot_icons[i]} />
				{:else}
					<p class="m-auto">{answer.answer}</p>
				{/if}
			</button>
		{/each}
	</div>
</div>
