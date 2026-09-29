<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	// Practice: a solo run through a quiz, on the same answer tiles as the live game, with
	// no timer and a score at the end (MVP.md D3). Rebuilt from scratch. The old screens
	// were raw SVGs on bg-white in absolute 80vh panels, and every answer loop referenced
	// an `i` that was never declared, so picking an answer threw. They also leaked a
	// timer interval per question and shuffled the quiz object they were bound to.
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible } from '$lib/stores.svelte';
	import { sanitizeTitleHtml } from '$lib/sanitize';
	import { get_foreground_color } from '$lib/helpers.ts';
	import { answerColor } from '$lib/play/answer_colors';
	import { QuizQuestionType, type QuizData, type Question } from '$lib/quiz_types';
	import { isCorrect, isPracticable, isScored } from '$lib/practice/score';
	import AnswerShape from '$lib/play/kahoot_mode_assets/AnswerShape.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Check from '@lucide/svelte/icons/check';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import Play from '@lucide/svelte/icons/play';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import X from '@lucide/svelte/icons/x';

	const { t } = getLocalization();
	navbarVisible.visible = true;

	const quiz_id = page.url.searchParams.get('quiz_id');
	const back_href = quiz_id ? `/view/${quiz_id}` : '/explore';

	let quiz: QuizData | null = $state(null);
	let load_failed = $state(false);

	onMount(async () => {
		try {
			const res = await fetch(`/api/v1/quiz/get/public/${quiz_id}`);
			if (!res.ok) throw new Error(String(res.status));
			quiz = await res.json();
		} catch {
			load_failed = true;
		}
	});

	type Phase = 'intro' | 'question' | 'done';
	let phase: Phase = $state('intro');
	let index = $state(0);
	let picked: boolean[] = $state([]);
	let revealed = $state(false);
	let score = $state(0);
	let scored_count = $state(0);

	const questions: Question[] = $derived(quiz?.questions ?? []);
	const question: Question | undefined = $derived(questions[index]);
	const is_check = $derived(question?.type === QuizQuestionType.CHECK);
	const tiles = $derived(
		(question?.answers ?? []) as unknown as {
			answer: string;
			right?: boolean;
			color?: string;
		}[]
	);
	const got_it_right = $derived(
		question && revealed && isScored(question) ? isCorrect(question, picked) : null
	);

	const load_question = (i: number) => {
		index = i;
		revealed = false;
		picked = new Array(tiles.length).fill(false);
	};

	const start = () => {
		score = 0;
		scored_count = 0;
		phase = 'question';
		load_question(0);
	};

	const reveal = () => {
		if (revealed || !question) return;
		revealed = true;
		if (isScored(question)) {
			scored_count += 1;
			if (isCorrect(question, picked)) score += 1;
		}
	};

	const choose = (i: number) => {
		if (revealed) return;
		if (is_check) {
			picked[i] = !picked[i];
			return;
		}
		picked = picked.map((_, j) => j === i);
		reveal();
	};

	const next = () => {
		if (index + 1 < questions.length) load_question(index + 1);
		else phase = 'done';
	};
</script>

<svelte:head>
	<title>frogQuiz - {$t('practice_page.title')}</title>
</svelte:head>

<div
	class="mx-auto flex min-h-dvh w-full max-w-2xl flex-col gap-(--fq-space-group) px-4 pt-6 pb-16"
