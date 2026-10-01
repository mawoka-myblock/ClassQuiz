<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { reach } from 'yup';
	import { dataSchema } from '$lib/yupSchemas';
	import { editorValidation } from '$lib/editor/validation.svelte';
	import { isQuestionComplete } from '$lib/editor/question_complete';
	import { htmlToPlainText } from '$lib/sanitize';
	import Spinner from '../Spinner.svelte';
	import { getLocalization } from '$lib/i18n';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import RangeEditor from '$lib/editor/RangeSelectorEditorPart.svelte';
	import { fade } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import * as AlertDialog from '$lib/components/ui/alert-dialog/index.js';
	import { buttonVariants } from '$lib/components/ui/button';
	import CircleDot from '@lucide/svelte/icons/circle-dot';
	import Clock from '@lucide/svelte/icons/clock';
	import ListChecks from '@lucide/svelte/icons/list-checks';
	import Settings2 from '@lucide/svelte/icons/settings-2';
	import ChevronUp from '@lucide/svelte/icons/chevron-up';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import Copy from '@lucide/svelte/icons/copy';
	import GripVertical from '@lucide/svelte/icons/grip-vertical';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import X from '@lucide/svelte/icons/x';

	const { t } = getLocalization();

	interface Props {
		data: EditorData;
		/** This card's question. Fixed for the card: the column renders one per question. */
		index: number;
		focused: boolean;
		edit_id: string;
		total: number;
		onselect: (index: number) => void;
		onmove: (from: number, to: number) => void;
		ondelete: (index: number) => void;
		onduplicate: (index: number) => void;
		ondragstart: (index: number) => void;
		ondragenter: (index: number) => void;
		ondragend: () => void;
		dragging: boolean;
	}

	let {
		data = $bindable(),
		index,
		focused,
		edit_id = $bindable(),
		total,
		onselect,
		onmove,
		ondelete,
		onduplicate,
		ondragstart,
		ondragenter,
		ondragend,
		dragging
	}: Props = $props();

	let advanced_options_open = $state(false);
	let confirm_delete = $state(false);
	let uppyOpen = $state(false);

	const question = $derived(data.questions[index]);
	const type = $derived(question.type);

	// The timer is a free-text number field, so it can hold anything the keyboard
	// produces. Clamp what the author can store rather than what the game has to cope with.
	const correctTimeInput = () => {
		const time = data.questions[index].time;
		if (time === null || time === undefined) {
			data.questions[index].time = '';
			return;
		}
		if (String(time).length > 3) {
			data.questions[index].time = String(time).slice(0, 3);
		}
	};

	const question_valid = $derived(
		// Marked only after the first Save (validation.svelte.ts): a new question is blank.
		!editorValidation.shown ||
			reach(dataSchema, 'questions[].question').isValidSync(question.question)
	);
	const incomplete = $derived(editorValidation.shown && !isQuestionComplete(question));
	const summary = $derived(htmlToPlainText(question.question ?? '').trim());
	const answers = $derived(Array.isArray(question.answers) ? question.answers : []);

	// Arrow keys on the grip move the question without a pointer at all, which is the
	// single-pointer alternative WCAG 2.5.7 asks for. Kept from the old rail.
	const on_grip_keydown = (e: KeyboardEvent) => {
		const delta = e.key === 'ArrowUp' ? -1 : e.key === 'ArrowDown' ? 1 : 0;
		if (delta === 0) return;
		e.preventDefault();
		e.stopPropagation();
		onmove(index, index + delta);
		const target = e.currentTarget as HTMLElement;
		requestAnimationFrame(() =>
			target.closest('[data-question-card]')?.querySelector<HTMLElement>('[data-grip]')?.focus()
		);
	};
</script>

<!-- One card per question in a single column, the way Google Forms and Kahoot both do
     it: the whole quiz is visible as a list, and the card you are working on opens in
     place. A collapsed card renders plain text on purpose -- the rich-text editor is a
     CKEditor instance, and twenty of them on one page is not an editor, it is a stall. -->
<article
	data-question-card
	data-question-index={index}
	class="border-border bg-card relative scroll-mt-24 rounded-xl border shadow-sm transition
	       {focused ? 'ring-primary/40 ring-2' : 'hover:border-border'}
	       {dragging ? 'opacity-40' : ''}"
	ondragover={(e) => {
		e.preventDefault();
		ondragenter(index);
	}}
	ondrop={(e) => {
		e.preventDefault();
		ondragend();
	}}
	role="listitem"
