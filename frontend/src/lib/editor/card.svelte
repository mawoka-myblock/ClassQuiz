<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { EditorData, Answer } from '$lib/quiz_types';
	import { reach } from 'yup';
	import { dataSchema } from '$lib/yupSchemas';
	import Spinner from '../Spinner.svelte';
	import { fade } from 'svelte/transition';
	import { mint } from '$lib/hashcash';
	import { createTippy } from 'svelte-tippy';
	import 'tippy.js/animations/perspective-subtle.css';
	import 'tippy.js/dist/tippy.css';

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'top'
	});

	export let data: EditorData;
	export let selected_question: number;
	export let edit_id: string;
	export let pow_data;
	let pow_salt: string;
	const empty_answer: Answer = {
		right: false,
		answer: ''
	};
	let uppyOpen = false;

	const computePOW = async (salt: string) => {
		if (pow_salt === undefined) {
			return;
		}
		console.log('Computing POW');
		pow_data = await mint(salt, 17, '', 8, false);
		pow_salt = undefined;
		return;
	};

	$: {
		pow_salt;
		computePOW(pow_salt);
	}

	/*eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }]*/
	const correctTimeInput = (_) => {
		let time = data.questions[selected_question].time;
		if (time === null || time === undefined) {
			data.questions[selected_question].time = '';
			time = '';
		}
		if (data.questions[selected_question].time > 3) {
			data.questions[selected_question].time = data.questions[selected_question].time
				.toString()
				.slice(0, 3);
		}
	};
	$: correctTimeInput(data.questions[selected_question].time);
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
					bind:value={data.questions[selected_question].question}
					placeholder="No title..."
					class="p-3 rounded-lg border-gray-500 border text-center w-2/3 text-lg font-semibold placeholder:italic placeholder:font-normal dark:bg-gray-500"
					class:bg-yellow-500={!reach(dataSchema, 'questions[].question').isValidSync(
						data.questions[selected_question].question
					)}
				/>
			</div>
			{#if data.questions[selected_question].image != undefined && data.questions[selected_question].image !== ''}
				<div class="flex justify-center pt-10 w-full max-h-72 w-full">
					<img
						src={data.questions[selected_question].image}
						alt="not available"
						class="max-h-72 h-auto w-auto"
						on:contextmenu|preventDefault={() => {
							data.questions[selected_question].image = '';
						}}
					/>
				</div>
			{:else if pow_data === undefined}
				<a
					href="/docs/pow"
					target="_blank"
					use:tippy={{ content: "Click to learn why it's loading so long." }}
					class="cursor-help"
				>
					<Spinner />
				</a>
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
						bind:pow_data
						bind:pow_salt
					/>
				{/await}
			{/if}
			<div class="flex justify-center pt-10 w-full">
				<div>
					<svg
						class="w-8 h-8 inline-block"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					<input
						type="number"
						max="999"
						min="1"
						class="w-20 bg-transparent rounded-lg text-lg border-2 border-gray-500 p-1"
						bind:value={data.questions[selected_question].time}
					/>
				</div>
			</div>

			<div class="flex justify-center pt-10 w-full">
				<div class="grid grid-cols-2 gap-4 w-full px-10">
					{#each data.questions[selected_question].answers as answer, index}
						<div
							on:contextmenu|preventDefault={() => {
								data.questions[selected_question].answers.splice(index, 1);
								data.questions[selected_question].answers =
									data.questions[selected_question].answers;
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
						</div>
					{/each}
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
							<span class="italic text-center">Add an answer</span>
						</button>
					{/if}
				</div>
			</div>
			<p class="italic text-center mt-auto pt-4">Right-click on an answer to delete it!</p>
		</div>
	</div>
</div>