>
	<!-- The way home, on every phase: practice is always something you can walk away from. -->
	<a
		href={back_href}
		class="text-muted-foreground hover:text-foreground fq-touch-target relative inline-flex w-fit items-center gap-1.5 text-sm font-medium transition-colors"
	>
		<ArrowLeft class="size-4" aria-hidden="true" />
		{$t('practice_page.back_to_quiz')}
	</a>

	{#if load_failed}
		<Card.Root>
			<Card.Content class="flex flex-col items-center gap-4 py-10 text-center">
				<p class="text-muted-foreground">{$t('practice_page.not_found')}</p>
				<Button href="/explore" variant="outline">{$t('words.discover')}</Button>
			</Card.Content>
		</Card.Root>
	{:else if !quiz}
		<div class="text-muted-foreground flex justify-center py-16">
			<LoaderCircle class="size-8 animate-spin" aria-label="Loading" />
		</div>
	{:else if phase === 'intro'}
		<Card.Root class="overflow-hidden">
			{#if quiz.cover_image}
				<div class="bg-muted relative aspect-video w-full">
					<MediaComponent
						src={quiz.cover_image}
						css_classes="absolute inset-0 h-full w-full object-cover"
					/>
				</div>
			{/if}
			<Card.Content class="flex flex-col items-center gap-4 py-8 text-center">
				<p class="text-muted-foreground text-sm font-medium">{$t('practice_page.title')}</p>
				<h1 class="text-3xl font-semibold tracking-tight text-balance wrap-anywhere">
					{@html sanitizeTitleHtml(quiz.title)}
				</h1>
				{#if quiz.description}
					<p class="text-muted-foreground max-w-prose">{quiz.description}</p>
				{/if}
				<p class="text-muted-foreground text-sm">
					{$t('practice_page.intro', { count: questions.length })}
				</p>
				<Button size="lg" onclick={start} disabled={questions.length === 0}>
					<Play />
					{$t('practice_page.start')}
				</Button>
			</Card.Content>
		</Card.Root>
	{:else if phase === 'question' && question}
		<div class="flex items-center justify-between gap-3 text-sm">
			<span class="text-muted-foreground font-medium">
				{$t('editor.question_n_of_total', { n: index + 1, total: questions.length })}
			</span>
			{#if scored_count > 0}
				<span class="text-muted-foreground">
					{$t('practice_page.running_score', { score, count: scored_count })}
				</span>
			{/if}
		</div>

		<Card.Root>
			<Card.Content class="flex flex-col gap-5 py-6">
				<h2 class="text-center text-2xl font-semibold text-balance wrap-anywhere">
					{@html sanitizeTitleHtml(question.question)}
				</h2>
				{#if question.image}
					<div class="flex max-h-72 justify-center">
						<MediaComponent
							src={question.image}
							css_classes="h-full max-h-72 w-auto max-w-full rounded-md"
							muted={true}
						/>
					</div>
				{/if}

				{#if !isPracticable(question)}
					<p class="text-muted-foreground text-center">
						{$t('practice_page.unsupported')}
					</p>
				{:else}
					{#if is_check && !revealed}
						<p class="text-muted-foreground text-center text-sm">
							{$t('practice_page.pick_all')}
						</p>
					{/if}
					<ul class="grid w-full gap-3 sm:grid-cols-2">
						{#each tiles as answer, i (i)}
							{@const bg = answer.color ?? answerColor(i)}
							{@const ink = get_foreground_color(bg)}
							{@const show_right = revealed && isScored(question) && answer.right}
							{@const missed =
								revealed && picked[i] && isScored(question) && !answer.right}
							<!-- min-w-0: a grid item won't shrink below its content otherwise. -->
							<li class="min-w-0">
								<button
									type="button"
									class="focus-visible:ring-ring flex min-h-16 w-full min-w-0 items-center gap-3 rounded-xl p-4 text-left transition focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none disabled:cursor-default"
									class:ring-3={show_right || (!revealed && picked[i])}
									class:ring-foreground={show_right || (!revealed && picked[i])}
									class:opacity-40={revealed && !show_right && !picked[i]}
									style="background-color: {bg}; color: {ink}"
									aria-pressed={is_check ? picked[i] : undefined}
									disabled={revealed}
									onclick={() => choose(i)}
								>
									<AnswerShape index={i} class="size-6 shrink-0" />
									<span class="min-w-0 flex-1 text-lg font-medium wrap-anywhere">
										{answer.answer}
									</span>
									{#if show_right}
										<Check class="size-5 shrink-0" aria-hidden="true" />
										<span class="sr-only">{$t('words.correct')}</span>
									{:else if missed}
										<X class="size-5 shrink-0" aria-hidden="true" />
										<span class="sr-only">{$t('practice_page.wrong')}</span>
									{/if}
								</button>
							</li>
						{/each}
					</ul>
				{/if}

				{#if revealed && got_it_right !== null}
					<p
						class="text-center text-lg font-semibold"
						class:text-destructive={!got_it_right}
						role="status"
					>
						{got_it_right ? $t('practice_page.right') : $t('practice_page.not_quite')}
					</p>
				{/if}
			</Card.Content>
		</Card.Root>

		<div class="flex justify-end gap-2">
			{#if is_check && !revealed && isPracticable(question)}
				<Button size="lg" onclick={reveal} disabled={!picked.some(Boolean)}>
					{$t('words.submit')}
				</Button>
			{:else if revealed || !isPracticable(question)}
				<Button size="lg" onclick={next}>
					{index + 1 < questions.length ? $t('words.next') : $t('practice_page.finish')}
				</Button>
			{/if}
		</div>
	{:else if phase === 'done'}
		<Card.Root>
			<Card.Content class="flex flex-col items-center gap-4 py-10 text-center">
				<p class="text-muted-foreground text-sm font-medium">{$t('practice_page.done')}</p>
				{#if scored_count > 0}
					<p class="text-4xl font-semibold tracking-tight">
						{$t('practice_page.final_score', { score, count: scored_count })}
					</p>
				{/if}
				<div class="flex flex-wrap justify-center gap-2">
					<Button onclick={start}>
						<RotateCcw />
						{$t('practice_page.again')}
					</Button>
					<Button href={back_href} variant="outline"
						>{$t('practice_page.back_to_quiz')}</Button
					>
				</div>
			</Card.Content>
		</Card.Root>
	{/if}
</div>
