<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { EditorData, Question } from '../quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { reach } from 'yup';
	import { ABCDQuestionSchema, dataSchema } from '../yupSchemas';
	import { createTippy } from 'svelte-tippy';

	export let data: EditorData;
	export let selected_question = -1;

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'right'
	});
	let arr_of_cards = Array(data.questions.length);
	let propertyCard;
	const empty_question: Question = {
		question: '',
		time: '20',
		image: '',
		answers: [],
		type: QuizQuestionType.ABCD
	};

	const setSelectedQuestion = (index: number): void => {
		selected_question = index;
		if (index === -1) {
			propertyCard.scrollIntoView({
				behavior: 'smooth'
			});
		} else {
			arr_of_cards[index].scrollIntoView({
				behavior: 'smooth'
			});
		}
	};
	/*	onMount(() => {
			propertyCard.scrollIntoView({
				behavior: 'smooth'
			});
		});*/
</script>

<div class="h-screen border-r-2 pt-6 px-6 overflow-scroll">
	<div
		class="bg-white shadow rounded-lg h-40 p-2 mb-6 hover:cursor-pointer drop-shadow-2xl border border-gray-500 dark:bg-gray-600 transition"
		bind:this={propertyCard}
		class:bg-green-300={selected_question === -1}
		class:dark:bg-green-500={selected_question === -1}
		on:click={() => setSelectedQuestion(-1)}
	>
		<div
			use:tippy={{ content: data.title === '' ? "It's empty!" : data.title }}
			class="m-1 border border-gray-500 rounded-lg p-0.5 transition"
			class:border-red-600={!reach(dataSchema, 'title').isValidSync(data.title)}
			class:border-solid={!reach(dataSchema, 'title').isValidSync(data.title)}
			class:border-2={!reach(dataSchema, 'title').isValidSync(data.title)}
		>
			<input
				type="text"
				class="whitespace-nowrap truncate text-center w-full bg-transparent rounded font-semibold dark:text-white"
				class:dark:text-black={selected_question === -1}
				bind:value={data.title}
			/>
		</div>
		<div
			use:tippy={{ content: data.description === '' ? "It's empty!" : data.description }}
			class="m-1 border border-gray-500 rounded-lg p-0.5 transition"
			class:border-red-600={!reach(dataSchema, 'description').isValidSync(data.description)}
			class:border-solid={!reach(dataSchema, 'description').isValidSync(data.description)}
			class:border-2={!reach(dataSchema, 'description').isValidSync(data.description)}
		>
			<textarea
				bind:value={data.description}
				class="bg-transparent resize-none w-full rounded text-sm dark:text-white"
				class:dark:text-black={selected_question === -1}
			/>
		</div>
		<div
			class="w-full flex justify-center dark:text-white"
			class:dark:text-black={selected_question === -1}
		>
			<button
				type="button"
				on:click={() => {
					data.public = !data.public;
				}}
				class="text-center"
			>
				{#if data.public}
					<svg
						class="w-5 h-5 inline-block"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					<span>Public</span>
				{:else}
					<svg
						class="w-5 h-5 inline-block"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
						/>
					</svg>
					<span>Private</span>
				{/if}
			</button>
		</div>
	</div>
	{#each data.questions as question, index}
		<div
			class="bg-white shadow rounded-lg h-40 p-2 mb-6 hover:cursor-pointer drop-shadow-2xl border border-gray-500 dark:bg-gray-600 transition"
			class:bg-green-300={index === selected_question}
			class:dark:bg-green-500={index === selected_question}
			on:contextmenu|preventDefault={() => {
				if (confirm('Do you really want to delete this Question?')) {
					selected_question = selected_question - 1;
					data.questions.splice(index, 1);
					data.questions = data.questions;
				}
			}}
			on:click={() => {
				setSelectedQuestion(index);
			}}
			bind:this={arr_of_cards[index]}
		>
			<div
				use:tippy={{ content: question.question === '' ? 'No title' : question.question }}
				class="m-1 border border-gray-500 rounded-lg p-0.5"
			>
				<h1
					class="whitespace-nowrap truncate text-center rounded-lg dark:text-white transition"
					class:bg-yellow-500={!reach(dataSchema, 'questions[].question').isValidSync(
						question.question
					)}
					class:dark:text-black={index === selected_question}
				>
					{#if question.question === ''}
						<span class="italic text-gray-500">No title...</span>
					{:else}
						{question.question}
					{/if}
				</h1>
			</div>
			{#if question.image}
				<div class="flex justify-center align-middle pb-0.5">
					<img
						src={question.image}
						class="h-10 border rounded-lg"
						alt="Not available"
						use:tippy={{
							content: `<img src='${question.image}' alt='Not available' class='rounded'>`,
							allowHTML: true
						}}
					/>
				</div>
			{/if}
			{#if question.type === QuizQuestionType.ABCD}
				<div class="grid grid-cols-2 gap-2">
					{#if Array.isArray(question.answers)}
						{#each question.answers as answer}
							<span
								class="whitespace-nowrap truncate rounded-lg p-0.5 text-sm text-center border border-gray-700"
								class:bg-green-500={answer.right}
								class:bg-red-500={!answer.right}
								class:bg-yellow-500={!reach(
									ABCDQuestionSchema,
									'answer'
								).isValidSync(answer.answer)}
								use:tippy={{
									content: answer.answer === '' ? 'Empty...' : answer.answer
								}}
								>{#if answer.answer === ''}
									<i>Empty...</i>
								{:else}
									{answer.answer}
								{/if}</span
							>
						{/each}
					{/if}
				</div>
			{:else if question.type === QuizQuestionType.RANGE}
				<p class="text-center text-sm p-0.5">
					All numbers between {question.answers.min_correct}
					and {question.answers.max_correct} are correct, where numbers between {question
						.answers.min} and {question.answers.max} can be selected.
				</p>
			{:else if question.type === QuizQuestionType.VOTING}
				{#if Array.isArray(question.answers)}
					<div class="grid grid-cols-2 gap-2">
						{#each question.answers as answer}
							<span
								class="whitespace-nowrap truncate rounded-lg p-0.5 text-sm text-center border border-gray-700"
								class:dark:bg-gray-500={answer.answer}
								class:bg-gray-300={answer.answer}
								class:bg-yellow-500={!reach(
									ABCDQuestionSchema,
									'answer'
								).isValidSync(answer.answer)}
								use:tippy={{
									content: answer.answer === '' ? 'Empty...' : answer.answer
								}}
								>{#if answer.answer === ''}
									<i>Empty...</i>
								{:else}
									{answer.answer}
								{/if}</span
							>
						{/each}
					</div>
				{/if}
			{:else}
				<p>Unknown Question Type (shouldn't happen)</p>
			{/if}
		</div>
	{/each}
	<div
		class="bg-white shadow rounded-lg h-40 p-2 mb-6 hover:cursor-pointer drop-shadow-2xl border border-gray-500 dark:bg-gray-600"
	>
		<button
			type="button"
			class="h-full flex justify-center w-full dark:text-black"
			on:click={() => {
				data.questions = [...data.questions, { ...empty_question }];
			}}
		>
			<svg
				class="h-full"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 6v6m0 0v6m0-6h6m-6 0H6"
				/>
			</svg>
		</button>
	</div>
</div>
