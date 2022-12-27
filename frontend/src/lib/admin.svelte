<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import { get_question_title } from '$lib/admin.ts';
	import type { PlayerAnswer } from '$lib/admin.ts';
	import { socket } from './socket';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { kahoot_icons } from './play/kahoot_mode_assets/kahoot_icons';
	import CircularTimer from '$lib/play/circular_progress.svelte';
	import Spinner from '$lib/Spinner.svelte';

	export let game_token: string;
	export let quiz_data: QuizData;
	export let game_mode;
	export let bg_color;

	const { t } = getLocalization();

	let question_results = null;
	export let final_results: Array<null> | Array<Array<PlayerAnswer>> = [null];
	let selected_question = -1;
	let timer_res: string;
	let shown_question_now: number;
	let final_results_clicked = false;
	let timer_interval;
	export let control_visible: boolean;

	export let player_scores;

	export const set_question_number = (q_number: number) => {
		socket.emit('set_question_number', q_number.toString());
	};

	socket.on('set_question_number', () => {
		console.log('set_question_number');
	});
	socket.on('get_question_results', () => {
		console.log('get_question_results');
	});
	socket.on('question_results', (_) => {
		timer_res = '0';
		clearInterval(timer_interval);
	});
	socket.on('set_question_number', (data) => {
		timer_res = '0';
		clearInterval(timer_interval);
		question_results = null;
		shown_question_now = data.question_index;
		timer_res = quiz_data.questions[data.question_index].time;
		selected_question = selected_question + 1;
		timer(timer_res);
	});
	const get_question_results = () => {
		socket.emit('get_question_results', {
			game_id: game_token,
			question_number: shown_question_now
		});
	};
	const show_solutions = () => {
		socket.emit('show_solutions', {});
		timer_res = '0';
	};

	const get_final_results = () => {
		socket.emit('get_final_results', {});
	};

	socket.on('solutions', (_) => {
		timer_res = '0';
		clearInterval(timer_interval);
	});

	socket.on('final_results', (data) => {
		// data = JSON.parse(data);
		final_results_clicked = true;
		timer_res = '0';
		final_results = data;
	});

	socket.on('everyone_answered', (_) => {
		timer_res = '0';
	});

	socket.on('question_results', (data) => {
		try {
			question_results = JSON.parse(data);
			timer_res = '0';
		} catch {
			question_results = undefined;
		}
	});

	const timer = (time: string) => {
		let seconds = Number(time);
		timer_interval = setInterval(() => {
			if (timer_res === '0') {
				clearInterval(timer_interval);
				// socket.emit('show_solutions', {});
				return;
			} else {
				seconds--;
			}

			timer_res = seconds.toString();
		}, 1000);
	};
	let circular_progress = 0;
	$: {
		try {
			circular_progress =
				1 -
				((100 / quiz_data.questions[selected_question].time) * parseInt(timer_res)) / 100;
		} catch {
			circular_progress = 0;
		}
	}
</script>

