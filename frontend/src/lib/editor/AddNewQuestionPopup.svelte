<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Answers, Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';

	export let questions: Question[];
	export let open: boolean;

	export let selected_question: number;

	const { t } = getLocalization();
	onMount(() => {
		document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	});
	const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
		if (key.code === 'Escape') {
			open = false;
		}
	};
	const on_parent_click = (e: Event) => {
		if (e.target === e.currentTarget) {
			open = false;
		}
	};

	const question_types: {
		name: string;
		description: string;
		answers: Answers;
		type: QuizQuestionType;
	}[] = [
		{
			name: $t('words.multiple_choice'),
			description: $t('editor.abcd_description'),
			answers: [],
			type: QuizQuestionType.ABCD
		},
		{
			name: $t('words.voting'),
			description: $t('editor.voting_description'),
			answers: [],
			type: QuizQuestionType.VOTING
		},
		{
			name: $t('words.check_choice'),
			description: $t('editor.check_choice_description'),
			answers: [],
			type: QuizQuestionType.CHECK
		},
		{
			name: $t('words.order'),
			description: $t('editor.order_description'),
			answers: [],
			type: QuizQuestionType.ORDER
		},
		{
			name: $t('words.text'),
			description: $t('editor.text_description'),
			answers: [],
			type: QuizQuestionType.TEXT
		},
		{
			name: $t('words.range'),
			description: $t('editor.range_description'),
			answers: {
				max: 10,
				min: 0,
				max_correct: 7,
				min_correct: 3
			},
			type: QuizQuestionType.RANGE
		}
	];

	const add_question = (index: number) => {
		const empty_question: Question = {
			type: question_types[index].type,
			time: '20',
			question: '',
			image: undefined,
			answers: question_types[index].answers
		};
		questions = [...questions, { ...empty_question }];
		selected_question = questions.length - 1;
		open = false;
	};
</script>

<div
	class="fixed top-0 left-0 w-screen h-screen flex bg-black z-50 bg-opacity-50"
	on:click={on_parent_click}
	transition:fade|local={{ duration: 100 }}
>
	<div class="m-auto w-2/3 h-5/6 rounded shadow-2xl bg-white dark:bg-gray-600 p-6 flex flex-col">
		<h1 class="text-center text-3xl mb-6">{$t('quiztivity.editor.select_page_type')}</h1>
		<div class="grid grid-cols-4 gap-4 overflow-y-scroll">
			{#each question_types as qt, i}
				<div class="rounded p-6 border-[#B07156] border">
					<button
						class="text-xl text-black dark:text-white"
						on:click={() => {
							add_question(i);
						}}>{qt.name}</button
					>
					<p class="text-sm">{qt.description}</p>
				</div>
			{/each}
		</div>

		<div class="mt-auto flex justify-center">
			<p>
				{$t('editor.need_more_help')}
				<a
					href="/docs/quiz/question-types"
					target="_blank"
					class="text-sm font-bold underline text-blue-500 dark:text-blue-400"
					>{$t('editor.visit_docs')}</a
				>
			</p>
		</div>
	</div>
</div>
