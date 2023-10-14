<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { fade } from 'svelte/transition';
	import type { EditorData, TextQuizAnswer } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import { reach } from 'yup';
	import { TextQuestionSchema } from '$lib/yupSchemas';
	import { createTippy } from 'svelte-tippy';

	export let selected_question: number;
	export let data: EditorData;

	const { t } = getLocalization();

	if (!Array.isArray(data.questions[selected_question].answers)) {
		data.questions[selected_question].answers = [];
	}

	for (let i = 0; i < data.questions[selected_question].answers.length; i++) {
		data.questions[selected_question].answers[i] = {
			answer: data.questions[selected_question].answers[i].answer,
			case_sensitive: false
		};
	}

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle'
	});

	const get_empty_answer = (): TextQuizAnswer => {
		return {
			answer: '',
			case_sensitive: false
		};
	};
</script>

<div class="grid grid-cols-2 gap-4 w-full px-10">
	{#if Array.isArray(data.questions[selected_question].answers)}
		{#each data.questions[selected_question].answers as answer, index}
			<div
				out:fade|local={{ duration: 150 }}
				class="p-4 rounded-lg flex justify-center w-full transition relative"
				class:dark:bg-gray-500={answer.answer}
				class:bg-gray-300={answer.answer}
				class:bg-yellow-500={!reach(TextQuestionSchema, 'answer').isValidSync(
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
					class="border-b-2 border-dotted w-5/6 text-center rounded-lg bg-transparent outline-none"
					placeholder={$t('editor.enter_answer')}
				/>
				<button
					type="button"
					on:click={() => {
						answer.case_sensitive = !answer.case_sensitive;
					}}
					use:tippy={{ content: 'Case sensitive?', placement: 'top' }}
				>
					{#if answer.case_sensitive}
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
					{ ...get_empty_answer() }
				];
			}}
		>
			<span class="italic text-center">{$t('editor_page.add_an_answer')}</span>
		</button>
	{/if}
</div>
