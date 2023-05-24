<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { EditorData, Answer } from '../quiz_types';
	import { fade } from 'svelte/transition';
	import { reach } from 'yup';
	import { ABCDQuestionSchema } from '$lib/yupSchemas';
	import { getLocalization } from '$lib/i18n';
	import { get_foreground_color } from '$lib/helpers';

	const { t } = getLocalization();

	const default_colors = ['#D6EDC9', '#B07156', '#7F7057', '#4E6E58'];

	console.log(get_foreground_color(default_colors[0]));

	export let selected_question: number;
	export let data: EditorData;
	if (!Array.isArray(data.questions[selected_question].answers)) {
		data.questions[selected_question].answers = [];
	}
	const save_colors = (data_local: EditorData) => {
		if (selected_question === 0) {
			for (let i = 0; i < data_local.questions[selected_question].answers.length; i++) {
				localStorage.setItem(
					`quiz_color:${i}:${data_local.title}`,
					data_local.questions[selected_question].answers[i].color
				);
			}
		}
	};

	const get_empty_answer = (i: number): Answer => {
		return {
			answer: '',
			color: default_colors[i],
			right: false
		};
	};
	$: save_colors(data);
</script>

<div class="grid grid-rows-2 grid-flow-col auto-cols-auto gap-4 w-full px-10">
	{#if Array.isArray(data.questions[selected_question].answers)}
		{#each data.questions[selected_question].answers as answer, index}
			<div
				out:fade|local={{ duration: 150 }}
				class="p-4 rounded-lg flex justify-center w-full transition relative"
				class:bg-red-500={!answer.right}
				class:bg-green-500={answer.right}
				class:bg-yellow-500={!reach(ABCDQuestionSchema, 'answer').isValidSync(
					answer.answer
				)}
			>
				<button
					class="rounded-full absolute -top-2 -right-2 opacity-70 hover:opacity-100 transition"
					type="button"
					on:click={() => {
						data.questions[selected_question].answers.splice(index, 1);
						data.questions[selected_question].answers =
							data.questions[selected_question].answers;
					}}
				>
					<svg
						class="w-6 h-6 bg-red-500 rounded-full"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</button>
				<input
					bind:value={answer.answer}
					type="text"
					class="border-b-2 border-dotted w-5/6 text-center rounded-lg bg-transparent"
					style="background-color: {answer.color}; color: {get_foreground_color(
						answer.color
					)}"
					placeholder={$t('editor.empty')}
				/>
				<button
					type="button"
					on:click={() => {
						answer.right = !answer.right;
						console.log(answer.right);
					}}
				>
					{#if answer.right}
						<svg
							class="w-6 h-6 inline-block"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					{:else}
						<svg
							class="w-6 h-6 inline-block"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					{/if}
				</button>
				<input
					class="rounded-lg p-1 border-black border"
					type="color"
					bind:value={answer.color}
					on:contextmenu|preventDefault={() => {
						answer.color = default_colors[index];
					}}
				/>
			</div>
		{/each}
	{/if}
	{#if data.questions[selected_question].answers.length < 4}
		<button
			class="p-4 rounded-lg bg-transparent border-gray-500 border-2 hover:bg-gray-300 transition dark:hover:bg-gray-600"
			type="button"
			in:fade|local={{ duration: 150 }}
			on:click={() => {
				data.questions[selected_question].answers = [
					...data.questions[selected_question].answers,
					{ ...get_empty_answer(data.questions[selected_question].answers.length) }
				];
			}}
		>
			<span class="italic text-center">{$t('editor_page.add_an_answer')}</span>
		</button>
	{/if}
</div>