{#if control_visible}
	<div
		class="fixed top-0 w-full h-10 z-20 grid grid-cols-2"
		style="background: {bg_color ? bg_color : 'transparent'}"
		class:text-black={bg_color}
	>
		<p class="mr-auto ml-0 col-start-1 col-end-1">
			{selected_question === -1 ? '0' : selected_question + 1}
			/{quiz_data.questions.length}
		</p>
		<div class="justify-self-end ml-auto mr-0 col-start-3 col-end-3">
			{#if selected_question + 1 === quiz_data.questions.length && ((timer_res === '0' && question_results !== null) || quiz_data?.questions?.[selected_question]?.type === QuizQuestionType.SLIDE)}
				{#if JSON.stringify(final_results) === JSON.stringify([null])}
					<button on:click={get_final_results} class="admin-button"
						>Get final results
					</button>
				{/if}
			{:else if timer_res === '0' || selected_question === -1}
				{#if (selected_question + 1 !== quiz_data.questions.length && question_results !== null) || selected_question === -1}
					<button
						on:click={() => {
							set_question_number(selected_question + 1);
						}}
						class="admin-button"
						>Next Question ({selected_question + 2})
					</button>
				{/if}
				{#if question_results === null && selected_question !== -1}
					{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
						<button
							on:click={() => {
								set_question_number(selected_question + 1);
							}}
							class="admin-button"
							>Next Question ({selected_question + 2})
						</button>
					{:else}
						<button on:click={get_question_results} class="admin-button"
							>Show results
						</button>
					{/if}
				{/if}
			{:else if selected_question !== -1}
				{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
					<button
						on:click={() => {
							set_question_number(selected_question + 1);
						}}
						class="admin-button"
						>Next Question ({selected_question + 2})
					</button>
				{:else}
					<button on:click={show_solutions} class="admin-button"
						>Stop time and show solutions
					</button>
				{/if}
			{:else}
				<!--				<button
					on:click={() => {
						set_question_number(selected_question + 1);
					}}
					class='admin-button'
				>Next Question ({selected_question + 2}
					)
				</button>-->
			{/if}
		</div>
	</div>
{/if}
{#if timer_res !== '0' && selected_question >= 0}
	<span
		class="fixed top-0 bg-red-500 h-8 transition-all"
		class:mt-10={control_visible}
		style="width: {(100 / quiz_data.questions[selected_question].time) * parseInt(timer_res)}vw"
	/>
{/if}

<div class="w-full h-full" class:pt-28={control_visible} class:pt-12={!control_visible}>
	{#if timer_res !== undefined && !final_results_clicked && !question_results}
		{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
			{#await import('$lib/play/admin/slide.svelte')}
				<Spinner my_20={false} />
			{:then c}
				<svelte:component
					this={c.default}
					bind:question={quiz_data.questions[selected_question]}
				/>
			{/await}
		{:else}
			<div class="flex flex-col justify-center w-screen h-1/6">
				<h1 class="text-6xl text-center">
					{@html quiz_data.questions[selected_question].question}
				</h1>
				<!--			<span class='text-center py-2 text-lg'>{$t('admin_page.time_left')}: {timer_res}</span>-->
				<div class="mx-auto my-2">
					<CircularTimer
						bind:text={timer_res}
						bind:progress={circular_progress}
						color="#ef4444"
					/>
				</div>
			</div>
			{#if quiz_data.questions[selected_question].image !== null}
				<div>
					<img
						src={quiz_data.questions[selected_question].image}
						class="max-h-[20vh] object-cover mx-auto mb-8 w-auto"
						alt="Content for Question"
					/>
				</div>
			{/if}
			{#if quiz_data.questions[selected_question].type === QuizQuestionType.ABCD || quiz_data.questions[selected_question].type === QuizQuestionType.VOTING}
				<div class="grid grid-cols-2 gap-2 w-full p-4">
					{#each quiz_data.questions[selected_question].answers as answer, i}
						<div
							class="rounded-lg h-fit flex"
							style="background-color: {answer.color ?? '#B45309'}"
							class:opacity-50={!answer.right &&
								timer_res === '0' &&
								quiz_data.questions[selected_question].type ===
									QuizQuestionType.ABCD}
						>
							<img class="w-14 inline-block pl-4" alt="icon" src={kahoot_icons[i]} />
							<span class="text-center text-2xl px-2 py-4 w-full text-black"
								>{answer.answer}</span
							>
							<span class="pl-4 w-10" />
						</div>
					{/each}
				</div>
			{/if}
		{/if}
	{/if}
	<br />
	{#if timer_res === '0' && JSON.stringify(final_results) === JSON.stringify( [null] ) && quiz_data.questions[selected_question].type !== QuizQuestionType.SLIDE}
		{#if question_results === null}{:else if question_results === undefined}
			{#if !final_results_clicked}
				<div class="w-full flex justify-center">
					<h1 class="text-3xl">{$t('admin_page.no_answers')}</h1>
				</div>
			{/if}
		{:else if quiz_data.questions[selected_question].type === QuizQuestionType.VOTING}
			{#await import('$lib/play/admin/voting_results.svelte')}
				<Spinner />
			{:then c}
				<svelte:component
					this={c.default}
					bind:data={question_results}
					bind:question={quiz_data.questions[selected_question]}
				/>
			{/await}
		{:else}
			{#await import('$lib/play/admin/results.svelte')}
				<Spinner />
			{:then c}
				<svelte:component
					this={c.default}
					bind:data={player_scores}
					bind:new_data={question_results}
				/>
			{/await}
		{/if}
	{:else if timer_res !== undefined}{/if}
	<br />
	{#if get_question_title(selected_question + 1, quiz_data) !== '' && selected_question + 1 !== 0}{:else if selected_question + 1 === 0}
		<div class="flex flex-col justify-center w-screen h-full">
			<h1 class="text-7xl text-center">{@html quiz_data.title}</h1>
			<p class="text-3xl pt-8 text-center">{@html quiz_data.description}</p>
			{#if quiz_data.cover_image}
				<div class="flex justify-center align-middle items-center">
					<div class="h-[30vh] m-auto w-auto mt-12">
						<img
							class="max-h-full max-w-full  block"
							src={quiz_data.cover_image}
							alt="Not provided"
						/>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
