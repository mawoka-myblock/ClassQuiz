<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->
<script lang="ts">
	import { page } from '$app/stores';
	import type { QuizData } from '$lib/quiz_types';
	import Spinner from '$lib/Spinner.svelte';
	import TitleScreen from '$lib/practice/title_screen.svelte';
	import Question from '$lib/practice/question.svelte';

	let quiz: QuizData;
	let unique = {};

	let selected_question = -1;

	const get_quiz = async () => {
		const res = await fetch(`/api/v1/quiz/get/public/${$page.url.searchParams.get('quiz_id')}`);
		if (!res.ok) {
			throw res.status;
		}
		quiz = await res.json();
		return quiz;
	};
	const reload_q = () => {
		unique = {};
	};
</script>

{#await get_quiz()}
	<Spinner />
{:then q}
	<div class="h-full overflow-hidden">
		{#if selected_question === -1}
			<TitleScreen bind:data={quiz} />
		{:else}
			{#key unique}
				<Question bind:question={quiz.questions[selected_question]} />
			{/key}
		{/if}

		<div class="grid grid-cols-2 h-fit px-20 mt-6 absolute bottom-0 w-full">
			<button
				class="flex justify-start transition-all disabled:opacity-60"
				disabled={selected_question <= -1}
				on:click={() => {
					selected_question -= 1;
				}}
			>
				<svg
					class="w-16 h-16"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 19l-7-7 7-7"
					/>
				</svg>
			</button>
			<button
				class="flex justify-end transition-all disabled:opacity-60"
				disabled={selected_question >= quiz.questions.length - 1}
				on:click={() => {
					reload_q();
					selected_question += 1;
				}}
			>
				<svg
					class="w-16 h-16"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 5l7 7-7 7"
					/>
				</svg>
			</button>
		</div>
	</div>
{:catch e}
	{#if e === 404 || e === 400}
		<h1 class="text-center text-5xl">Quiz not found!</h1>
	{:else}
		<h1 class="text-center text-5xl">unknown error!</h1>
	{/if}
{/await}
