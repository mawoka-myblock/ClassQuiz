<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	throw new Error(
		'@migration task: Add data prop (https://github.com/sveltejs/kit/discussions/5774#discussioncomment-3292707)'
	);

	import { getLocalization } from '$lib/i18n';
	import CollapsSection from '$lib/collapsible.svelte';
	import { createTippy } from 'svelte-tippy';
	import ImportedOrNot from '$lib/view_quiz/imported_or_not.svelte';
	import { QuizQuestionType } from '$lib/quiz_types.js';

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'right'
	});

	const { t } = getLocalization();
	export let logged_in: boolean;
	export let quiz: QuizData;

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
	}

	const startGame = async (id: string): Promise<void> => {
		let res;
		if (window.confirm('Do you want to enable the captcha for players?')) {
			res = await fetch(`/api/v1/quiz/start/${id}?captcha_enabled=True`, {
				method: 'POST'
			});
		} else {
			res = await fetch(`/api/v1/quiz/start/${id}?captcha_enabled=False`, {
				method: 'POST'
			});
		}
		if (res.status !== 200) {
			throw new Error('Failed to start game');
		}
		const data = await res.json();
		// eslint-disable-next-line no-undef
		plausible('Started Game', { props: { quiz_id: id } });
		window.location.assign(`/admin?token=${data.game_id}&pin=${data.game_pin}&connect=1`);
	};
</script>

<svelte:head>
	<title>ClassQuiz - View {quiz.title}</title>
</svelte:head>

<div>
	<h1 class="text-4xl text-center">{quiz.title}</h1>
	<div class="text-center">
		<p>{quiz.description}</p>
	</div>
	<div class="text-center text-sm pt-1">
		<ImportedOrNot imported={quiz.imported_from_kahoot} />
	</div>

	<div class="flex justify-center m-8">
		{#if logged_in}
			<button
				class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
				on:click={() => {
					startGame(quiz.id);
				}}
			>
				{$t('words.start')}
			</button>
		{:else}
			<button
				class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none cursor-not-allowed opacity-50"
				disabled
				use:tippy={{ content: 'You need to be logged in to start a game' }}
			>
				{$t('words.start')}
			</button>
		{/if}
	</div>
	<div class="flex justify-center">
		<a href="mailto:report@mawoka.eu?subject=Report quiz {quiz.id}" class="text-sm underline">
			{$t('words.report')}
		</a>
	</div>
	{#each quiz.questions as question, index_question}
		<div class="px-4 py-1">
			<CollapsSection headerText={question.question}>
				<div class="grid grid-cols-1 gap-2 rounded-b-lg bg-white dark:bg-gray-700 -mt-1">
					<h3 class="text-3xl m-1 text-center">
						{index_question + 1}: {question.question}
					</h3>

					<!--					<label class='m-1 flex flex-row gap-2 w-3/5'>-->

					<!--					</label>-->
					{#if question.image}
						<span>
							{$t('words.image')}:
							<img class="pl-8" src={question.image} alt="Not provided" />
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
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/></svg
						>
						<span class="text-lg">{question.time}s</span>
					</p>
					{#if question.type === QuizQuestionType.ABCD || question.type === undefined}
						<div class="grid grid-cols-2 gap-4 m-4 p-6">
							{#each question.answers as answer, index_answer}
								<div
									class="p-1 rounded-lg py-4"
									class:bg-green-500={answer.right}
									class:bg-red-500={!answer.right}
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
					{/if}
				</div>
			</CollapsSection>
		</div>
	{/each}
</div>
