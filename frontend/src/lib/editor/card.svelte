<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import RangeEditor from '$lib/editor/RangeSelectorEditorPart.svelte';
	import { reach } from 'yup';
	import { dataSchema } from '$lib/yupSchemas';
	import Spinner from '../Spinner.svelte';
	import { createTippy } from 'svelte-tippy';
	import { getLocalization } from '$lib/i18n';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { fade } from 'svelte/transition';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	// import MediaComponent from "$lib/editor/MediaComponent.svelte";

	const { t } = getLocalization();

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'top'
	});

	export let data: EditorData;
	export let selected_question: number;
	export let edit_id: string;

	let advanced_options_open = false;

	let uppyOpen = false;
	let unique = {};

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
	const set_unique = () => {
		unique = {};
	};
	$: correctTimeInput(data.questions[selected_question].time);
	$: {
		selected_question;
		set_unique();
	}
	let image_url = '';

	const update_image_url = () => {
		image_url = data.questions[selected_question].image;
	};
	$: {
		update_image_url();
		selected_question;
		data.questions;
	}

	const type_to_name = {
		RANGE: $t('words.range'),
		ABCD: $t('words.multiple_choice'),
		VOTING: $t('words.voting'),
		TEXT: $t('words.text'),
		ORDER: $t('words.order'),
		CHECK: $t('words.check_choice')
	};

	/*
    if (typeof data.questions[selected_question].type !== QuizQuestionType) {
        console.log(data.questions[selected_question].type !== QuizQuestionType.ABCD || data.questions[selected_question].type !== QuizQuestionType.RANGE)
        data.questions[selected_question].type = QuizQuestionType.ABCD;
    }
     */
</script>

<div class="w-full max-h-full pb-10 px-10 h-full">
	<div class="rounded-lg bg-white w-full h-full border-gray-500 dark:bg-gray-700 shadow-2xl">
		<div class="h-12 bg-gray-300 rounded-t-lg dark:bg-gray-500">
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
				<button
					class="ml-auto"
					type="button"
					use:tippy={{ content: $t('editor.advanced_settings') }}
					on:click={() => (advanced_options_open = true)}
				>
					<svg
						class="text-white w-5 h-5"
						aria-hidden="true"
						fill="none"
						stroke="white"
						stroke-width="2"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
							stroke-linecap="round"
							stroke-linejoin="round"
						></path>
						<path
							d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
							stroke-linecap="round"
							stroke-linejoin="round"
						></path>
					</svg>
				</button>
			</div>
		</div>
		{#if data.questions[selected_question].type === QuizQuestionType.SLIDE}
			{#await import('./slide.svelte')}
				<Spinner my_20={false} />
			{:then c}
				<svelte:component this={c.default} bind:data={data.questions[selected_question]} />
			{/await}
		{:else}
			{@const type = data.questions[selected_question].type}
			<div class="flex flex-col">
				<div class="flex justify-center pt-10 w-full">
					{#key unique}
						{#await import('$lib/inline-editor.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<div
								class="rounded-lg placeholder:italic placeholder:font-normal dark:bg-gray-500"
								class:bg-yellow-500={!reach(
									dataSchema,
									'questions[].question'
								).isValidSync(data.questions[selected_question].question)}
							>
								<svelte:component
									this={c.default}
									bind:text={data.questions[selected_question].question}
								/>
							</div>
						{/await}
					{/key}
				</div>
				{#if data.questions[selected_question].image}
					<div class="flex justify-center pt-10 w-full h-72">
						<div class="h-72 relative">
							<button
								class="rounded-full absolute -top-2 -right-2 opacity-70 hover:opacity-100 transition"
								type="button"
								on:click={() => {
									data.questions[selected_question].image = null;
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
							<MediaComponent bind:src={image_url} />
						</div>
					</div>
				{:else}
					{#await import('$lib/editor/uploader.svelte')}
						<Spinner my_20={false} />
					{:then c}
						<svelte:component
							this={c.default}
							bind:modalOpen={uppyOpen}
							bind:edit_id
							bind:data
							bind:selected_question
							video_upload={true}
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
							class="w-20 bg-transparent rounded-lg text-lg border-2 border-gray-500 p-1 outline-none focus:shadow-2xl"
							bind:value={data.questions[selected_question].time}
						/>
						<p class="inline-block">s</p>
					</div>
				</div>
				<div class="flex justify-center py-5">
					<p>{type_to_name[String(data.questions[selected_question].type)]}</p>
				</div>
				<div class="flex justify-center w-full">
					{#if type === QuizQuestionType.ABCD || type === QuizQuestionType.CHECK}
						{#await import('$lib/editor/ABCDEditorPart.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<svelte:component
								this={c.default}
								bind:data
								bind:selected_question
								check_choice={type === QuizQuestionType.CHECK}
							/>
						{/await}
					{:else if type === QuizQuestionType.RANGE}
						<RangeEditor bind:selected_question bind:data />
					{:else if type === QuizQuestionType.VOTING}
						{#await import('$lib/editor/VotingEditorPart.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<svelte:component this={c.default} bind:data bind:selected_question />
						{/await}
					{:else if type === QuizQuestionType.TEXT}
						{#await import('$lib/editor/TextEditorPart.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<svelte:component this={c.default} bind:data bind:selected_question />
						{/await}
					{:else if type === QuizQuestionType.ORDER}
						{#await import('$lib/editor/OrderEditorPart.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<svelte:component this={c.default} bind:data bind:selected_question />
						{/await}
					{/if}
				</div>
			</div>
		{/if}
	</div>
</div>

{#if advanced_options_open}
	<div
		class="fixed top-0 left-0 w-full h-full bg-black/60 flex"
		transition:fade={{ duration: 150 }}
	>
		<div class="w-1/4 h-1/3 m-auto bg-white dark:bg-gray-700 rounded-lg flex flex-col p-2 gap-2">
			<h1 class="text-3xl mx-auto">{$t('editor.advanced_settings')}</h1>
			<label class="flex justify-around text-lg">
				<span class="my-auto">{$t('editor.hide_question_results')}</span>
				<input type="checkbox" bind:checked={data.questions[selected_question]["hide_results"]} />
			</label>
			<div class="mt-auto w-full">
				<BrownButton on:click={() => (advanced_options_open = false)}>{$t('words.close')}</BrownButton>
			</div>

		</div>
	</div>
{/if}
