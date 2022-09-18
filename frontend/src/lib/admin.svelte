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

	export let game_token: string;
	export let quiz_data: QuizData;
	export let game_mode;

	const { t } = getLocalization();

	let question_results = null;
	export let final_results: Array<null> | Array<Array<PlayerAnswer>> = [null];
	let selected_question = -1;
	let timer_res: string;
	let shown_question_now: number;
	let final_results_clicked = false;

	console.log(quiz_data);

	export const set_question_number = (q_number: number) => {
		question_results = null;
		socket.emit('set_question_number', q_number.toString());
		shown_question_now = q_number;
		timer_res = quiz_data.questions[q_number].time;
		selected_question += 1;
		timer(timer_res);
	};
	const get_question_results = () => {
		socket.emit('get_question_results', {
			game_id: game_token,
			question_number: shown_question_now
		});
		timer_res = '0';
	};

	const get_final_results = () => {
		socket.emit('get_final_results', {});
		final_results_clicked = true;
	};

	socket.on('final_results', (data) => {
		// data = JSON.parse(data);
		final_results = data;
	});

	socket.on('question_results', (data) => {
		try {
			question_results = JSON.parse(data);
		} catch {
			question_results = undefined;
		}
	});

	const timer = (time: string) => {
		let seconds = Number(time);
		let timer_interval = setInterval(() => {
			if (timer_res === '0') {
				clearInterval(timer_interval);
				return;
			} else {
				seconds--;
			}

			timer_res = seconds.toString();
		}, 1000);
	};
	let circular_prgoress = 0;
	$: {
		try {
			circular_prgoress =
				1 -
				((100 / quiz_data.questions[selected_question].time) * parseInt(timer_res)) / 100;
		} catch {}
	}
</script>

{#if game_mode === 'kahoot'}
	<div class="fixed top-0 w-full h-14 bg-transparent z-20 grid grid-cols-3">
		<p class="mr-auto ml-0 col-start-1 col-end-1">
			{selected_question === -1 ? '0' : selected_question + 1}
			/{quiz_data.questions.length}
		</p>
		{#if selected_question >= 0}
			<div class="flex justify-center flex-col my-auto col-start-2 col-end-2">
				<h2 class="text-center">{quiz_data.questions[selected_question].question}</h2>
				<p class="w-full text-center">{timer_res}</p>
			</div>
		{/if}
		<div class="justify-self-end ml-auto mr-0 col-start-3 col-end-3">
			<button
				on:click={() => {
					set_question_number(selected_question + 1);
				}}
				>Next Question ({selected_question + 2}
				)
			</button>
		</div>
	</div>
	{#if timer_res !== '0' && selected_question >= 0}
		<span
			class="fixed top-0 bg-red-500 h-10 transition-all mt-14"
			style="width: {(100 / quiz_data.questions[selected_question].time) *
				parseInt(timer_res)}vw"
		/>
	{/if}
{/if}
<div class:mt-28={game_mode === 'kahoot'} class="w-full h-full">
	{#if timer_res !== undefined && !final_results_clicked}
		<div class="flex flex-col justify-center w-screen h-1/6">
			<h1 class="text-6xl text-center">
				{quiz_data.questions[selected_question].question}
			</h1>
			<!--			<span class='text-center py-2 text-lg'>{$t('admin_page.time_left')}: {timer_res}</span>-->
			<div class="mx-auto my-2">
				<CircularTimer
					bind:text={timer_res}
					bind:progress={circular_prgoress}
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
		{#if game_mode === 'kahoot'}
			{#if quiz_data.questions[selected_question].type === QuizQuestionType.ABCD}
				<div class="grid grid-cols-2 gap-2 w-full p-4">
					{#each quiz_data.questions[selected_question].answers as answer, i}
						<div
							class="rounded-lg h-fit flex"
							style="background-color: {answer.color ?? '#B45309'}"
						>
							<img class="w-14 inline-block pl-4" alt="icon" src={kahoot_icons[i]} />
							<span class="text-center text-2xl px-2 py-4 w-full"
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
	{#if timer_res === '0'}
		{#if question_results === null}
			{#if game_mode === 'normal'}
				<div class="w-full flex justify-center">
					<button
						on:click={get_question_results}
						id="GetQuestionResults"
						class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
						>{$t('admin_page.get_results')}</button
					>
				</div>
			{/if}
		{:else if question_results === undefined}
			{#if !final_results_clicked}
				<div class="w-full flex justify-center">
					<h1 class="text-3xl">{$t('admin_page.no_answers')}</h1>
				</div>
			{/if}
		{:else}
			<div class="w-full flex justify-center">
				<div class="relative overflow-x-auto shadow-md rounded-lg">
					<table class="w-fit text-sm text-left text-gray-500 dark:text-gray-400">
						<thead
							class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400"
						>
							<tr>
								<th scope="col" class="px-6 py-3">
									{$t('words.username')}
								</th>
								<th scope="col" class="px-6 py-3">
									{$t('words.answer')}
								</th>
								<th scope="col" class="px-6 py-3">
									{$t('words.correct')}?
								</th>
							</tr>
						</thead>
						<tbody>
							{#each question_results as result}
								<tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
									<th
										scope="row"
										class="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap"
									>
										{result.username}
									</th>
									<td class="px-6 py-4">
										{result.answer}
									</td>
									<td class="px-6 py-4">
										{#if result.right}
											✅
										{:else}
											❌
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		{/if}
	{:else if timer_res !== undefined}
		{#if game_mode === 'normal'}
			<div class="w-full flex justify-center">
				<button
					on:click={get_question_results}
					id="GetQuestionResultsAndStopTime"
					class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
					>{$t('admin_page.get_results_and_stop_time')}</button
				>
			</div>
		{/if}
	{/if}
	<br />
	{#if get_question_title(selected_question + 1, quiz_data) !== '' && selected_question + 1 !== 0}
		{#if game_mode === 'normal'}
			<div class="w-full flex justify-center">
				<button
					class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
					disabled={!(timer_res === undefined || timer_res === '0')}
					id="SetQuestionNumber"
					on:click={() => {
						set_question_number(selected_question + 1);
					}}
					>{$t('admin_page.show_next_question')}: {get_question_title(
						selected_question + 1,
						quiz_data
					)}</button
				>
			</div>
		{/if}
	{:else if selected_question + 1 === 0}
		{#if game_mode === 'normal'}
			<div class="w-full flex justify-center">
				<button
					on:click={() => {
						set_question_number(0);
					}}
					class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
				>
					{$t('admin_page.start_by_showing_first_question')}
				</button>
			</div>
		{/if}
	{:else if final_results_clicked === false}
		{#if game_mode === 'normal'}
			<div class="w-screen flex justify-center">
				<button
					on:click={get_final_results}
					class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
					>{$t('admin_page.get_final_results')}</button
				>
			</div>
		{/if}
	{/if}
</div>
