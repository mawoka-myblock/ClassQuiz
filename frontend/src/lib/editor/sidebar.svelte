<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData } from '../quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { reach } from 'yup';
	import { ABCDQuestionSchema, dataSchema } from '../yupSchemas';
	import { createTippy } from 'svelte-tippy';
	import { getLocalization } from '$lib/i18n';
	import { isQuestionComplete } from '$lib/editor/question_complete';
	import { editorValidation } from '$lib/editor/validation.svelte';
	import { moveItem, selectionAfterMove } from '$lib/editor/reorder';
	import { sanitizeTitleHtml, htmlToPlainText } from '$lib/sanitize';
	import AddNewQuestionPopup from '$lib/editor/AddNewQuestionPopup.svelte';
	import { Button } from '$lib/components/ui/button';
	import GripVertical from '@lucide/svelte/icons/grip-vertical';
	import Settings2 from '@lucide/svelte/icons/settings-2';
	import Check from '@lucide/svelte/icons/check';
	import Globe from '@lucide/svelte/icons/globe';
	import Link2 from '@lucide/svelte/icons/link-2';
	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';
	import PanelLeftClose from '@lucide/svelte/icons/panel-left-close';
	import PanelLeftOpen from '@lucide/svelte/icons/panel-left-open';

	const { t } = getLocalization();

	interface Props {
		/** Collapsed to a slim strip. The list stays in the layout either way. */
		collapsed?: boolean;
		data: EditorData;
		selected_question?: any;
	}

	let {
		data = $bindable(),
		selected_question = $bindable(-1),
		collapsed = $bindable(false)
	}: Props = $props();

	// Reordering was a mode: a toolbar toggle that laid two invisible half-card hit
	// areas over every question, each holding an unsized <svg> that stretched to fill
	// its grid cell -- so turning it on painted a pair of chevrons the size of the card
	// over the content you were trying to reorder. It was also unreachable by keyboard:
	// the hit areas were `role="button"` divs with no tabindex.
	//
	// Dragging replaces it, matching the long-press drag the mobile strip already has.
	// The grip is a real button, so Arrow keys move the question without a pointer at
	// all, which is the single-pointer alternative WCAG 2.5.7 asks for.
	let drag_from: number | null = $state(null);
	let drag_over: number | null = $state(null);

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'right'
	});
	let arr_of_cards = $state(Array(data.questions.length));
	let propertyCard = $state();
	let add_new_question_popup_open = $state(false);

	const moveQuestion = (from: number, to: number) => {
		if (to < 0 || to >= data.questions.length || from === to) {
			return;
		}
		data.questions = moveItem(data.questions, from, to);
		selected_question = selectionAfterMove(selected_question, from, to);
	};

	const on_grip_keydown = (e: KeyboardEvent, index: number) => {
		const delta = e.key === 'ArrowUp' ? -1 : e.key === 'ArrowDown' ? 1 : 0;
		if (delta === 0) {
			return;
		}
		e.preventDefault();
		e.stopPropagation();
		moveQuestion(index, index + delta);
		// Keep the grip under the finger: after the move, focus the one that travelled.
		const target = e.currentTarget as HTMLElement;
		requestAnimationFrame(() =>
			target
				.closest('[data-question-card]')
				?.querySelector<HTMLElement>('[data-grip]')
				?.focus()
		);
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

<!-- Below lg the rail is an off-canvas drawer: a fixed w-72 rail on a 390px phone
     leaves about 118px of canvas, which is not an editor. At lg and up it is a
     static column again. The scrim is a sibling so it never covers the rail. -->
<!-- The question list is the editor's navigation and the only place the quiz's shape
     is visible, so it stays in the layout at every width: an aside that collapses to
     a slim strip, never an overlay that hides the structure behind a tap. Below lg
     the horizontal strip in question-strip.svelte plays the same role. -->
<aside
	class="border-border bg-muted/30 hidden shrink-0 flex-col border-r transition-[width] duration-200 lg:flex
		{collapsed ? 'w-12' : 'w-64 xl:w-72'}"
>
	<div class="border-border flex h-14 shrink-0 items-center gap-2 border-b px-2">
		<p
			class="text-muted-foreground min-w-0 flex-1 truncate px-1 text-xs font-medium {collapsed
				? 'hidden'
				: ''}"
		>
			{$t('editor.questions_count', { count: data.questions.length })}
		</p>
		<Button
			type="button"
			variant="ghost"
			size="icon-sm"
			class="shrink-0"
			aria-label={collapsed ? $t('editor.show_questions') : $t('editor.hide_questions')}
			aria-expanded={!collapsed}
			onclick={() => (collapsed = !collapsed)}
		>
			{#if collapsed}<PanelLeftOpen />{:else}<PanelLeftClose />{/if}
		</Button>
	</div>
	<div class="min-h-0 flex-1 overflow-y-auto p-3 {collapsed ? 'hidden' : ''}">
		<div
			bind:this={propertyCard}
			class="border-border bg-card mb-3 rounded-lg border p-2 transition hover:cursor-pointer"
			class:ring-2={selected_question === -1}
			class:ring-primary={selected_question === -1}
			onclick={() => setSelectedQuestion(-1)}
		>
			<p class="text-muted-foreground mb-2 flex items-center gap-2 text-xs font-medium">
				<Settings2 class="size-3.5" />
				{$t('editor.quiz_setup')}
			</p>
			<div
				use:tippy={{
					content: data.title === '' ? "It's empty!" : htmlToPlainText(data.title)
				}}
				class="border-border m-1 rounded-md border p-1 transition"
				class:ring-2={editorValidation.shown &&
					!reach(dataSchema, 'title').isValidSync(data.title)}
				class:ring-destructive={editorValidation.shown &&
					!reach(dataSchema, 'title').isValidSync(data.title)}
			>
				<p
					type="text"
					class="w-full truncate rounded-sm bg-transparent text-center whitespace-nowrap"
				>
					{#if data.title}
						{@html sanitizeTitleHtml(data.title)}
					{:else}
						<i>{$t('editor.no_title')}</i>
					{/if}
				</p>
			</div>
			<div
				use:tippy={{ content: data.description === '' ? "It's empty!" : data.description }}
				class="border-border m-1 rounded-md border p-1 transition"
				class:ring-2={editorValidation.shown &&
					!reach(dataSchema, 'description').isValidSync(data.description)}
				class:ring-destructive={editorValidation.shown &&
					!reach(dataSchema, 'description').isValidSync(data.description)}
			>
				<textarea
					bind:value={data.description}
					class="w-full resize-none rounded-sm bg-transparent text-sm"
				></textarea>
			</div>
			<div class="flex w-full justify-center">
				<button
					type="button"
					onclick={() => {
						data.public = !data.public;
					}}
					class="text-muted-foreground hover:text-foreground flex items-center gap-1.5 rounded-md px-2 py-1 text-sm transition"
				>
					{#if data.public}
						<Globe class="inline-block size-4" />
						<span>{$t('words.public')}</span>
					{:else}
						<Link2 class="inline-block size-4" />
						<span>{$t('words.private')}</span>
					{/if}
				</button>
			</div>
		</div>
		{#each data.questions as question, index}
			<div
				data-question-card
				class="border-border bg-card relative mb-3 rounded-lg border p-2 transition hover:cursor-pointer"
				class:ring-2={index === selected_question}
				class:ring-primary={index === selected_question}
				class:opacity-40={drag_from === index}
				ondragover={(e) => {
					if (drag_from === null) return;
					e.preventDefault();
					drag_over = index;
				}}
				ondragleave={() => {
					if (drag_over === index) drag_over = null;
				}}
				ondrop={(e) => {
					if (drag_from === null) return;
					e.preventDefault();
					moveQuestion(drag_from, index);
					drag_from = null;
					drag_over = null;
				}}
				onclick={() => {
					setSelectedQuestion(index);
				}}
				bind:this={arr_of_cards[index]}
			>
				<!-- A real element, not a before:/after: variant: those need an explicit
				     content-[''] to generate a box at all, so the indicator was there in
				     the class list and invisible on screen. -->
				{#if drag_over === index && drag_from !== null && drag_from !== index}
					<div
						class="bg-primary pointer-events-none absolute inset-x-0 h-0.5 rounded-full"
						class:-top-1.5={drag_from > index}
						class:-bottom-1.5={drag_from < index}
						aria-hidden="true"
					></div>
				{/if}
				<button
					class="border-border bg-card text-muted-foreground hover:text-destructive focus-visible:ring-ring absolute -top-2 -right-2 rounded-full border p-1 shadow-sm transition focus-visible:ring-2 focus-visible:outline-none"
					type="button"
					title={$t('editor.delete_question')}
					aria-label={$t('editor.delete_question')}
					onclick={() => {
						if (confirm('Do you really want to delete this Question?')) {
							selected_question = -1;
							data.questions.splice(index, 1);
							data.questions = data.questions;
						}
					}}
				>
					<X class="size-4" />
				</button>
				<div
					use:tippy={{
						content:
							question.question === ''
								? 'No title'
								: htmlToPlainText(question.question)
					}}
					class="mb-2 flex items-center gap-2"
				>
					<!-- The whole card is draggable, but only the grip starts a drag, so
					     selecting a question by clicking its title still works. -->
					<button
						data-grip
						type="button"
						draggable="true"
						class="text-muted-foreground hover:text-foreground focus-visible:ring-ring -ml-1 shrink-0 cursor-grab rounded-sm p-0.5 transition-colors focus-visible:ring-2 focus-visible:outline-none active:cursor-grabbing"
						aria-label={$t('editor.reorder_grip', { n: index + 1 })}
						onclick={(e) => e.stopPropagation()}
						onkeydown={(e) => on_grip_keydown(e, index)}
						ondragstart={(e) => {
							drag_from = index;
							e.dataTransfer?.setData('text/plain', String(index));
							if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move';
						}}
						ondragend={() => {
							drag_from = null;
							drag_over = null;
						}}
					>
						<GripVertical class="size-4" aria-hidden="true" />
					</button>
					<span class="text-muted-foreground w-4 shrink-0 text-xs tabular-nums"
						>{index + 1}</span
					>
					{#if editorValidation.shown && !isQuestionComplete(question)}
						<span
							class="bg-destructive size-2 shrink-0 rounded-full"
							title={$t('editor.question_incomplete')}
						></span>
						<span class="sr-only">{$t('editor.question_incomplete')}</span>
					{/if}
					<p class="min-w-0 flex-1 truncate text-sm">
						{#if question.question === ''}
							<span class="text-muted-foreground italic">{$t('editor.no_title')}</span
							>
						{:else}
							{@html sanitizeTitleHtml(question.question)}
						{/if}
					</p>
				</div>
				{#if question.image}
					<div class="flex justify-center align-middle pb-0.5">
						<img
							src="/api/v1/storage/download/{question.image}"
							class="h-10 border rounded-lg"
							alt="Not available"
							use:tippy={{
								content: `<img src="/api/v1/storage/download/${question.image}" alt="Not available" class="rounded-sm">`,
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
									class="flex items-center gap-1 truncate rounded-md border px-1.5 py-0.5 text-sm whitespace-nowrap {answer.right
										? 'border-primary/40 bg-primary/10'
										: 'border-border bg-muted text-muted-foreground'}"
									class:ring-2={editorValidation.shown &&
										!reach(ABCDQuestionSchema, 'answer').isValidSync(
											answer.answer
										)}
									class:ring-destructive={editorValidation.shown &&
										!reach(ABCDQuestionSchema, 'answer').isValidSync(
											answer.answer
										)}
									use:tippy={{
										content:
											answer.answer === ''
												? $t('editor.empty')
												: answer.answer
									}}
								>
									{#if answer.right}<Check class="size-3 shrink-0" />{/if}
									<span class="truncate"
										>{#if answer.answer === ''}<i>{$t('editor.empty')}</i
											>{:else}{answer.answer}{/if}</span
									>
								</span>
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
									class="border-border bg-muted text-muted-foreground truncate rounded-md border px-1.5 py-0.5 text-center text-sm whitespace-nowrap"
									class:ring-2={editorValidation.shown &&
										!reach(ABCDQuestionSchema, 'answer').isValidSync(
											answer.answer
										)}
									class:ring-destructive={editorValidation.shown &&
										!reach(ABCDQuestionSchema, 'answer').isValidSync(
											answer.answer
										)}
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
	</div>
	<!-- The add control used to be the last child of the scrolling list, so on a quiz
	     with more than a screenful of questions it scrolled out of reach and the only
	     way to add one was to scroll to the bottom first. It is a pinned footer of the
	     rail now, outside the scroll container. -->
	<div class="border-border shrink-0 border-t p-3 {collapsed ? 'hidden' : ''}">
		<Button
			class="w-full"
			type="button"
			variant="outline"
			onclick={() => {
				add_new_question_popup_open = true;
			}}
		>
			<Plus />
			{$t('editor.add_new_question')}
		</Button>
	</div>
</aside>
<!-- No {#if} wrapper: Dialog.Root owns its own visibility, and mounting on `open`
     would skip the exit animation and rebuild the dialog on every open. -->
<AddNewQuestionPopup
	bind:questions={data.questions}
	bind:open={add_new_question_popup_open}
	bind:selected_question
/>
