<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import DownloadQuiz from '$lib/components/DownloadQuiz.svelte';
	import { getLocalization } from '$lib/i18n';
	import CollapsSection from '$lib/collapsible.svelte';
	import { createTippy } from 'svelte-tippy';
	import ImportedOrNot from '$lib/view_quiz/imported_or_not.svelte';
	import { QuizQuestionType } from '$lib/quiz_types.js';
	import StartGamePopup from '$lib/dashboard/start_game.svelte';
	import { onMount } from 'svelte';
	import Spinner from '$lib/Spinner.svelte';
	import GrayButton from '$lib/components/buttons/gray.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import RatingComponent from '$lib/view_quiz/RatingComponent.svelte';
	import { page } from '$app/stores';
	import ModComponent from './ModComponent.svelte';
	import { get_foreground_color } from '$lib/helpers.ts';

	const default_colors = ['#D6EDC9', '#B07156', '#7F7057', '#4E6E58'];

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'right'
	});

	let start_game = null;
	let download_id: string | null = null;
	const urlparams = $page.url.searchParams;
	const mod_view = Boolean(urlparams.get('mod'));
	const auto_expand = Boolean(urlparams.get('autoExpand'));
	const auto_return = Boolean(urlparams.get('autoReturn'));
	console.log(auto_expand, 'autoexpand');
	const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
		if (key.code === 'Escape') {
			start_game = null;
		}
	};
	onMount(() => {
		document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	});

	const { t } = getLocalization();
	export let data;
	let { quiz, logged_in }: { quiz: QuizData; logged_in: boolean } = data;

	interface Question {
		time: string;
		question: string;
		image?: string;
		answers: Answer[];
	}

	interface Answer {
		right: boolean;
		answer: string;
	}

	interface QuizData {
		id: string;
		public: boolean;
		title: string;
		description: string;
		created_at: string;
		updated_at: string;
		user_id: string;
		imported_from_kahoot?: boolean;
		questions: Question[];
		kahoot_id?: string;
		mod_rating?: number;
	}
</script>

<svelte:head>
	<title>ClassQuiz - View {quiz.title}</title>
</svelte:head>

