<script lang="ts">
	import type { EditorData, Answer } from '$lib/quiz_types';
	import CheckerBg from '$lib/editor/checker-bg.svg';
	import { reach } from 'yup';
	import { dataSchema } from '$lib/yupSchemas';
	import Spinner from '../Spinner.svelte';
	import { fade } from 'svelte/transition';

	export let data: EditorData;
	export let selected_question: number;
	export let edit_id: string;

	let question = data.questions[selected_question];
	$: question = data.questions[selected_question];
	const empty_answer: Answer = {
		right: false,
		answer: ''
	};
	console.log(question.image);
	let uppyOpen = false;
	$: console.log(uppyOpen);
</script>

<div class="w-full h-full pb-20 px-20">
	<div class="rounded-lg bg-white w-full h-full border-gray-500 drop-shadow-2xl dark:bg-gray-700">
		<div class="h-fit bg-gray-300 rounded-t-lg dark:bg-gray-500">
			<div class="flex align-middle p-4 gap-3">
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-red-400 transition"
				/>
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-yellow-400 transition"
				/>
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-green-400 transition"
				/>
			</div>
		</div>
		<div class="flex flex-col">
			<div class="flex justify-center pt-10 w-full">
				<input
					type="text"
					bind:value={question.question}
					placeholder="No title..."
					class="p-3 rounded-lg border-gray-500 border text-center w-2/3 text-lg font-semibold placeholder:italic placeholder:font-normal dark:bg-gray-500"
					class:bg-yellow-500={!reach(dataSchema, 'questions[].question').isValidSync(
						question.question
					)}
				/>
			</div>
			{#if question.image != undefined && question.image !== ''}
				<div class="flex justify-center pt-10 w-full max-h-72 w-full">
					<img
						src={question.image}
						alt="not available"
						class="max-h-72 h-auto w-auto"
						on:contextmenu|preventDefault={() => {
							question.image = '';
						}}
					/>
				</div>
			{:else}
				{#await import('$lib/editor/uploader.svelte')}
					<Spinner />
				{:then c}
					<svelte:component
						this={c.default}
						bind:modalOpen={uppyOpen}
						bind:edit_id
						bind:data
						bind:selected_question
					/>
				{/await}
			{/if}
			<div class="flex justify-center pt-10 w-full">
				<div class="grid grid-cols-2 gap-4 w-full px-10">
					{#each question.answers as answer, index}
						<div
							on:contextmenu|preventDefault={() => {
								question.answers.splice(index, 1);
								question.answers = question.answers;
							}}
							out:fade={{ duration: 150 }}
							class="p-4 rounded-lg flex justify-center w-full transition"
							class:bg-red-500={!answer.right}
							class:bg-green-500={answer.right}
							class:bg-yellow-500={!reach(
								dataSchema,
								'questions[].answers[].answer'
							).isValidSync(answer.answer)}
						>
							<input
								bind:value={answer.answer}
								type="text"
								class="bg-transparent border-b-2 border-dotted w-5/6 text-center"
								placeholder="Empty..."
							/>
							<button
								type="button"
								on:click={() => {
									answer.right = !answer.right;
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
						</div>
					{/each}
					{#if question.answers.length < 4}
						<button
							class="p-4 rounded-lg bg-transparent border-gray-500 border-2 hover:bg-gray-300 transition dark:hover:bg-gray-600"
							type="button"
							in:fade={{ duration: 150 }}
							on:click={() => {
								question.answers = [...question.answers, { empty_answer }];
							}}
						>
							<span class="italic text-center">Add an answer</span>
						</button>
					{/if}
				</div>
			</div>
			<p class="italic text-center mt-auto pt-4">Right-click on an answer to delete it!</p>
		</div>
	</div>
</div>
