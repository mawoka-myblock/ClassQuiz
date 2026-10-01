<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizQuestionType } from '$lib/quiz_types';
	import type { QuizData } from '$lib/quiz_types';
	import { get_foreground_color } from '$lib/helpers.js';
	import AnswerShape from '$lib/play/kahoot_mode_assets/AnswerShape.svelte';
	import CircularTimer from '$lib/play/circular_progress.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { getLocalization } from '$lib/i18n';
	import { sanitizeTitleHtml } from '$lib/sanitize';

	interface Props {
		quiz_data: QuizData;
		selected_question: number;
		timer_res: string;
		answer_count: number;
		default_colors: string[];
	}

	let {
		quiz_data,
		selected_question,
		timer_res = $bindable(),
		answer_count,
		default_colors
	}: Props = $props();

	const { t } = getLocalization();

	let circular_progress = $derived.by(() => {
		try {
			return (
				1 -
				((100 / parseInt(quiz_data.questions[selected_question].time)) *
					parseInt(timer_res)) /
					100
			);
		} catch {
			return 0;
		}
	});
</script>

<!-- The stage wrapper is what the other three host screens (lobby, per-question
     results, podium) already use. This one was left without it, so its content sat
     flush against the top of the viewport: the title was overlapped by the fixed
     controls bar and the timer rule, and the bottom half of the projector was
     empty. -->
<div class="fq-stage">
	<div class="fq-section">
		<h1 class="fq-display max-w-[22ch] text-center font-bold text-balance">
			{@html sanitizeTitleHtml(quiz_data.questions[selected_question].question)}
		</h1>
		<div class="flex items-center gap-10">
			<CircularTimer text={timer_res} progress={circular_progress} color="#ef4444" />
			<p class="fq-meta text-muted-foreground font-medium tabular-nums" aria-live="polite">
				{$t('admin_page.answers_submitted', { count: answer_count })}
			</p>
		</div>
	</div>
	{#if quiz_data.questions[selected_question].image !== null}
		<div class="flex w-full">
			<MediaComponent
				src={quiz_data.questions[selected_question].image}
				muted={false}
				css_classes="max-h-[20vh] object-cover mx-auto mb-8 w-auto"
			/>
		</div>
	{/if}
	{#if quiz_data.questions[selected_question].type === QuizQuestionType.ABCD || quiz_data.questions[selected_question].type === QuizQuestionType.VOTING || quiz_data.questions[selected_question].type === QuizQuestionType.CHECK}
		<div
			class="mx-auto grid w-full max-w-6xl grid-cols-1 gap-[var(--fq-space-item)] sm:grid-cols-2"
		>
			{#each quiz_data.questions[selected_question].answers as answer, i}
				<div
					class="answer-row relative flex min-h-20 items-center overflow-hidden rounded-2xl transition-all duration-300
					motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-bottom-2"
					style="background-color: {answer.color ??
						default_colors[i]}; animation-delay: {i * 70}ms"
					class:opacity-50={!answer.right &&
						timer_res === '0' &&
						quiz_data.questions[selected_question].type === QuizQuestionType.ABCD}
				>
					<AnswerShape
						index={i}
						class="w-7 h-7 ml-4 shrink-0 self-center"
						style="color: {get_foreground_color(answer.color ?? default_colors[i])}"
					/>
					<span
						class="fq-answer w-full px-3 py-5 text-center font-semibold wrap-anywhere"
						style="color: {get_foreground_color(answer.color ?? default_colors[i])}"
						>{answer.answer}</span
					>
					<span class="pl-4 w-10"></span>
				</div>
			{/each}
		</div>
	{:else if quiz_data.questions[selected_question].type === QuizQuestionType.TEXT}
		{#if timer_res === '0'}
			<div class="grid grid-cols-2 gap-2 w-full p-4">
				{#each quiz_data.questions[selected_question].answers as answer}
					<div class="rounded-2xl h-fit flex border border-neutral-200 bg-white">
						<span class="fq-answer text-center px-2 py-4 w-full text-black"
							>{answer.answer}</span
						>
						<span class="pl-4 w-10"></span>
					</div>
				{/each}
			</div>
		{:else}
			<div class="flex justify-center">
				<p class="fq-meta">{$t('admin_page.enter_answer_into_field')}</p>
			</div>
		{/if}
	{/if}
</div>

