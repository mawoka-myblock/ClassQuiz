<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { run } from 'svelte/legacy';

	import type { EditorData } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import RangeEditor from '$lib/editor/RangeSelectorEditorPart.svelte';
	import { reach } from 'yup';
	import { dataSchema } from '$lib/yupSchemas';
	import { editorValidation } from '$lib/editor/validation.svelte';
	import Spinner from '../Spinner.svelte';
	import { getLocalization } from '$lib/i18n';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { fade } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import CircleDot from '@lucide/svelte/icons/circle-dot';
	import Clock from '@lucide/svelte/icons/clock';
	import ListChecks from '@lucide/svelte/icons/list-checks';
	import Settings2 from '@lucide/svelte/icons/settings-2';
	import MoveLeft from '@lucide/svelte/icons/move-left';
	import MoveRight from '@lucide/svelte/icons/move-right';
	import X from '@lucide/svelte/icons/x';

	const { t } = getLocalization();

	interface Props {
		data: EditorData;
		selected_question: number;
		edit_id: string;
	}

	let {
		data = $bindable(),
		selected_question = $bindable(),
		edit_id = $bindable()
	}: Props = $props();

	let advanced_options_open = $state(false);

	let uppyOpen = $state(false);
	let unique = $state({});

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
	run(() => {
		correctTimeInput(data.questions[selected_question].time);
	});
	run(() => {
		selected_question;
		set_unique();
	});
	let image_url = $state('');

	const update_image_url = () => {
		image_url = data.questions[selected_question].image;
	};
	run(() => {
		update_image_url();
		selected_question;
		data.questions;
	});

	const type = $derived(data.questions[selected_question].type);
	const question_valid = $derived(
		// Marked only after the first Save (validation.svelte.ts): a new question is blank.
		!editorValidation.shown ||
			reach(dataSchema, 'questions[].question').isValidSync(
				data.questions[selected_question].question
			)
	);
	// Reordering is a move of the question plus a move of the selection: the author is
	// still editing the same question after it changes position, so the selection has
	// to follow it rather than stay on the index.
	const move_question = (delta: number) => {
		const to = selected_question + delta;
		if (to < 0 || to >= data.questions.length) return;
		const next = [...data.questions];
		[next[selected_question], next[to]] = [next[to], next[selected_question]];
		data.questions = next;
		selected_question = to;
	};
</script>

<div class="mx-auto flex w-full max-w-4xl flex-col gap-5">
	<!-- Toolbar: what this question is, how long it runs, and how it is answered. These
	     three facts govern the whole round, so they sit above the canvas rather than being
	     scattered through it. -->
	<div class="flex flex-wrap items-center gap-3">
		<p class="text-sm font-medium">
			{$t('editor.question_n_of_total', {
				n: selected_question + 1,
				total: data.questions.length
			})}
		</p>
		<!-- Reordering lives here rather than on the navigation chip: two 20px arrows
		     crammed into a 144px chip is half the 44px a finger needs, and it put two
		     different actions -- choose this question, move this question -- on the same
		     object. Two plain buttons that each say what they do: a bordered group with a
		     shared "Move" label glued to two icons was neither one control nor two, and
		     bare chevrons beside "Question 1 of 3" read as previous and next, which is
		     navigation and the opposite of what these do. -->
		<Button
			type="button"
			variant="outline"
			size="sm"
			disabled={selected_question === 0}
			onclick={() => move_question(-1)}
		>
			<MoveLeft />
			{$t('editor.move_question_left')}
		</Button>
		<Button
			type="button"
			variant="outline"
			size="sm"
			disabled={selected_question === data.questions.length - 1}
			onclick={() => move_question(1)}
		>
			{$t('editor.move_question_right')}
			<MoveRight />
		</Button>
		<div class="ml-auto flex flex-wrap items-center gap-2">
			<label
				class="border-input bg-background text-muted-foreground flex min-h-11 items-center gap-2 rounded-md border px-2.5 py-1.5 text-sm"
			>
				<Clock class="size-4" />
				<span class="sr-only">{$t('editor.time_in_seconds')}</span>
				<input
					type="number"
					max="999"
					min="1"
					class="text-foreground w-12 bg-transparent text-right tabular-nums outline-none"
					bind:value={data.questions[selected_question].time}
				/>
				<span>s</span>
			</label>
			{#if type === QuizQuestionType.ABCD || type === QuizQuestionType.CHECK}
				<Button
					type="button"
					variant="outline"
					size="sm"
					onclick={() => {
						data.questions[selected_question].type =
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

	<!-- The canvas renders the question the way the room will see it, so there is no gap
	     between what the author builds and what gets projected. -->
	<div class="border-border bg-card flex flex-col gap-6 rounded-xl border p-6 shadow-sm">
		{#if data.questions[selected_question].type === QuizQuestionType.SLIDE}
			{#await import('./slide.svelte')}
				<Spinner my_20={false} />
			{:then c}
				<c.default bind:data={data.questions[selected_question]} />
			{/await}
		{:else}
			{#key unique}
				{#await import('$lib/inline-editor.svelte')}
					<Spinner my_20={false} />
				{:then c}
					<div
						class="rounded-lg text-center text-xl font-semibold [&_[contenteditable]]:w-full"
						class:ring-2={!question_valid}
						class:ring-destructive={!question_valid}
					>
						<c.default bind:text={data.questions[selected_question].question} />
					</div>
				{/await}
			{/key}

			{#if data.questions[selected_question].image}
				<div class="relative mx-auto w-fit">
					<button
						class="border-border bg-card text-muted-foreground hover:text-destructive focus-visible:ring-ring absolute -top-2 -right-2 z-10 rounded-full border p-1 shadow-sm transition focus-visible:ring-2 focus-visible:outline-none"
						type="button"
						title={$t('words.delete')}
						aria-label={$t('words.delete')}
						onclick={() => {
							data.questions[selected_question].image = null;
						}}
					>
						<X class="size-4" />
					</button>
					<div class="h-56">
						<MediaComponent bind:src={image_url} />
					</div>
				</div>
			{:else}
				{#await import('$lib/editor/uploader.svelte')}
					<Spinner my_20={false} />
				{:then c}
					<c.default
						bind:modalOpen={uppyOpen}
						bind:data
						bind:selected_question
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
					<c.default bind:data bind:selected_question />
				{/await}
			{:else if type === QuizQuestionType.TEXT}
				{#await import('$lib/editor/TextEditorPart.svelte')}
					<Spinner my_20={false} />
				{:then c}
					<c.default bind:data bind:selected_question />
				{/await}
			{:else if type === QuizQuestionType.ORDER}
				{#await import('$lib/editor/OrderEditorPart.svelte')}
					<Spinner my_20={false} />
				{:then c}
					<c.default bind:data bind:selected_question />
				{/await}
			{/if}
		{/if}
	</div>
</div>

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
					bind:checked={data.questions[selected_question]['hide_results']}
				/>
			</label>
			<Button class="w-full" type="button" onclick={() => (advanced_options_open = false)}>
				{$t('words.close')}
			</Button>
		</div>
	</div>
{/if}
