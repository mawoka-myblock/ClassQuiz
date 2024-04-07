<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData, Question } from '../quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { reach } from 'yup';
	import { ABCDQuestionSchema, dataSchema } from '../yupSchemas';
	import { createTippy } from 'svelte-tippy';
	import { getLocalization } from '$lib/i18n';
	import AddNewQuestionPopup from '$lib/editor/AddNewQuestionPopup.svelte';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { fade } from 'svelte/transition';

	const { t } = getLocalization();

	export let data: EditorData;
	export let selected_question = -1;

	let reorder_mode = false;

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'right'
	});
	let arr_of_cards = Array(data.questions.length);
	let propertyCard;
	let add_new_question_popup_open = false;

	const empy_slide: Question = {
		type: QuizQuestionType.SLIDE,
		time: '120',
		question: 'Slide',
		image: undefined,
		answers: ''
	};

	const swapArrayElements = (arr, a: number, b: number) => {
		let _arr = [...arr];
		let temp = _arr[a];
		_arr[a] = _arr[b];
		_arr[b] = temp;
		return _arr;
	};

	const setSelectedQuestion = (index: number): void => {
		if (reorder_mode) {
			return;
		}
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

<div class="h-screen relative">
	<div class="h-10 flex justify-center w-full p-1 absolute z-20">
		<div>
			<BrownButton on:click={() => (reorder_mode = !reorder_mode)}
				>{#if reorder_mode}{$t('editor.disable_reorder')}{:else}{$t(
						'editor.enable_reorder'
					)}{/if}</BrownButton
			>
		</div>
	</div>
	<div class="border-r-2 pt-6 px-6 overflow-scroll h-full">
		<div
			bind:this={propertyCard}
			class="bg-white shadow rounded-lg h-40 p-2 mb-6 hover:cursor-pointer drop-shadow-2xl border border-gray-500 dark:bg-gray-600 transition"
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
				<p
					type="text"
					class="whitespace-nowrap truncate text-center w-full bg-transparent rounded dark:text-white"
					class:dark:text-black={selected_question === -1}
				>
					{#if data.title}
						{@html data.title}
					{:else}
						<i>{$t('editor.no_title')}</i>
					{/if}
				</p>
			</div>
			<div
				use:tippy={{ content: data.description === '' ? "It's empty!" : data.description }}
				class="m-1 border border-gray-500 rounded-lg p-0.5 transition"
				class:border-red-600={!reach(dataSchema, 'description').isValidSync(
					data.description
				)}
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
						<span>{$t('words.public')}</span>
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
						<span>{$t('words.private')}</span>
					{/if}
				</button>
			</div>
		</div>
		{#each data.questions as question, index}
			<div
				class="bg-white shadow rounded-lg h-40 p-2 mb-6 hover:cursor-pointer drop-shadow-2xl border border-gray-500 dark:bg-gray-600 transition relative"
				class:bg-green-300={index === selected_question}
				class:dark:bg-green-500={index === selected_question}
				on:click={() => {
					setSelectedQuestion(index);
				}}
				bind:this={arr_of_cards[index]}
			>
				{#if reorder_mode}
					<div
						transition:fade={{ duration: 90 }}
						class="absolute z-10 grid grid-cols-2 bg-transparent w-full rounded h-full"
					>
						<!-- Div is used, since it just put me on the dashboard when using button elements... Idk why and I hate it-->
						<div
							class="h-full"
							role="button"
							aria-label="Move card up"
							class:opacity-50={index === 0}
							class:pointer-events-none={index === 0}
							on:click={() =>
								(data.questions = swapArrayElements(
									data.questions,
									index,
									index - 1
								))}
						>
							<!-- heroicons/new/ChevronUp --><svg
								data-slot="icon"
								aria-hidden="true"
								fill="none"
								stroke-width="1.5"
								stroke="currentColor"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="m4.5 15.75 7.5-7.5 7.5 7.5"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</div>
						<div
							class="h-full"
							role="button"
							aria-label="Move card down"
							class:opacity-50={index + 1 === data.questions.length}
							class:pointer-events-none={index + 1 === data.questions.length}
							on:click={() =>
								(data.questions = swapArrayElements(
									data.questions,
									index,
									index + 1
								))}
						>
							<!-- heroicons/new/ChevronDown -->
							<svg
								data-slot="icon"
								aria-hidden="true"
								fill="none"
								stroke-width="1.5"
								stroke="currentColor"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="m19.5 8.25-7.5 7.5-7.5-7.5"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</div>
					</div>
				{/if}
				<button
					class="rounded-full absolute -top-3 -right-3 opacity-70 hover:opacity-100 transition"
					type="button"
					on:click={() => {
						if (confirm('Do you really want to delete this Question?')) {
							selected_question = -1;
							data.questions.splice(index, 1);
							data.questions = data.questions;
						}
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
				<div
					use:tippy={{
						content: question.question === '' ? 'No title' : question.question
					}}
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
							<span class="italic text-gray-500">{$t('editor.no_title')}</span>
						{:else}
							{@html question.question}
						{/if}
					</h1>
				</div>
				{#if question.image}
					<div class="flex justify-center align-middle pb-0.5">
						<img
							src="/api/v1/storage/download/{question.image}"
							class="h-10 border rounded-lg"
							alt="Not available"
							use:tippy={{
								content: `<img src="/api/v1/storage/download/${question.image}" alt="Not available" class="rounded">`,
								allowHTML: true
							}}
						/>
					</div>
				{/if}

				{#if question.type === QuizQuestionType.ABCD || question.type === QuizQuestionType.CHECK}
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
										content:
											answer.answer === ''
												? $t('editor.empty')
												: answer.answer
									}}
									>{#if answer.answer === ''}
										<i>{$t('editor.empty')}</i>
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
				{:else if question.type === QuizQuestionType.VOTING || question.type === QuizQuestionType.TEXT}
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
										content:
											answer.answer === ''
												? $t('editor.empty')
												: answer.answer
									}}
									>{#if answer.answer === ''}
										<i>{$t('editor.empty')}</i>
									{:else}
										{answer.answer}
									{/if}</span
								>
							{/each}
						</div>
					{/if}
				{:else if question.type === QuizQuestionType.SLIDE}
					<p>Some smart information on a slide</p>
				{:else if question.type === QuizQuestionType.ORDER}
					<p>Get thing's into the right order!</p>
				{:else}
					<p>Unknown Question Type (shouldn't happen)</p>
				{/if}
			</div>
		{/each}
		<div
			class="bg-white shadow rounded-lg h-40 p-2 hover:cursor-pointer drop-shadow-2xl border border-gray-500 dark:bg-gray-600 grid grid-cols-2"
		>
			<button
				type="button"
				class="h-full flex justify-center w-full flex-col border-r border-black dark:text-white"
				on:click={() => {
					add_new_question_popup_open = true;
				}}
			>
				<span class="w-full text-center">{$t('words.question')}</span>
				<svg
					class="w-5/6 m-auto"
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
			<button
				type="button"
				class="h-full flex justify-center w-full dark:text-white flex-col"
				on:click={() => {
					data.questions = [...data.questions, { ...empy_slide }];
				}}
			>
				<span class="w-full text-center">{$t('words.slide')}</span>
				<svg
					class="w-5/6 m-auto"
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
</div>
{#if add_new_question_popup_open}
	<AddNewQuestionPopup
		bind:questions={data.questions}
		bind:open={add_new_question_popup_open}
		bind:selected_question
	/>
{/if}
