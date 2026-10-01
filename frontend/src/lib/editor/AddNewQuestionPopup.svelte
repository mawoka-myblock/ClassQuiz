<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Answers, Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Button } from '$lib/components/ui/button';
	import X from '@lucide/svelte/icons/x';

	interface Props {
		questions: Question[];
		open: boolean;
		selected_question: number;
		/** Insert before this index. null appends, which is what the end button does. */
		at?: number | null;
	}

	let {
		questions = $bindable(),
		open = $bindable(),
		selected_question = $bindable(),
		at = null
	}: Props = $props();

	const { t } = getLocalization();

	// RANGE, TEXT, VOTING, ORDER and SLIDE were cut from the MVP: each one multiplies the
	// editor, the play screen, the results screen and the scoring path, and none of them is
	// what people run a live quiz for. True/false needs no type of its own -- it is an ABCD
	// question with two answers. Existing quizzes that already use a cut type still open and
	// still play; this list only governs what can be created from here.
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
			name: $t('words.check_choice'),
			description: $t('editor.check_choice_description'),
			answers: [],
			type: QuizQuestionType.CHECK
		},
		// True/False is not a type of its own anywhere: it is an ABCD question that
		// arrives with its two answers already written. Kahoot offers the same preset,
		// and it needs no play, scoring or export path that ABCD does not already have.
		{
			name: $t('words.true_false'),
			description: $t('editor.true_false_description'),
			answers: [
				{ answer: $t('words.true'), right: true },
				{ answer: $t('words.false'), right: false }
			],
			type: QuizQuestionType.ABCD
		}
	];

	const add_question = (index: number) => {
		const empty_question: Question = {
			type: question_types[index].type,
			time: '20',
			question: '',
			image: undefined,
			// A fresh copy: the preset's answers are a template, not shared state.
			answers: question_types[index].answers.map((a) => ({ ...a }))
		};
		const position = at === null ? questions.length : Math.max(0, Math.min(at, questions.length));
		questions = [
			...questions.slice(0, position),
			{ ...empty_question },
			...questions.slice(position)
		];
		// The new question is the one you are about to write, so it opens.
		selected_question = position;
		open = false;
	};
</script>

<!-- Was a hand-rolled overlay: a fixed div, a body keydown listener for Escape, and a
     target === currentTarget check for the backdrop. The shadcn Dialog brings the
     Escape handling, the backdrop, the focus trap and the return of focus to whatever
     opened it -- none of which the hand-rolled version did. Its own close button is
     turned off because its label is hardcoded English; ours is translated. -->
<Dialog.Root bind:open>
	<Dialog.Content showCloseButton={false} class="gap-5">
		<div class="flex items-start justify-between gap-4">
			<Dialog.Title class="text-lg font-semibold">
				{$t('editor.add_new_question')}
			</Dialog.Title>
			<Dialog.Close>
				{#snippet child({ props })}
					<Button variant="ghost" size="icon-sm" aria-label={$t('words.close')} {...props}>
						<X />
					</Button>
				{/snippet}
			</Dialog.Close>
		</div>

		<div class="flex flex-col gap-2">
			{#each question_types as qt, i (qt.name)}
				<button
					type="button"
					class="border-border hover:border-primary/50 hover:bg-muted focus-visible:ring-ring rounded-lg border p-4 text-left transition focus-visible:ring-2 focus-visible:outline-none"
					onclick={() => {
						add_question(i);
					}}
				>
					<span class="font-medium">{qt.name}</span>
					<span class="text-muted-foreground mt-1 block text-sm">{qt.description}</span>
				</button>
			{/each}
		</div>
	</Dialog.Content>
</Dialog.Root>