<div>
	<h1 class="text-4xl text-center">{@html quiz.title}</h1>
	<div class="text-center">
		<p>{@html quiz.description}</p>
	</div>
	<p class="text-center">
		{$t('view_quiz_page.made_by')}
		<a href="/user/{quiz.user_id.id}" class="underline">@{quiz.user_id.username}</a>
	</p>
	{#if quiz.cover_image}
		<div class="flex justify-center align-middle items-center">
			<div class="h-[15vh] m-auto w-auto my-3">
				<img
					class="max-h-full max-w-full block"
					src="/api/v1/storage/download/{quiz.cover_image}"
					alt="Not provided"
				/>
			</div>
		</div>
	{/if}
	<div class="text-center text-sm pt-1 mb-4">
		<ImportedOrNot imported={quiz.imported_from_kahoot} />
	</div>
	<div class="flex justify-center mb-2 flex-row gap-2">
		<RatingComponent bind:quiz />
		{#if mod_view}
			<ModComponent autoReturn={auto_return} quiz_id={quiz.id} />
		{/if}
	</div>
	<div class="flex flex-col justify-center">
		<div class="mx-auto flex flex-col gap-2 justify-center w-fit">
			{#if quiz.imported_from_kahoot && quiz.kahoot_id}
				<div class="w-full">
					<GrayButton
						href="https://create.kahoot.it/details/{quiz.kahoot_id}"
						target="_blank"
					>
						{$t('view_quiz_page.view_on_kahoot')}
					</GrayButton>
				</div>
			{/if}
			{#if logged_in}
				<div class="w-full">
					<GrayButton
						on:click={() => {
							start_game = quiz.id;
						}}
						flex={true}
					>
						<!-- heroicons/legacy-outline/Play -->
						<svg
							class="w-5 h-5"
							aria-hidden="true"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
							<path
								d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
						</svg>
					</GrayButton>
				</div>
			{:else}
				<div use:tippy={{ content: 'You need to be logged in to start a game' }}>
					<div class="w-full">
						<GrayButton disabled={true} flex={true}>
							<!-- heroicons/legacy-outline/Play -->
							<svg
								class="w-5 h-5"
								aria-hidden="true"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
								<path
									d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</GrayButton>
					</div>
				</div>
			{/if}
			<div class="w-full">
				<GrayButton href="/practice?quiz_id={quiz.id}">
					{$t('words.practice')}
				</GrayButton>
			</div>
			<div class="w-full">
				{#if logged_in}
					<GrayButton flex={true} on:click={() => (download_id = quiz.id)}>
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
								d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
							/>
						</svg>
						{$t('words.download')}
					</GrayButton>
				{:else}
					<div use:tippy={{ content: 'You need to be logged in to download a game' }}>
						<GrayButton disabled={true} flex={true}>
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
									d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
								/>
							</svg>
							{$t('words.download')}
						</GrayButton>
					</div>
				{/if}
			</div>
		</div>
		<div class="flex justify-center">
			<a
				href="mailto:report@mawoka.eu?subject=Report quiz {quiz.id}"
				class="text-sm underline"
			>
				{$t('words.report')}
			</a>
		</div>
	</div>

	{#each quiz.questions as question, index_question}
		<div class="px-4 py-1">
			<CollapsSection headerText={question.question} expanded={auto_expand}>
				<div class="grid grid-cols-1 gap-2 rounded-b-lg bg-white dark:bg-gray-700 -mt-1">
					<h3 class="text-3xl m-1 text-center">
						{index_question + 1}: {@html question.question}
					</h3>

					<!--					<label class='m-1 flex flex-row gap-2 w-3/5'>-->

					<!--					</label>-->
					{#if question.image}
						<span>
							<MediaComponent
								css_classes="mx-auto"
								src={question.image}
								muted={true}
							/>
						</span>
					{/if}
					<p
						class="m-1 flex flex-row gap-2 flex-nowrap whitespace-nowrap w-full justify-center"
					>
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
						<span class="text-lg">{question.time}s</span>
					</p>
					{#if question.type === QuizQuestionType.ABCD || question.type === undefined || question.type === QuizQuestionType.CHECK}
						<div class="grid grid-cols-2 gap-4 m-4 p-6">
							{#each question.answers as answer, index_answer}
								<div
									class="p-1 rounded-lg py-4 shadow-xl"
									style="background-color: {answer.color ??
										default_colors[index_answer]}; color: {get_foreground_color(
										answer.color ?? default_colors[index_answer]
									)}"
									class:shadow-blue-500={answer.right &&
										question.type !== QuizQuestionType.VOTING}
									class:shadow-yellow-500={!answer.right &&
										question.type !== QuizQuestionType.VOTING}
								>
									<h4 class="text-center">
										{quiz.questions[index_question].answers[index_answer]
											.answer}
									</h4>
								</div>
							{/each}
						</div>
					{:else if question.type === QuizQuestionType.RANGE}
						<p class="m-1 text-center">
							All numbers between {question.answers.min_correct}
							and {question.answers.max_correct} are correct, where numbers between {question
								.answers.min} and {question.answers.max} can be selected.
						</p>
					{:else if question.type === QuizQuestionType.ORDER}
						<ul class="flex flex-col gap-4 m-4 p-6">
							{#each question.answers as answer}
								<li class="p-1 rounded-lg py-3 dark:bg-gray-500 bg-gray-300">
									<h4 class="text-center">
										{answer.answer}
									</h4>
								</li>
							{/each}
						</ul>
					{:else if question.type === QuizQuestionType.VOTING || question.type === QuizQuestionType.TEXT}
						<div class="grid grid-cols-2 gap-4 m-4 p-6">
							{#each question.answers as answer, index_answer}
								<div class="p-1 rounded-lg py-4 dark:bg-gray-500 bg-gray-300">
									<h4 class="text-center">
										{quiz.questions[index_question].answers[index_answer]
											.answer}
									</h4>
								</div>
							{/each}
						</div>
					{:else if question.type === QuizQuestionType.SLIDE}
						{#await import('$lib/play/admin/slide.svelte')}
							<Spinner my={false} />
						{:then c}
							<div class="max-h-[90%] max-w-[90%]">
								<svelte:component this={c.default} bind:question />
							</div>
						{/await}
					{/if}
				</div>
			</CollapsSection>
		</div>
	{/each}
</div>

{#if start_game !== null}
	<StartGamePopup bind:quiz_id={start_game} />
{/if}

<DownloadQuiz bind:quiz_id={download_id} />
