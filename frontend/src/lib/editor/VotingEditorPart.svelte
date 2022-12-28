<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { EditorData, VotingAnswer } from '../quiz_types';
	import { fade } from 'svelte/transition';
	import { reach } from 'yup';
	import { getLocalization } from '$lib/i18n';
	import { VotingQuestionSchema } from '$lib/yupSchemas';

	const { t } = getLocalization();

	const empty_answer: VotingAnswer = {
		answer: '',
		image: undefined
	};
	export let selected_question: number;
	export let data: EditorData;

	if (!Array.isArray(data.questions[selected_question].answers)) {
		data.questions[selected_question].answers = [];
	}
	try {
		if (typeof data.questions[selected_question].answers[0].right === 'boolean') {
			data.questions[selected_question].answers = [];
		}
		// eslint-disable-next-line no-empty
	} catch {}

	/*console.log(data.questions[selected_question].answers, 'moIn!', data.questions[selected_question].answers.length);
	onMount(() => {
		for (let i = 0; i < data.questions[selected_question].answers; i++) {
			console.log(data.questions[selected_question].answers[i], 'iterate');
			data.questions[selected_question].answers[i].right = undefined;
		}
	});*/
</script>

<div class="grid grid-cols-2 gap-4 w-full px-10">
	{#if Array.isArray(data.questions[selected_question].answers)}
		{#each data.questions[selected_question].answers as answer, index}
			<div
				out:fade={{ duration: 150 }}
				class="p-4 rounded-lg flex justify-center w-full transition relative"
				class:bg-yellow-500={!reach(VotingQuestionSchema, 'answer').isValidSync(
					answer.answer
				)}
				class:dark:bg-gray-500={answer.answer}
				class:bg-gray-300={answer.answer}
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
					class="border-b-2 border-dotted w-5/6 text-center rounded-lg"
					style="background-color: {answer.color ?? 'transparent'}"
					placeholder="Empty..."
				/>
				<input
					class="rounded-lg p-1 border-black border"
					type="color"
					bind:value={answer.color}
					on:contextmenu|preventDefault={() => {
						answer.color = null;
					}}
				/>
			</div>
		{/each}
	{/if}
	{#if data.questions[selected_question].answers.length < 4}
		<button
			class="p-4 rounded-lg bg-transparent border-gray-500 border-2 hover:bg-gray-300 transition dark:hover:bg-gray-600"
			type="button"
			in:fade={{ duration: 150 }}
			on:click={() => {
				data.questions[selected_question].answers = [
					...data.questions[selected_question].answers,
					{ ...empty_answer }
				];
			}}
		>
			<span class="italic text-center">{$t('editor_page.add_an_answer')}</span>
		</button>
	{/if}
</div>