>
	<div class="flex items-start gap-1 p-2 sm:gap-2 sm:p-3">
		<!-- Only the grip starts a drag, so selecting text in the card does not drag it. -->
		<button
			type="button"
			data-grip
			draggable="true"
			ondragstart={() => ondragstart(index)}
			ondragend={ondragend}
			onkeydown={on_grip_keydown}
			class="fq-touch-target text-muted-foreground hover:text-foreground focus-visible:ring-ring mt-1 inline-flex size-8 shrink-0 cursor-grab items-center justify-center rounded-md focus-visible:ring-2 focus-visible:outline-none"
			aria-label={$t('editor.reorder_grip', { n: index + 1 })}
		>
			<GripVertical class="size-4" />
		</button>

		<div class="min-w-0 flex-1">
			{#if focused}
				<!-- Toolbar: what this question is, how long it runs, how it is answered. -->
				<div class="flex flex-wrap items-center gap-2 pt-1 pr-1 pb-3">
					<p class="text-muted-foreground text-sm font-medium">
						{$t('editor.question_n_of_total', { n: index + 1, total })}
					</p>
					<!-- The open card needs the marker as much as a closed one: after Save the
					     header says how many questions need finishing, and the author has to be
					     able to see which card they are standing in is one of them. -->
					{#if incomplete}
						<Badge variant="destructive">{$t('editor.question_incomplete')}</Badge>
					{/if}
					<div class="ml-auto flex flex-wrap items-center gap-1.5">
						<label
							class="border-input bg-background text-muted-foreground flex min-h-9 items-center gap-1.5 rounded-md border px-2 py-1 text-sm"
						>
							<Clock class="size-4" />
							<span class="sr-only">{$t('editor.time_in_seconds')}</span>
							<input
								type="number"
								max="999"
								min="1"
								class="text-foreground w-10 bg-transparent text-right tabular-nums outline-none"
								bind:value={data.questions[index].time}
								oninput={correctTimeInput}
							/>
							<span>s</span>
						</label>
						{#if type === QuizQuestionType.ABCD || type === QuizQuestionType.CHECK}
							<Button
								type="button"
								variant="outline"
								size="sm"
								onclick={() => {
									data.questions[index].type =
										type === QuizQuestionType.CHECK
											? QuizQuestionType.ABCD
											: QuizQuestionType.CHECK;
								}}
							>
								{#if type === QuizQuestionType.CHECK}
									<ListChecks />
									{$t('editor.multiple_answers')}
								{:else}
									<CircleDot />
									{$t('editor.single_answer')}
								{/if}
							</Button>
						{/if}
						<Button
							variant="ghost"
							size="icon"
							type="button"
							title={$t('editor.advanced_settings')}
							aria-label={$t('editor.advanced_settings')}
							onclick={() => (advanced_options_open = true)}
						>
							<Settings2 />
						</Button>
					</div>
				</div>

				<!-- The body renders the question the way the room will see it, so there is no
				     gap between what the author builds and what gets projected. -->
				<div class="flex flex-col gap-5 pb-1">
					{#if type === QuizQuestionType.SLIDE}
						{#await import('./slide.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<c.default bind:data={data.questions[index]} />
						{/await}
					{:else}
						{#await import('$lib/inline-editor.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<div
								class="rounded-lg text-center text-xl font-semibold [&_[contenteditable]]:w-full"
								class:ring-2={!question_valid}
								class:ring-destructive={!question_valid}
							>
								<c.default
									bind:text={data.questions[index].question}
									label={$t('editor.question_text')}
								/>
							</div>
						{/await}

						{#if question.image}
							<div class="relative mx-auto w-fit">
								<button
									class="border-border bg-card text-muted-foreground hover:text-destructive focus-visible:ring-ring absolute -top-2 -right-2 z-10 rounded-full border p-1 shadow-sm transition focus-visible:ring-2 focus-visible:outline-none"
									type="button"
									title={$t('words.delete')}
									aria-label={$t('words.delete')}
									onclick={() => {
										data.questions[index].image = null;
									}}
								>
									<X class="size-4" />
								</button>
								<div class="h-56">
									<MediaComponent src={question.image} />
								</div>
							</div>
						{:else}
							{#await import('$lib/editor/uploader.svelte')}
								<Spinner my_20={false} />
							{:then c}
								<c.default
									bind:modalOpen={uppyOpen}
									bind:data
									selected_question={index}
									video_upload={false}
									library_enabled={false}
									pixabay_enabled={false}
								/>
							{/await}
						{/if}

						{#if type === QuizQuestionType.ABCD || type === QuizQuestionType.CHECK}
							{#await import('$lib/editor/ABCDEditorPart.svelte')}
								<Spinner my_20={false} />
							{:then c}
								<c.default
									bind:data
									selected_question={index}
									check_choice={type === QuizQuestionType.CHECK}
								/>
							{/await}
						{:else if type === QuizQuestionType.RANGE}
							<RangeEditor selected_question={index} bind:data />
						{:else if type === QuizQuestionType.VOTING}
							{#await import('$lib/editor/VotingEditorPart.svelte')}
								<Spinner my_20={false} />
							{:then c}
								<c.default bind:data selected_question={index} />
							{/await}
						{:else if type === QuizQuestionType.TEXT}
							{#await import('$lib/editor/TextEditorPart.svelte')}
								<Spinner my_20={false} />
							{:then c}
								<c.default bind:data selected_question={index} />
							{/await}
						{:else if type === QuizQuestionType.ORDER}
							{#await import('$lib/editor/OrderEditorPart.svelte')}
								<Spinner my_20={false} />
							{:then c}
								<c.default bind:data selected_question={index} />
							{/await}
						{/if}
					{/if}
				</div>
			{:else}
				<!-- Collapsed: enough to recognise the question and see whether it is finished. -->
				<button
					type="button"
					class="focus-visible:ring-ring w-full rounded-lg px-1 py-2 text-left focus-visible:ring-2 focus-visible:outline-none"
					onclick={() => onselect(index)}
				>
					<span class="flex items-baseline gap-2">
						<span class="text-muted-foreground shrink-0 text-sm tabular-nums">
							{index + 1}
						</span>
						<span class="min-w-0 flex-1 truncate font-medium">
							{summary || $t('editor.no_title')}
						</span>
						{#if incomplete}
							<Badge variant="destructive" class="shrink-0">
								{$t('editor.question_incomplete')}
							</Badge>
						{/if}
					</span>
					{#if answers.length}
						<span class="mt-1.5 flex flex-wrap gap-1.5 pl-6">
							{#each answers.slice(0, 4) as answer, i (i)}
								<span
									class="bg-muted text-muted-foreground max-w-[12rem] truncate rounded-sm px-1.5 py-0.5 text-xs"
									class:font-medium={answer.right}
									class:text-foreground={answer.right}
								>
									{answer.right ? '✓ ' : ''}{htmlToPlainText(answer.answer ?? '') ||
										$t('editor.empty')}
								</span>
							{/each}
						</span>
					{/if}
				</button>
			{/if}
		</div>

	</div>

	<!-- Card actions sit in a footer on the open card, the way Forms and Kahoot both do
	     it: on the right of the content they are a third column, and at 390px a third
	     column leaves the question about 200px to live in. The closed card carries none
	     of them -- a list of twenty questions should read as a list, not as eighty
	     buttons. -->
	{#if focused}
		<div class="border-border flex items-center justify-end gap-0.5 border-t px-2 py-1">
			<Button
				type="button"
				variant="ghost"
				size="icon"
				disabled={index === 0}
				aria-label={$t('editor.move_question_up')}
				title={$t('editor.move_question_up')}
				onclick={() => onmove(index, index - 1)}
			>
				<ChevronUp />
			</Button>
			<Button
				type="button"
				variant="ghost"
				size="icon"
				disabled={index === total - 1}
				aria-label={$t('editor.move_question_down')}
				title={$t('editor.move_question_down')}
				onclick={() => onmove(index, index + 1)}
			>
				<ChevronDown />
			</Button>
			<Button
				type="button"
				variant="ghost"
				size="icon"
				aria-label={$t('editor.duplicate_question')}
				title={$t('editor.duplicate_question')}
				onclick={() => onduplicate(index)}
			>
				<Copy />
			</Button>
			<!-- Deleting a question is the one action here that cannot be undone -- the
			     editor autosaves, so it is gone from the server moments later. It asks
			     first, like deleting a quiz does. -->
			<AlertDialog.Root bind:open={confirm_delete}>
				<!-- The whole editor is one <form>, so a button with no type submits it: the
				     trash icon saved the quiz and left for the view page instead of asking. -->
				<AlertDialog.Trigger
					type="button"
					class={buttonVariants({
						variant: 'ghost',
						size: 'icon',
						class: 'text-muted-foreground hover:text-destructive'
					})}
					aria-label={$t('editor.delete_question')}
					title={$t('editor.delete_question')}
				>
					<Trash2 />
				</AlertDialog.Trigger>
				<AlertDialog.Content class="max-w-md">
					<AlertDialog.Header>
						<AlertDialog.Title>{$t('editor.delete_question_confirm')}</AlertDialog.Title>
						<AlertDialog.Description>
							{summary || $t('editor.no_title')}
						</AlertDialog.Description>
					</AlertDialog.Header>
					<AlertDialog.Footer>
						<AlertDialog.Cancel type="button">{$t('words.cancel')}</AlertDialog.Cancel>
						<AlertDialog.Action
							type="button"
							class={buttonVariants({ variant: 'destructive' })}
							onclick={() => ondelete(index)}
						>
							{$t('words.delete')}
						</AlertDialog.Action>
					</AlertDialog.Footer>
				</AlertDialog.Content>
			</AlertDialog.Root>
		</div>
	{/if}
</article>

{#if advanced_options_open}
	<div class="fixed inset-0 z-50 flex bg-black/60 p-4" transition:fade|global={{ duration: 150 }}>
		<div
			class="border-border bg-card m-auto flex w-full max-w-sm flex-col gap-5 rounded-xl border p-5 shadow-xl"
		>
			<h2 class="text-lg font-semibold">{$t('editor.advanced_settings')}</h2>
			<label class="flex items-center justify-between gap-4 text-sm">
				<span>{$t('editor.hide_question_results')}</span>
				<input
					type="checkbox"
					class="accent-primary size-5"
					bind:checked={data.questions[index]['hide_results']}
				/>
			</label>
			<Button class="w-full" type="button" onclick={() => (advanced_options_open = false)}>
				{$t('words.close')}
			</Button>
		</div>
	</div>
{/if}
