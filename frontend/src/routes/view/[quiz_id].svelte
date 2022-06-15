<script lang="ts" context="module">
	export async function load({ params, fetch, session }) {
		const { quiz_id } = params;
		const res = await fetch(`/api/v1/quiz/get/public/${quiz_id}`);
		if (res.status === 404) {
			return {
				status: 404
			};
		} else if (res.status === 200) {
			const quiz = await res.json();
			return {
				props: {
					quiz: quiz,
					logged_in: session.authenticated
				}
			};
		} else {
			return {
				status: 500
			};
		}
	}
</script>

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import CollapsSection from '$lib/collapsible.svelte';
	import { createTippy } from 'svelte-tippy';
	import 'tippy.js/animations/perspective-subtle.css';
	import 'tippy.js/dist/tippy.css';

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
		window.location.replace(`/admin?token=${data.game_id}&pin=${data.game_pin}&connect=1`);
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
		{#if quiz.imported_from_kahoot === true}
			<svg
				class="w-6 h-6 inline-block h-8 w-8 align-middle"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
				use:tippy={{ content: 'This quiz is imported from KAHOOT!' }}
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
		{:else if quiz.imported_from_kahoot === false}
			<svg
				class="w-6 h-6 inline-block h-8 w-8 align-middle"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
				use:tippy={{ content: 'This quiz was made by the creator themself!' }}
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
				/>
			</svg>
		{:else}
			<svg
				class="w-6 h-6 inline-block h-8 w-8 align-middle"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
				use:tippy={{ content: 'TThis quiz could be imported, it could be OC.' }}
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
		{/if}
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
				<div class="ml-8 grid grid-cols-1 gap-2 m-2 border border-black border-2">
					<h1 class="text-3xl m-1">{$t('words.question')} {index_question + 1}</h1>

					<!--					<label class='m-1 flex flex-row gap-2 w-3/5'>-->
					<p class="text-black w-full bg-inherit text-black dark:text-gray-200">
						{$t('words.question')}: {question.question}
					</p>
					<!--					</label>-->
					{#if question.image}
						<span>
							{$t('words.image')}:
							<img class="pl-8" src={question.image} alt="Not provided" />
						</span>
					{/if}
					<span class="m-1 flex flex-row gap-2 w-3/5 flex-nowrap whitespace-nowrap">
						{$t('editor.time_in_seconds')}:
						<p>{question.time}</p>
					</span>
					{#each question.answers as answer, index_answer}
						<div
							class="ml-8 grid grid-cols-1 gap-2 m-2 border border-black border-2 m-1"
						>
							<h1 class="text-3xl m-1">{$t('words.answer')} {index_answer + 1}</h1>
							<p class="m-1">
								{$t('words.answer')}: {index_answer + 1}
								{$t('words.question')}: {index_question + 1}
							</p>
							<p>
								{$t('words.answer')}
								: {quiz.questions[index_question].answers[index_answer].answer}
							</p>
							<label
								class="m-1 flex flex-row gap-2 w-2/6 flex-nowrap whitespace-nowrap"
							>
								<input
									type="checkbox"
									bind:checked={answer.right}
									class="text-black w-fit"
									disabled
								/>
								<span class="w-fit">{$t('editor.right_or_true?')}</span>
							</label>
						</div>
					{/each}
				</div>
			</CollapsSection>
		</div>
	{/each}
</div>
