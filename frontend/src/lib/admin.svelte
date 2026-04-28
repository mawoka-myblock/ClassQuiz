<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import { socket } from './socket';
	import { QuizQuestionType } from '$lib/quiz_types';
	import Spinner from '$lib/Spinner.svelte';
	import Controls from '$lib/play/admin/controls.svelte';
	import Question from '$lib/play/admin/question.svelte';
	import { SocketGameControls } from '$lib/play/admin/socket_game_controls.ts';
	import type { IGameState } from '$lib/play/admin/game_state.ts';

	const { t } = getLocalization();
	const default_colors = ['#D6EDC9', '#B07156', '#7F7057', '#4E6E58'];

	let final_results_clicked = $state(false);
	let timer_interval: NodeJS.Timeout;

	interface Props {
		game_token: string;
		bg_color: string;
		game_state: IGameState;
	}

	let { game_token, bg_color, game_state = $bindable() }: Props = $props();

	socket.on('get_question_results', () => {
		console.log('get_question_results');
	});
	socket.on('set_question_number', (data) => {
		game_state.timer_res = '0';
		game_state.question_results = null;
		game_state.shown_question_now = data.question_index;
		game_state.timer_res = game_state.quiz_data.questions[data.question_index].time;
		game_state.selected_question = game_state.selected_question + 1;
		game_state.answer_count = 0;

		clearInterval(timer_interval);
		timer(game_state.timer_res);
	});

	socket.on('solutions', (_) => {
		game_state.timer_res = '0';
		clearInterval(timer_interval);
	});

	socket.on('final_results', (data) => {
		final_results_clicked = true;
		game_state.timer_res = '0';
		game_state.final_results = data;
	});

	socket.on('everyone_answered', (_) => {
		game_state.timer_res = '0';
	});

	socket.on('question_results', (data) => {
		game_state.question_results = data;
		game_state.timer_res = '0';
	});

	socket.on('player_answer', (_) => {
		game_state.answer_count += 1;
	});

	const timer = (time: string) => {
		let seconds = Number(time);
		timer_interval = setInterval(() => {
			if (game_state.timer_res === '0') {
				clearInterval(timer_interval);
				return;
			} else {
				seconds--;
			}

			game_state.timer_res = seconds.toString();
		}, 1000);
	};

	const socket_game_controls: SocketGameControls = new SocketGameControls(socket);
</script>

{#if game_state.control_visible}
	<Controls {bg_color} {socket_game_controls} {game_token} bind:game_state />
{/if}
{#if game_state.timer_res !== '0' && game_state.selected_question >= 0}
	<span
		class="fixed top-0 bg-red-500 h-8 transition-all"
		class:mt-10={game_state.control_visible}
		style="width: {(100 /
			parseInt(game_state.quiz_data.questions[game_state.selected_question].time)) *
			parseInt(game_state.timer_res)}vw"
	></span>
{/if}

<div
	class="w-full h-full"
	class:pt-28={game_state.control_visible}
	class:pt-12={!game_state.control_visible}
>
	{#if game_state.timer_res !== undefined && !final_results_clicked && !game_state.question_results}
		<!-- Question is shown -->
		{#if game_state.quiz_data.questions[game_state.selected_question].type === QuizQuestionType.SLIDE}
			{#await import('$lib/play/admin/slide.svelte')}
				<Spinner my_20={false} />
			{:then c}
				<c.default
					question={game_state.quiz_data.questions[game_state.selected_question]}
				/>
			{/await}
		{:else}
			<Question
				quiz_data={game_state.quiz_data}
				selected_question={game_state.selected_question}
				timer_res={game_state.timer_res}
				answer_count={game_state.answer_count}
				{default_colors}
			/>
		{/if}
	{/if}
	<br />
	{#if game_state.timer_res === '0' && JSON.stringify(game_state.final_results) === JSON.stringify( [null] ) && game_state.quiz_data.questions[game_state.selected_question].type !== QuizQuestionType.SLIDE && game_state.question_results !== null && game_state.quiz_data.questions[game_state.selected_question]?.hide_results !== true}
		{#if game_state.question_results === undefined}
			{#if !final_results_clicked}
				<div class="w-full flex justify-center">
					<h1 class="text-3xl">{$t('admin_page.no_answers')}</h1>
				</div>
			{/if}
		{:else if game_state.quiz_data.questions[game_state.selected_question].type === QuizQuestionType.VOTING}
			{#await import('$lib/play/admin/voting_results.svelte')}
				<Spinner />
			{:then c}
				<c.default
					data={game_state.question_results}
					question={game_state.quiz_data.questions[game_state.selected_question]}
				/>
			{/await}
		{:else}
			{#await import('$lib/play/admin/results.svelte')}
				<Spinner />
			{:then c}
				<c.default
					bind:data={game_state.player_scores}
					question={game_state.quiz_data.questions[game_state.selected_question]}
					new_data={game_state.question_results}
				/>
			{/await}
		{/if}
	{/if}
	<br />
	{#if game_state.selected_question === -1}
		<div class="flex flex-col justify-center w-screen h-full">
			<h1 class="text-7xl text-center">{@html game_state.quiz_data.title}</h1>
			<p class="text-3xl pt-8 text-center">{@html game_state.quiz_data.description}</p>
			{#if game_state.quiz_data.cover_image}
				<div class="flex justify-center align-middle items-center">
					<div class="h-[30vh] m-auto w-auto mt-12">
						<img
							class="max-h-full max-w-full block"
							src="/api/v1/storage/download/{game_state.quiz_data.cover_image}"
							alt="Not provided"
						/>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
